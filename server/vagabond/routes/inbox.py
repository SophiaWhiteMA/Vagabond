import json

from math import ceil

from flask import request, make_response

from vagabond.routes import error, require_signin
from vagabond.__main__ import app, db
from vagabond.crypto import require_signature, signed_request
from vagabond.models import Actor, Activity, Following, FollowedBy, Follow, APObject, APObjectRecipient, Create, APObjectType, Notification, Accept, Reject, Like, Delete, Undo
from vagabond.util import resolve_ap_object

from dateutil.parser import parse as parse_date

import os


'''
    -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        HELPER FUNCTIONS - SIDE EFFECTS
    -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
'''

def handle_inbound_accept_reject(activity, obj):
    '''
        Incoming Accept and Reject activites on Follow objects
        have side effects which are handled here
    '''

    actor = APObject.get_object_from_url(obj['actor']) #actor on local server who is following external actor
    if not isinstance(actor, Actor):
        raise Exception('Remote server tried to accept or reject a Follow request done by an object and not by an actor. Aborting.')

    following = db.session.query(Following).filter(db.and_(
        Following.follower_id == actor.id,
        Following.leader == activity['actor']),
        Following.approved == 0
    ).first()

    follow_activity = db.session.query(Follow).filter(db.and_(
        Follow.external_object_id == obj['object'],
        Follow.internal_actor_id == actor.id
    )).first()

    if following is None or follow_activity is None:
        return error('Follow request not found.', 404)

    if activity['type'] == 'Accept':
        following.approved = True
        db.session.add(following)
    else:
        db.session.delete(following)

    return None


def handle_inbound_follow(activity, obj):
    '''
        Handles the side effects of an incoming Follow activity.
        Returns: Flask response if an error occurs, None otherwise
    '''

    api_url = os.environ['API_URL']

    if obj['id'].find(f'{api_url}/actors/') < 0:
        return error('Invalid actor ID')

    local_actor_name = obj['id'].replace(f'{api_url}/actors/', '').lower()

    leader = db.session.query(Actor).filter(db.func.lower(Actor.username) == local_actor_name).first()

    if leader is None:
        return error('Actor not found', 404)

    follower = resolve_ap_object(activity['actor'])

    follower_shared_inbox = None
    follower_inbox = follower['inbox']

    if 'endpoints' in follower:
        if 'sharedInbox' in follower['endpoints']:
            follower_shared_inbox = follower['endpoints']['sharedInbox']


    accept_activity = Accept()
    accept_activity.set_actor(leader)
    accept_activity.set_object(activity)

    db.session.add(accept_activity)
    db.session.flush()

    message_body = accept_activity.to_dict()
    message_body['object'] = activity

    try:
        signed_request(leader, message_body, url=follower_inbox)
    except:
        return error('An error occurred while processing that follow request.', 400)

    new_followed_by = FollowedBy(leader.id, follower['id'], follower_inbox, follower_shared_inbox)
    db.session.add(new_followed_by)

    follower_username = follower['id']
    if 'preferredUsername' in follower:
        follower_username = follower['preferredUsername']

    db.session.add(Notification(leader, f'{follower_username} has followed you', 'Follow'))

    return None


def handle_tags(base_activity, base_object, activity, obj):
    '''
        base_activity: db model
        base_object: db model
        activity: incoming JSON
        obj: incoming JSON

        Takes the incoming activity (and possibly object) and notifies
        the user if he's been tagged in the activity or object.

        The notification is flushed to the database but not commited
    '''

    def notify(tag):
        if 'name' in tag:
            splits = tag['name'].split('@')
            if len(splits) == 3 and splits[2].lower() == os.environ['DOMAIN'].lower():
                name = splits[1]
                actor = db.session.query(Actor).filter(db.func.lower(name) == db.func.lower(Actor.username)).first()
                if actor is not None:
                    db.session.add(Notification(actor, f'{activity["actor"]} mentioned you', 'Mention'))

    if 'tag' in activity and isinstance(activity['tag'], list):
        for tag in obj['tag']:
            base_activity.add_tag(tag)
            notify(tag)
    
    if base_object is not None and 'tag' in obj and isinstance(obj['tag'], list):
        for tag in obj['tag']:
            base_object.add_tag(tag)
            notify(tag)

    db.session.flush()


'''
    =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        HELPER FUNCTIONS - OTHER
    =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''
def handle_undo(inbound_json, activity, obj):
    print(json.dumps(inbound_json))
    if obj['type'] == 'Follow':

        leader = APObject.get_object_from_url(obj['object'])
        if leader is None or not isinstance(leader, Actor):
            return error('Actor not found.', 404)

        follow_activity = db.session.query(Follow).filter(Follow.external_id == obj['id']).first()
        if follow_activity is None:
            return error('Cannot undo follow activity: follow not found.', 404)

        followed_by = db.session.query(FollowedBy).filter(FollowedBy.follower == inbound_json['actor']).filter(FollowedBy.leader_id == leader.id).first()
        if followed_by is None:
            return error('Cannot undo follow activity: follow not found.', 404)

        db.session.delete(follow_activity)
        db.session.delete(followed_by)
        db.session.commit()

        return make_response('', 200)
        
        

def new_ob_object(inbound_json, activity, obj):
    '''
        activity: dict
            The activity being preformed
        obj: dict
            The object the activity is being done on

        Returns: Flask Response object

        To avoid repetition, this function is used to process
        ALL inbound APObjects to an actor's inbox regardless as
        to the type. Special behavior for certain kinds of incoming
        objects is to be handled on a case-by-case basis.

        The newly created objects are added to the database, flushed, and committed.
    '''

    if obj is None:
        return error('Failed to resolve target object.')

    #Set polymorphic type
    base_activity = None
    base_object = None

    if activity['type'] == 'Create':
        base_activity = Create()
        if obj['type'] == 'Note':
            base_object = APObject()
            base_object.type = APObjectType.NOTE
    elif activity['type'] == 'Like':
        base_activity = Like()
    elif (activity['type'] == 'Accept' or activity['type'] == 'Reject') and obj['type'] == 'Follow':
        if activity['type'] == 'Accept':
            base_activity = Accept()
        if activity['type'] == 'Reject':
            base_activity = Reject()
        err_response = handle_inbound_accept_reject(activity, obj)
        if err_response is not None:
            return err_response
    elif activity['type'] == 'Follow':
        base_activity = Follow()
        err_response = handle_inbound_follow(activity, obj)
        if err_response is not None:
            return err_response
    elif activity['type'] == 'Delete':

        base_activity = Delete()
        deleted_object_external_id = None

        if isinstance(inbound_json['object'], dict):
            deleted_object_external_id = inbound_json['object']['id']
        else:
            deleted_object_external_id = inbound_json['object']

        deleted_object = db.session.query(APObject).filter(APObject.external_id == deleted_object_external_id).first()
        if deleted_object is not None:
            deleted_object.content = 'Message erased'

        else:
            return error('Cannot delete object: object not found', 404)

    elif activity['type'] == 'Undo':
        return handle_undo(inbound_json, activity, obj)

    else:
        return error('Invalid request. That activity type may not supported by Vagabond.', 400)
          
        

    # flsuh to db to generate ID needed for assigning generic attributes
    db.session.add(base_activity)
    db.session.flush()

    #set object
    if base_object is not None:
        base_activity.set_object(base_object)

    #set the actor and external id
    base_activity.external_id = activity['id']
    base_activity.external_actor_id = activity['actor']

    #published
    if 'published' in activity:
        base_activity.published = parse_date(activity['published'])
    
    #inReplyTo
    if base_object is not None and 'inReplyTo' in obj:
        base_object.set_in_reply_to(obj['inReplyTo'])

    # recipients
    base_activity.add_all_recipients(activity)

    #set the boject that the activity is acting upon
    base_activity.external_object_id = obj['id']

    # Parse incoming tags
    handle_tags(base_activity, base_object, activity, obj)

    # Assign common properties to the generic object
    if base_object is not None:
        db.session.add(base_object)
        db.session.flush()
        base_object.external_id = obj['id']
        if 'published' in obj:
            base_object.published = parse_date(obj['published'])
        base_object.attribute_to(obj['attributedTo'])
        base_object.add_all_recipients(obj)
        if 'content' in obj:
            base_object.content = obj['content']
        base_activity.object = base_object

    db.session.commit()

    return make_response('', 200)



@require_signin
def get_inbox(personalized, user=None):

    '''
        if personalized == True:
            the route is /api/v1/actors/<actor_name>/inbox
        if personalized == False:
            the route is /api/v1/inbox

        This is not an arbitrary distinction and the AP spec dictates
        the difference in behavior between the two.
    '''

    actor = user.primary_actor

    api_url = os.environ['API_URL']

    # Figure out who the actor is following and put that into a list
    # Do another query for all isntances of APObjectRecipient where the recipiet is contained inside he previously generated list

    leaders = db.session.query(Following).filter(Following.follower_id == actor.id).all()
    followers_urls = []
    for leader in leaders:
        followers_urls.append(leader.followers_collection)

    total_items = db.session.query(APObjectRecipient.ap_object_id.distinct()).filter(APObjectRecipient.recipient.in_(followers_urls)).count()
    max_id_object = db.session.query(APObjectRecipient.ap_object_id.distinct()).filter(APObjectRecipient.recipient.in_(followers_urls)).order_by(APObjectRecipient.ap_object_id.desc()).first()
    
    max_id = 0
    if max_id_object is not None:
        max_id = max_id_object[0]

    items_per_page = 20
    max_page = ceil(total_items / items_per_page)

    root_url = None
    if personalized:
        root_url = f'{api_url}/actors/{actor.username}/inbox'
    else:
        root_url = f'{api_url}/inbox'

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{root_url}',
        'type': 'OrderedCollection',
        'totalItems': total_items,
        'first': f'{root_url}/1?maxId={max_id}',
        'last': f'{root_url}/{max_page}?maxId={max_id}'
    }

    response = make_response(output)
    response.headers['content-type'] = 'application/activity+json'
    return response



def get_inbox_paginated(actor, page, personalized):

    leaders = db.session.query(Following).filter(Following.follower_id == actor.id).all()
    followers_urls = []
    for leader in leaders:
        followers_urls.append(leader.followers_collection)

    base_query = db.session.query(APObjectRecipient).filter(APObjectRecipient.recipient.in_(followers_urls))


    if 'maxId' in request.args:
        base_query = base_query.filter(APObjectRecipient.ap_object_id <= int(request.args['maxId']))

    base_query = base_query.order_by(db.desc(APObjectRecipient.id)).paginate(page, 20)

    recipient_objects = base_query.items

    ordered_items = []

    for recipient_object in recipient_objects:
        appended = recipient_object.ap_object.to_dict()
        if 'object' in appended and isinstance(appended['object'], str):
            queried_item = db.session.query(APObject).filter(APObject.external_id == appended['object']).first()
            if queried_item is not None:
                appended['object'] = queried_item.to_dict()

        ordered_items.append(appended)

    api_url = os.environ['API_URL']

    root_url = None
    if personalized:
        root_url = f'{api_url}/actors/{actor.username}/inbox'
    else:
        root_url = f'{api_url}/inbox'

    prev = f'{root_url}/{page-1}'
    _next = f'{root_url}/{page+1}'

    if 'maxId' in request.args:
        max_id = int(request.args['maxId'])
        prev = prev + f'?maxId={max_id}'
        _next = _next + f'?maxId={max_id}'

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{root_url}/{page}',
        'partOf': f'{root_url}',
        'type': 'OrderedCollectionPage',
        'prev': prev,
        'next': _next,
        'orderedItems': ordered_items
    }

    response = make_response(output)
    response.headers['content-type'] = 'application/activity+json'
    return response


@require_signin
def get_actor_inbox(actor_name, user=None):

    actor_name = actor_name.lower()

    has_permission = False
    for _actor in user.actors:
        if _actor.username.lower() == actor_name:
            has_permission = True
            break

    if has_permission:
        return get_inbox(personalized=True)
    else:
        #TODO: Non-watseful way of figuring out which notes go to who
        return error('You can only view your own inbox, not someone else\'s!')

'''
    =-=-=-=-=-=-=-=-=-=-=-=-
            ROUTES
    =-=-=-=-=-=-=-=-=-=-=-=-
'''

@require_signature
@app.route('/api/v1/actors/<actor_name>/inbox', methods=['GET', 'POST'])
def route_actor_inbox(actor_name):
    
    if request.method == 'POST':
        activity = request.get_json()
        recipient = db.session.query(Actor).filter_by(username=actor_name.lower()).first()

        if recipient is None:
            return error('The specified actor could not be found.', 404)

        obj = resolve_ap_object(request.get_json().get('object'))

        return new_ob_object(request.get_json(), activity, obj)

    elif request.method == 'GET':
        return get_actor_inbox(actor_name=actor_name)


@app.route('/api/v1/actors/<actor_name>/inbox/<int:page>')
@require_signin
def route_actor_inbox_paginated(user, actor_name, page):

    has_permission = False
    actor = None
    for _actor in user.actors:
        if _actor.username.lower() == actor_name.lower():
            has_permission = True
            actor = _actor
            break

    if not has_permission:
        return error('You can only view your own inbox, not someone else\'s!')

    return get_inbox_paginated(actor, page, personalized=True)


@app.route('/api/v1/inbox', methods=['GET', 'POST'])
def route_shared_inbox():
    if request.method == 'GET':
        return get_inbox(personalized=False)
    elif request.method == 'POST':
        activity = request.get_json()
        obj = resolve_ap_object(activity['object'])

        return new_ob_object(request.get_json(), activity, obj)


@app.route('/api/v1/inbox/<int:page>')
@require_signin
def route_shared_inbox_paginated(user, page):

    if request.method == 'GET':
        actor = user.primary_actor
        return get_inbox_paginated(actor, page, personalized=False)
