from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

from base64 import b64encode

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15


import requests
import json
import os

def get_http_datetime():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)



def generate_signing_string(actor, host, request_target, method, body, date, content_type):
    method = method.lower()
    digest = b64encode(SHA256.new(bytes(body, 'utf-8')).digest()).decode('utf-8')
    # Single line used to make sure UNIX v.s. NT line endings don't cause any problems.
    return f'(request-target): {method} {request_target}\nhost: {host}\ndate: {date}\ndigest: SHA-256={digest}\ncontent-type: {content_type}'



def signed_request(actor, body, url=None, host=None, request_target=None, method='POST', content_type='application/activity+json'):
    '''
        Makes a signed POST request according to the HTTPS signatures specification.
        
        actor: Actor model
            actor who is making the signed request

        body: dict
            HTTP message body

        url: str
            URL of the request

        host: str
            Domain of server the signed request is being sent to.
            Auto populated if 'url' param is provided.

        request_target: str
            The target resource on the remote server the signed request is being sent to.
            Auto populated if 'url' param is provided.

        method: str
            HTTP request method of signed request. Currently only supports POST

        content-type: str
            Content type of data being sent. Defaults to 'application/activity+json'
    '''

    if url is None:
        if host is not None and request_target is not None:
            url = 'https://' + host + request_target
        else:
            raise Exception('Must provide either a URL or a remote host and request target when generating a signed request.')

    #TODO: Better error checking and more descriptive error message
    if request_target is None or host is None:
        if url is None:
            raise Exception('Error')
        splits = url.lstrip('http://').lstrip('https://').partition('/')
        host = splits[0]
        request_target = '/' + splits[2].partition('?')[0]



    if method != 'POST':
        raise Exception(f'Only valid HTTP method for signed_request function is POST. \'{method}\' provided.')

    date = get_http_datetime()

    if type(body) is dict:
        body = json.dumps(body)

    signing_string = generate_signing_string(actor, host, request_target, method, body, date, content_type)

    private_key = RSA.importKey(os.environ['PRIVATE_KEY'])
    pkcs = pkcs1_15.new(private_key)
    
    sha256_body = SHA256.new(bytes(body, 'utf-8'))
    digest_body = sha256_body.digest()
    b64_digest_body = b64encode(digest_body).decode('utf-8')


    sha256_signing_string = SHA256.new(bytes(signing_string, 'utf-8'))
    b64_sha256_signing_string = b64encode(pkcs.sign(sha256_signing_string)).decode('utf-8')

    api_url = os.environ['API_URL']

    headers = {
        'user-agent': 'Vagabond',
        'date': date,
        'digest': f'SHA-256={b64_digest_body}',
        'content-type': content_type,
        'signature': f'keyId="{api_url}/actors/{actor.username}#main-key",algorithm="rsa-sha256",headers="(request-target) host date digest content-type",signature="{b64_sha256_signing_string}"'
    }

    response = requests.post(url=url, headers=headers, data=body)

    if response.status_code >= 400:
        print(response.text)
        raise Exception('Signed request error')

    return response

