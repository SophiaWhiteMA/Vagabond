'''
    Handles all of Vagabond's routing and
    exports numerous decorators useful for routing. 
'''

import requests

from flask import make_response, request, session, jsonify

from cerberus import Validator

from vagabond.__main__ import app, db
from vagabond.models import User, Actor, Notification, Follow, Following
from vagabond.util import resolve_ap_object


from uuid import uuid4

import os

'''
@app.before_request
def log_request():
    app.logger.error("Request Path %s", request.path)
    app.logger.error("Request Headers %s", request.headers)
    app.logger.error("Request Body %s", request.data)
    return None
'''


def error(message, code=400):
    '''
        Standard error function used to
        give the client a consistent error
        format. Should be used whenever an error
        is intentionally returned by the server. 
    '''
    return make_response(message, code)



def validate(schema):
    '''
        Decorator.

        Validates JSON POST data according to
        the python-cerbeus schema provided
        as an argument. If the data does not
        match the schema or no POST data is
        provided, a 400 BAD REQUEST error is
        thrown.
    '''
    def decorator(f):
        def wrapper(*args, **kwargs):
            if not request.get_json():
                return error('No JSON data provided. Invalid request', 400)

            result = Validator(schema).validate(request.get_json())
            if not result:
                return error('Invalid request', 400)

            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator



def require_signin(f):
    '''
        Decorator.

        Requires that the incoming request's
        associated session has the 'uid' variable set
        to a valid user ID. An associated instance of the
        vagabond.models.User model is then provided to
        the subsequent function as a key word argument. 

    '''
    def wrapper(*args, **kwargs):
        
        if 'uid' not in session:
            return error('You must be signed in to perform this operation.')
        else:
            user = db.session.query(User).get(session['uid'])
            if not user:
                return error('Invalid session.')
            return f(user=user, *args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper



@app.errorhandler(404)
def route_error_404(e):
    return app.send_static_file('index.html')



# Serves the react app
@app.route('/')
def route_index():
    return app.send_static_file('index.html')



@app.route('/.well-known/webfinger')
def route_webfinger():
    resource = request.args.get('resource')
    if not resource:
        return error('Invalid request')

    splits = resource.split(':')

    if len(splits) != 2 or splits[0].lower() != 'acct':
        return error('Invalid resource parameter')

    splits = splits[1].split('@')
    if len(splits) != 2:
        return error('Invalid request')

    username = splits[0].lower()
    hostname = splits[1]

    actor = db.session.query(Actor).filter_by(username=username).first()
    if not actor:
        return error('User not found', 404)

    output = {
        'subject': resource,
        'links': [
            {
                'rel': 'self',
                'type': 'application/activity+json',
                'href': f'{os.environ["API_URL"]}/actors/{actor.username}'
            },
            {
                'rel': 'http://webfinger.net/rel/profile-page',
                'type': 'text/html',
                'href': f'https://{os.environ["DOMAIN"]}/actors/{actor.username}'
            }
        ]
    }

    return make_response(output, 200)



@app.route('/api/v1/proxy')
def webfinger_federated():
    '''
        Used for looking actors on other servers
        via their WebFinger interface.
    '''


    if 'type' not in request.args:
        return error('Invalid request')

    #webfinger proxy
    if request.args['type'] == 'webfinger':
        username = request.args.get('username')
        hostname = request.args.get('hostname')
        if not username or not hostname:
            return error('Invalid request')

        try:
            response = requests.get(f'https://{hostname}/.well-known/webfinger?resource=acct:{username}@{hostname}')
            if response.status_code == 404:
                return error('User not found.', 404)
            return make_response(response.json(), 200)
        except Exception as e:
            return error('An error occurred while attempting to look up the specified user.')
    
    #Actor proxy
    elif request.args['type'] == 'actor':
        username = request.args.get('username')
        hostname = request.args.get('hostname')
        try:
            response = requests.get(f'https://{hostname}/.well-known/webfinger?resource=acct:{username}@{hostname}')
            if response.status_code >= 300:
                return error(response.text, response.status_code)

            if 'links' in response.json() and isinstance(response.json()['links'], list):
                for link in response.json()['links']:
                    if 'rel' in link and link['rel'] == 'self':
                        actor_data = resolve_ap_object(link['href'])
                        return make_response(actor_data, 200)
                return error(f'Invalid WebFinger response for actor @{username}@{hostname}: no "self" link. ')
            elif 'href' in response.json():
                actor_data = resolve_ap_object(response.json()['href'])
                return make_response(actor_data, 200)
            else:

                return error(f'Failed to look up actor @{username}@{hostname}: server sent invalid response.')


        except Exception as e:
            print(e)
            return error('An error occurred while attempting to look up the specified actor.')



    
    
@app.route('/api/v1/notifications', methods=['GET', 'POST'])
@require_signin
def route_notifications(user):
    actor = user.primary_actor
    if request.method == 'GET':
        notifications = db.session.query(Notification).filter(Notification.actor_id == actor.id).all()
        output = []
        for notification in notifications:
            output.append(notification.to_dict())
        return make_response(jsonify(output))
    elif request.method == 'POST':
        request_data = request.get_json()
        if request_data['action'] == 'delete':
            notification = db.session.query(Notification).get(int(request_data['id']))
            if notification is not None:
                if notification.actor_id != actor.id:
                    return make_response('You can\'t delete someone else\'s notifications!', 400)
                else:
                    db.session.delete(notification)
                    db.session.commit()
                    return make_response('', 200)
        elif request_data['action'] == 'delete_all':
            notifications = db.session.query(Notification).filter(Notification.actor_id == actor.id).delete()
            db.session.commit()
            return make_response('', 200)

@app.route('/api/v1/unfollow', methods=['POST'])
@require_signin
def route_undo_follow(user):

    from vagabond.crypto import signed_request

    follower = user.primary_actor
    leader = resolve_ap_object(request.get_json()['leader'])

    follow_activity = db.session.query(Follow).filter(Follow.internal_actor_id == follower.id, Follow.external_object_id == leader['id']).first()
    if follow_activity is None:
        print('@@@@@@@@@@@@@@@@@@@@@@@')
        return error('It doesn''t appear that you follow that user :thonking:', 404)

    following = db.session.query(Following).filter(Following.leader == leader['id']).filter(Following.follower_id == follower.id).first()
    if following is None:
        return error('It doesn''t appear that you follow that user :thonking:', 404)

    api_url = os.environ['API_URL']
    uuid = uuid4()

    signed_request(follower, {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'type': 'Undo',
        'id': f'{api_url}/unfollowActivity/{uuid}',
        'actor': follower.to_dict()['id'],
        'object': {
            'type': 'Follow',
            'actor': follower.to_dict()['id'],
            'object': leader['id'],
            'id': follow_activity.to_dict()['id']
        }
    }, leader['inbox'])

    db.session.delete(follow_activity)
    db.session.delete(following)
    db.session.commit()

    return make_response('', 200)