'''
    Routes pertaining to user authentication
    and session management.
'''
from flask import make_response, request, session

import bcrypt

from vagabond.__main__ import app, db
from vagabond.models import User, Actor
from vagabond.routes import error, validate, require_signin
from vagabond.regex import ACTOR_NAME, USERNAME, PASSWORD

import os

def get_session_data(user):
    api_url = os.environ['API_URL']
        
    output = {
        'actors': [],
        'signedIn': True
    }

    for actor in user.actors:
        following = []

        appended = {
            'id': f'{api_url}/actors/{actor.username}',
            'username': actor.username,
            'preferredUsername': actor.username,
            'following': following
        }

        output['actors'].append(appended)

        if user.primary_actor_id == actor.id:
            output['currentActor'] = appended



    return output





schema_signup = {
    'username': {
        'type': 'string',
        'required': True,
        'regex': USERNAME
    },
    'password': {
        'type': 'string',
        'required': True,
        'regex': PASSWORD
    },
    'passwordConfirm': {
        'type': 'string',
        'required': True,
        'regex': PASSWORD
    },
    'actorName': {
        'type': 'string',
        'required': True,
        'regex': ACTOR_NAME
    }
}



@app.route('/api/v1/signup', methods=['POST'])
@validate(schema_signup)
def route_signup():
    username = request.get_json().get('username').lower()
    password = request.get_json().get('password')
    password_confirm = request.get_json().get('passwordConfirm')
    actor_name = request.get_json().get('actorName')

    existing_user = db.session.query(User).filter(db.func.lower(User.username) == db.func.lower(username)).first()
    if existing_user is not None:
        return error('That username is not available.', 400)

    existing_actor = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(actor_name)).first()
    if existing_actor is not None:
        return error('That actor name is not available.', 400)

    if password != password_confirm:
        return error('Passwords don\'t match.', 400)

    new_user = User(username, password)
    db.session.add(new_user)
    db.session.flush()

    new_actor = Actor(actor_name, user_id=new_user.id)
    db.session.add(new_actor)
    db.session.flush()

    new_user.primary_actor_id = new_actor.id

    db.session.commit()


    session['uid'] = new_user.id

    return make_response(get_session_data(new_user), 201)





schema_signin = {
    'username': {
        'type': 'string',
        'required': True,
        'regex': USERNAME
    },
    'password': {
        'type': 'string',
        'required': True,
        'regex': PASSWORD
    }
}



@app.route('/api/v1/signin', methods=['POST'])
@validate(schema_signin)
def route_signin():
    username = request.get_json().get('username')
    password = request.get_json().get('password')

    if 'uid' in session:
        return error('You are currently signed in. Please sign out before trying to sign in.')

    err_msg = 'Invalid username or password.'

    user = db.session.query(User).filter(db.func.lower(User.username) == db.func.lower(username)).first()

    if user is None:
        return error(err_msg)
    
    if not bcrypt.checkpw(bytes(password, 'utf-8'), bytes(user.password_hash, 'utf-8')):
        return error(err_msg)

    session['uid'] = user.id

    return make_response(get_session_data(user), 200)





@app.route('/api/v1/signout', methods=['POST'])
@require_signin
def route_signout(user):
    session.clear()
    return make_response('', 200)





@app.route('/api/v1/session')
@require_signin
def route_session(user):
    return make_response(get_session_data(user), 200)
