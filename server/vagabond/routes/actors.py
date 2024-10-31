from math import ceil

from flask import make_response, request

from vagabond.__main__ import app, db
from vagabond.models import Actor, User, Following, FollowedBy, Like
from vagabond.routes import require_signin
from vagabond.crypto import require_signature
from vagabond.routes import error

import os



@app.route('/api/v1/actors/<username>')
def route_get_actor_by_username(username):
    '''
        Returns: ActivityPub actor object
    '''
    actor = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(username)).first()
    if actor is None:
        return error('Actor not found', 404)
    response =  make_response(actor.to_dict(), 200)
    response.headers['Content-Type'] = 'application/activity+json'
    return response
    


@app.route('/api/v1/actors/<username>/following')
def route_get_actor_following(username):
    '''
       Publicly accessible following collection. 
    '''

    actor = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(username)).first()
    if actor is None:
        return error('Actor not found', 404)

    items_per_page = 20
    total_items = db.session.query(Following).filter(db.and_(Following.follower_id == actor.id, Following.approved == 1)).count()
    last_page = ceil(total_items / items_per_page)

    return make_response({
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{os.environ["API_URL"]}/actors/{actor.username}/following',
        'type': 'OrderedCollection',
        'totalItems': total_items,
        'first': f'{os.environ["API_URL"]}/actors/{actor.username}/following/1',
        'last': f'{os.environ["API_URL"]}/actors/{actor.username}/following/{last_page}'
    }, 200)



@app.route('/api/v1/actors/<username>/following/<int:page>')
def route_get_actor_following_page(username, page):
    actor = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(username)).first()
    if actor is None:
        return error('Actor not found', 404)

    items = db.session.query(Following).filter(db.and_(Following.follower_id == actor.id, Following.approved == 1)).paginate(page, 20).items


    ordered_items = []

    for item in items:
        ordered_items.append(item.leader)

    api_url = os.environ['API_URL']

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{api_url}/actors/{actor.username}/following/{page}',
        'type': 'OrderedCollectionPage',
        'partOf': f'{api_url}/actors/{actor.username}/following',
        'next': f'{api_url}/actors/{actor.username}/following/{page+1}',
        'orderedItems': ordered_items
    }

    if page > 1:
        output['prev'] = f'{api_url}/actors/{actor.username}/following/{page-1}'

    return make_response(output, 200)






@app.route('/api/v1/actors/<username>/followers')
def route_get_actor_followers(username):
    '''
       Publicly accessible followers collection. 
    '''

    actor = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(username)).first()
    if actor is None:
        return error('Actor not found', 404)

    items_per_page = 20
    total_items = db.session.query(FollowedBy).filter(FollowedBy.leader_id == actor.id).count()
    last_page = ceil(total_items / items_per_page)

    return make_response({
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{os.environ["API_URL"]}/actors/{actor.username}/followers',
        'type': 'OrderedCollection',
        'totalItems': total_items,
        'first': f'{os.environ["API_URL"]}/actors/{actor.username}/followers/1',
        'last': f'{os.environ["API_URL"]}/actors/{actor.username}/followers/{last_page}'
    }, 200)



@app.route('/api/v1/actors/<username>/followers/<int:page>')
def route_get_actor_followers_page(username, page):
    actor = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(username)).first()
    if actor is None:
        return error('Actor not found', 404)

    items = db.session.query(FollowedBy).filter(db.and_(FollowedBy.leader_id == actor.id)).paginate(page, 20).items


    ordered_items = []

    for item in items:
        ordered_items.append(item.follower)

    api_url = os.environ['API_URL']

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{api_url}/actors/{actor.username}/following/{page}',
        'type': 'OrderedCollectionPage',
        'partOf': f'{api_url}/actors/{actor.username}/following',
        'orderedItems': ordered_items,
        'next': f'{api_url}/actors/{actor.username}/following/{page+1}'
    }

    if(page > 1):
        output['prev'] = f'{api_url}/actors/{actor.username}/following/{page-1}'

    return make_response(output, 200)






@app.route('/api/v1/actors/<actor_name>/liked')
def route_get_liked_collection(actor_name):

    actor = db.session.query(Actor).filter(db.func.lower(actor_name) == db.func.lower(Actor.username)).first()
    if actor is None:
        return error('Actor not found.', 404)
    
    max_id = 0
    max_id_object = db.session.query(Like).filter(Like.internal_actor_id == actor.id).order_by(Like.id.desc()).first()
    if max_id_object is not None:
        max_id = max_id_object.id

    total_items = db.session.query(Like).filter(Like.internal_actor_id == actor.id).count()
    items_per_page = 20

    max_page = ceil(total_items / items_per_page)

    api_url = os.environ['API_URL']

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{api_url}/actors/{actor_name}/liked',
        'type': 'OrderedCollection',
        'totalItems': total_items,
        'first': f'{api_url}/actors/{actor_name}/liked/1?maxId={max_id}',
        'last': f'{api_url}/actors/{actor_name}/liked/{max_page}?maxId={max_id}'
    }

    output = make_response(output, 200)
    output.headers['content-type'] = 'application/activity+json'
    return output


@app.route('/api/v1/actors/<actor_name>/liked/<int:page>')
def route_get_liked_collection_paginated(actor_name, page):

    #actor check
    actor = db.session.query(Actor).filter(db.func.lower(actor_name) == db.func.lower(Actor.username)).first()
    if actor is None:
        return error('Actor not found.', 404)

    # set variables
    items_per_page = 20
    max_id = None
    if 'maxId' in request.args:
        max_id = int(request.args['maxId'])
    total_items = 0

    base_query = db.session.query(Like).filter(Like.internal_actor_id == actor.id).order_by(Like.id.desc())
    total_items = base_query.count()

    if max_id is not None:
        base_query = base_query.filter(Like.id <= max_id)

    api_url = os.environ['API_URL']

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{api_url}/actors/{actor_name}/liked/{page}',
        'type': 'OrderedCollectionPage',
        'partOf': f'{api_url}/actors/{actor.username}/liked',
        'orderedItems': []
    }

    for item in base_query.paginate(page, items_per_page).items:
        output['orderedItems'].append(item.to_dict())

    if max_id is not None:
        output['id'] = output['id'] + f'?maxId={max_id}'

    # previous page
    if page > 1:
        output['prev'] = f'{api_url}/actors/{actor_name}/liked/{page-1}'
        if max_id is not None:
            output['prev'] = output['prev'] + f'?maxId={max_id}'

    # optional next page
    if total_items > items_per_page * page:
        output['next'] = f'{api_url}/actors/{actor_name}/liked/{page}'
        if max_id is not None:
            output['next'] = output['next'] + f'?maxId={max_id}'

    output = make_response(output, 200)
    output.headers['content-type'] = 'application/activity+json'
    return output
    




@app.route('/api/v1/newactor')
@require_signin
def route_add_new_actor(user):
    actor_name = request.get_json().get('actorName')

    existing_actor = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(actor_name)).first()
    if existing_actor is not None:
        return error('That actor name is not available.', 404)
    
    new_actor = Actor(actor_name, user_id=user.id)
    db.session.add(new_actor)
    db.session.flush()

    db.session.commit()

    return make_response('', 201)



@app.route('/api/v1/switchactor')
@require_signin
def route_switch_actor(user):

    actor = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(user.username)).first()
    if actor is None:
        return error('Actor not found', 404)

    if actor.user_id == user.id:
        user.primary_actor_id = actor.id
        db.session.commit()

        return make_response('', 200)
        
    else:
        return error('User does not own actor.', 404) 
    