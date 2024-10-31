from flask import request, make_response

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from base64 import b64decode, b64encode

from vagabond.__main__ import app
from vagabond.util import resolve_ap_object
from vagabond.routes import error

import os

def parse_keypairs(raw_signature):
    '''
        returns: tuple (key_id, algorithm, headers, signature)
        key_id: string
        algorithm: string
        headers: list
        signature: string; base64 encoded signature
    '''
    keypairs = raw_signature.split(',')
    for i in range (0, len(keypairs)): keypairs[i] = keypairs[i].strip()
    key_id = None
    algorithm = None
    headers = None
    signature = None

    for keypair in keypairs:
        keypair = keypair.strip()

        if keypair.find('keyId="') >= 0:
            key_id = keypair.replace('keyId="', '').rstrip('"')

        if keypair.find('algorithm="') >= 0:
            algorithm = keypair.replace('algorithm="', '').rstrip('"')

        elif keypair.find('headers="') >= 0:
            headers = keypair.replace('headers="', '').rstrip('"').split(' ')
            for i in range(0, len(headers)): headers[i] = headers[i].strip()

        elif keypair.find('signature="') >= 0:
            signature = keypair.replace('signature="', '').rstrip('"')
 
        else:
            continue

    return (key_id, algorithm, headers, signature)



def construct_signing_string(headers):
    '''
        Takes a list of headers as present in the HTTP signature header and
        constructs a signing string
    '''
    output = ''
    for i in range(0, len(headers)):
        header = headers[i]
        header = header.strip()
        if header == '(request-target)':
            output += f'(request-target): post {request.path}'
        else:
            output += (header + ': ')
            output += request.headers[header.title()]


        if i != (len(headers) - 1):
            output += '\n'
        
    return output



def get_public_key(key_id):
    '''
        Takes the "keyId" field of a request and
        uses resolve_ap_object-actor to fetch the public key
        of the specified actor.
    '''
    actor = resolve_ap_object(key_id)

    if not actor or not actor.get('publicKey'):
        return error('An error occurred while attempting to fetch the public key of the inbound actor.', 400)

    public_key_wrapper = actor.get('publicKey')

    if public_key_wrapper.get('id') != key_id:
        return error('Keys don\'t match', 400)

    public_key_string = public_key_wrapper.get('publicKeyPem')

    if not public_key_string:
        return error('Public key not found.')

    public_key =  RSA.importKey(bytes(public_key_string, 'utf-8'))

    return public_key



def require_signature(f):
    '''
        Decoator that requires all POST requests have a valid HTTP
        signature according to the RFC standard
    '''
    def wrapper(*args, **kwargs):

        if request.method != 'POST':
            return f(*args, **kwargs)
        
        if not request.get_json():
            return error('No JSON provided.', 400)

        if not request.get_json().get('actor'):
            return error('Invalid request: "actor" field not provided')

        if 'Signature' not in request.headers or 'Digest' not in request.headers:
            return error('Authentication mechanism is missing or invalid. HTTP request must include both Signature and Digest headers.', 400)

        raw_signature = request.headers['Signature']
        (key_id, algorithm, headers, signature) = parse_keypairs(raw_signature)

        if key_id is None or algorithm is None or headers is None or signature is None:
            return error('Authentication mechanism is missing or invalid')

        # We know that the owner of the public key in the header is making the
        # request, but we don't necessarily know they have permission to
        # even send the message unless we verify that it's the same person!
        try:
            if request.get_json().get('actor') != key_id.replace('#main-key', ''):
                return error('Could not verify that the public key matches the URL of the actor')
        except:
            return error('Could not verify that the public key matches the URL of the actor')

        # 'digest' must be present in the list of headers inside of
        # The Signature HTTP header. If it isn't, an attacker can
        # fail to provide the digest and perform actions on behalf
        # of an arbitrary actor.
        if 'digest' not in headers or 'date' not in headers or 'host' not in headers:
            return error('Authentication mechanism is missing or invalid: the "digest", "date", or "host" arguments were not included in the "headers" field of the "Signature" HTTP header')

        # Make sure the message is intended for us:
        if request.headers['Host'] != os.environ['DOMAIN']:
            return error(f'Forged request: this message was originally intended for a recipient other than {os.environ["DOMAIN"]}')

        # The HTTP signatures spec supports more than just SHA-256,
        # But for simplicity's sake we only support the most common
        # type.
        if algorithm != 'rsa-sha256':
            return error('Invalid algorithm: only rsa-sha256 is supported.')

        signing_string = construct_signing_string(headers)

        digest = SHA256.new(bytes(signing_string, 'utf-8'))

        decoded_signature = b64decode(signature)

        public_key = get_public_key(key_id)

        if str(public_key) == 'None':
            return error(f'Could not get public key. Key id: {key_id}', 400)

        try:
            pkcs1_15.new(public_key).verify(digest, decoded_signature)
        except:
            return error('The integrity of the message could not be verified.', 400)

        body_digest = b64encode(SHA256.new(request.get_data()).digest())

        header_digest = bytes(request.headers.get('Digest').replace('SHA-256=', ''), 'utf-8')

        if body_digest != header_digest:
            return error('Body digest does not match header digest')

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper