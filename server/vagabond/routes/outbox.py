'''
    Contains routes and functions for processing
    inbound requests to an actor outbox and for displaying
    the contents of an Actor outbox.
'''

from math import ceil

from flask import make_response, request, session

from dateutil.parser import parse

from vagabond.__main__ import app, db
from vagabond.models import Actor, APObject, APObjectType, Following, Activity, Create, Follow, FollowedBy, Like, Notification, Note, Undo, Delete
from vagabond.routes import error, require_signin
from vagabond.crypto import signed_request
from vagabond.util import resolve_ap_object, xsd_datetime

import datetime
import os
import json

'''
    -=-=-=-=-=-=-=-=-=-=
      HELPER FUNCTIONS
    -=-=-=-=-=-=-=-=-=-=
'''

def deliver(actor, message):
    '''
        Delivers the specified message to the recipients listed in the to, bto, cc, and bcc fields. 
    '''

    api_url = os.environ['API_URL']

    keys = ['to', 'bto', 'cc', 'bcc']
    recipients = []
    for key in keys:
        if key in message:
            if isinstance(message[key], str):
                message[key] = [message[key]]
            for value in message[key]:
                recipients.append(value)

    all_inboxes = []

    for recipient in recipients:
        try:
            # possibility 1: local delivery of some kind. If delivery is to local actor, do nothing. If delivery is to local followers collection, distribute to followers.
            if recipient.replace(f'{api_url}/actors/', '') != recipient:
                splits = recipient.replace(f'{api_url}/actors/', '').split('/')

                if len(splits) == 2 and splits[1] == 'followers':
                    leader = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(splits[0])).first()
                    if leader is None:
                        continue

                    shared_inboxes = db.session.query(FollowedBy.follower_shared_inbox.distinct()).filter(FollowedBy.leader_id == leader.id, FollowedBy.follower_shared_inbox != None).all()
                    for inbox in shared_inboxes:
                        all_inboxes.append(inbox[0])

                    unique_inboxes = db.session.query(FollowedBy.follower_inbox.distinct()).filter(FollowedBy.leader_id == leader.id, FollowedBy.follower_shared_inbox == None).all()
                    for inbox in unique_inboxes:
                        all_inboxes.append(inbox[0])
            
            # possibility 2: external delivery of some kind
            else:

                actor_types = ['Application', 'Group', 'Organization', 'Person', 'Service']

                recipient_object = resolve_ap_object(recipient)

                if recipient_object is None:
                    continue

                if recipient_object['type'] in actor_types:

                    if 'endpoints' in recipient_object and 'sharedInbox' in recipient_object['endpoints'] and recipient_object['endpoints']['sharedInbox'] not in all_inboxes:
                        all_inboxes.append(recipient_object['endpoints']['sharedInbox'])
                    elif 'inbox' in recipient_object:
                        all_inboxes.append(recipient_object['inbox'])  

                elif (recipient_object['type'] == 'OrderedCollection' or recipient_object['type'] == 'Collection'):
                    
                    # We have a page with the items all in one place
                    if 'items' in recipient_object:
                        for item in recipient_object['items']:
                            if isinstance(item, str):
                                if item not in all_inboxes:
                                    all_inboxes.append(item)
                            elif isinstance(item, dict):
                                if 'endpoints' in item and 'sharedInbox' in item['endpoints']:
                                    shared_inbox = item['endpoints']['sharedInbox']
                                    if shared_inbox not in all_inboxes:
                                        all_inboxes.append(shared_inbox)
                                elif 'inbox' in item:
                                    if item['inbox'] not in all_inboxes:
                                        all_inboxes.append(item['inbox'])
                                        
                    # Traditional segmented OrderedCollection
                    else:

                        next_page = resolve_ap_object(recipient_object['first'])
                        iteration = 0

                        while next_page is not None and iteration < 10:

                            for item in next_page['items']:
                                if isinstance(item, str) and item not in all_inboxes:
                                    all_inboxes.append(item)
                                elif isinstance(item, dict) and 'id' in item and 'type' in item and item['type'] in actor_types:
                                    all_inboxes.append(item)

                            iteration = iteration + 1
                            if 'next' in next_page:
                                next_page = resolve_ap_object(next_page['next'])
                            else:
                                next_page = None


                    #TODO: Delivery to external collections

        except Exception as e:
            print(e)
            
    for inbox in all_inboxes:
        # Don't deliver messages to ourselves!
        if inbox.replace(os.environ['API_URL'], '') == inbox:
            try:
                signed_request(actor, message, url=inbox)
            except Exception as e:
                print(e)
                print( f'Could not deliver message to the following inbox: {inbox}')

                app.logger.error(f'Could not deliver message to the following inbox: {inbox}')



def outbox_permission_check(actor_name, user):
    '''
        Checks if the user has permission
        to POST to the URL of the actor's outbox.

        Returns an actor object if the user has permission,
        None otherwise.
    '''
    actor = None
    for _actor in user.actors:
        if _actor.username.lower() == actor_name.lower():
            actor = _actor
            break

    return actor




def get_base_objects(obj):
    '''
        The client is capable of sending a wide array of object types to
        the server. This function parses the input AP Activity+Object pair and
        returns a tuple containing the correct database model(s).

        base_object is either a string or a database model depending on context

        Returns: Flask.response | tuple(base_activity, base_object)
    '''
    base_activity = None
    base_object = None

    err_not_supported = 'Vagabond does not currently support this type of AcvtivityPub object.'

    if obj['type'] == 'Create':
        if obj['object']['type'] == 'Note':
            base_object = Note()
            base_activity = Create()
        else:
            return error(err_not_supported)

    elif obj['type'] == 'Follow':
        base_activity = Follow()
    elif obj['type'] == 'Like':
        base_activity = Like()
    elif obj['type'] == 'Undo':
        base_activity = Undo()
    elif obj['type'] == 'Delete':
        base_activity = Delete()
    else:
        return error(err_not_supported)

    if base_object is None:
        if(isinstance(obj['object'], str)):
            base_object = obj['object']
        elif(isinstance(obj['object'], dict)):
            base_object = obj['object']['id']
        else:
            raise Exception('Invalid Activity: object field was neither an object nor a string.')

    db.session.add(base_activity)
    if isinstance(base_object, db.Model):
        db.session.add(base_object)
    db.session.flush()

    return (base_activity, base_object)



def wrap_raw_object(obj):
    '''
        The ActivityPub specificiation allows the client to send raw objects to the
        server without being wrapped by an activity. When this happens, the server
        understands this to be shorthand for a Create activity on the incoming object.

        Function currently only works with Note objects, though other types are
        supported by the specification.
    '''

    if obj['type'] != 'Note':
        return obj
    else:
        output = {
            'type': 'Create',
            'object': obj
        }
        copy_keys = ['to', 'bto', 'cc', 'bcc', 'published', 'context']
        for key in copy_keys:
            if key in obj:
                output[key] = obj[key]

        return output



def determine_if_local(activity):
    '''
        Returns true if the Activity sent by the client is acting on an object
        that originated on this server. Used mainly for the special
        handling of the Follow activity. Returns false otherwise.
    '''
    api_url = os.environ['API_URL']
    output = False
    if 'object' in activity:
        if isinstance(activity['object'], dict) and 'id' in activity['object']:
            _id = activity['object']['id']
            if _id.replace(api_url, '') != _id:
                output = True
        elif isinstance(activity['object'], str):
            _id = activity['object']
            if _id.replace(api_url, '') != _id:
                output = True

    return output

def handle_follow(inbound_json, actor, base_activity, base_object, is_local):
    '''
        Handles the various oddities associated with the correspondance nature of the Follow activity.
    '''
    leader = resolve_ap_object(inbound_json['object'])

    existing_follow = db.session.query(Following).filter(db.and_(
        Following.follower_id == actor.id,
        Following.leader == leader['id']
    )).first()

    if existing_follow is not None and existing_follow.approved is True:
        return error('You are already following this actor.')

    new_follow = Following(
        actor.id, leader['id'], leader['followers'], approved=is_local)
    db.session.add(new_follow)

        # Due to the correspondance nature of the Follow activity, it has some very unusual requirements.
        # We need to detect if the incoming Follow activity is targeting a local user. If it is, we don't need
        # To deliver server-to-server messages about this transaction. Attempting to do so would cause problems
        # resulting from uncomitted database transactions and be a waste of resources.
    if is_local:
        local_leader = db.session.query(Actor).filter(db.func.lower(Actor.username) == db.func.lower(
            inbound_json['object'].replace(f'{os.environ["API_URL"]}/actors/', ''))).first()
        if local_leader is None:
            return make_response('Actor not found', 404)
        actor_dict = actor.to_dict()
        new_followed_by = FollowedBy(
            local_leader.id, actor_dict['id'], actor_dict['inbox'], follower_shared_inbox=actor_dict['endpoints']['sharedInbox'], approved=True)
        db.session.add(Notification(
            local_leader, f'{actor_dict["preferredUsername"]} has followed you.', 'Follow'))
        db.session.add(new_followed_by)
        db.session.commit()
    else:
        db.session.commit()  # This is required so when we get an Accept activity back before the end of this request, we're able to find the Follow activity
        try:
            signed_request(actor, base_activity.to_dict(), leader['inbox'])
        except:
            return error('Your follow request was not able to be delivered to that server.')

    return make_response('', 200)


def handle_undo(inbound_json, actor):
    '''
        The Undo activity is one of a handful with side effects.
        These include deleting Like objects and undoing leader-follower
        relationships. These side effects are handled here.

        Returns: None
    '''
    undone_activity = None
    if isinstance(inbound_json['object'], str):
        undone_activity = APObject.get_object_from_url(inbound_json['object'])
    elif isinstance(inbound_json['object'], dict):
        undone_activity = APObject.get_object_from_url(inbound_json['object']['id'])
    
    if undone_activity is None:
        return error('Could not undo activity: activity not found.', 404)

    if undone_activity.internal_actor_id != actor.id:
        return error('You cannot undo activities performed by other actors.')

    if isinstance(undone_activity, Follow):
        pass
    elif isinstance(undone_activity, Like):
        db.session.delete(undone_activity)
    else:
        return error('You cannot undo that kind of activity.')


def handle_delete(inbound_json, actor):

    deleted_object = None
    if isinstance(inbound_json['object'], str):
        deleted_object = APObject.get_object_from_url(inbound_json['object'])
    elif isinstance(inbound_json['object'], dict):
        deleted_object = APObject.get_object_from_url(inbound_json['object']['id'])
    
    if deleted_object is None:
        return error('Could not delete activity: activity not found.', 404)

    if deleted_object.internal_author_id != actor.id:
        return error('You cannot delete objects created by other actors.')

    if isinstance(deleted_object, Note):
        db.session.delete(deleted_object)


@require_signin
def post_outbox_c2s(actor_name, user=None):

    # Verify that user has permission to POST to this outbox
    actor = outbox_permission_check(actor_name, user)
    if actor is None:
        return error('You can\'t post to the outbox of an actor that isn\'t yours.')

    inbound_json = wrap_raw_object(request.get_json())

    is_local = determine_if_local(inbound_json)

    base_objects = get_base_objects(inbound_json)
    if not isinstance(base_objects, tuple):
        return base_objects

    (base_activity, base_object) = base_objects

    base_activity.set_actor(actor)

    base_activity.set_object(base_object)

    # set the inReplyTo field
    if isinstance(base_object, db.Model) and isinstance(inbound_json['object'], dict) and 'inReplyTo' in inbound_json['object']:
        base_object.set_in_reply_to(inbound_json['object']['inReplyTo'])


    #set the to, bto, cc, and bcc fields
    base_activity.add_all_recipients(inbound_json)
    if isinstance(base_object, db.Model):
        base_object.add_all_recipients(inbound_json['object'])

    # tags
    if 'tag' in inbound_json and isinstance(inbound_json['tag'], list):
        for tag in inbound_json['tag']:
            base_activity.add_tag(tag)
    
    if isinstance(base_object, APObject) and isinstance(inbound_json['object'], dict) and 'tag' in inbound_json['object']:
        for tag in inbound_json['object']['tag']:
            base_object.add_tag(tag)

    # Handle requirements for specific object types
    if inbound_json['type'] == 'Create':
        if inbound_json['object']['type'] == 'Note':
            base_object.attribute_to(actor)
            base_object.content = inbound_json['object']['content']
    
    elif inbound_json['type'] == 'Follow':
        return handle_follow(inbound_json, actor, base_activity, base_object, is_local)

    elif inbound_json['type'] == 'Like':
        liked_object_url = None
        if isinstance(inbound_json['object'], dict):
            liked_object_url = inbound_json['object']['id']
        else:
            liked_object_url = inbound_json['object']
        #We have to check if the count is > 1 because the Like object has already been flushed by the time these checks are being done.
        existing_like_count = db.session.query(Like).filter(Like.external_object_id == liked_object_url).filter(Like.internal_actor_id == actor.id).count()
        if existing_like_count > 1:
            return error('You already like that object.')
        else:
            local_object = APObject.get_object_from_url(liked_object_url)
            if local_object is not None:
                existing_like_count = db.session.query(Like).filter(Like.internal_object_id == local_object.id).filter(Like.internal_actor_id == actor.id).count()
                if existing_like_count > 1:
                    return error('You already like that object.')

    # We have to generate the message delivery text because
    # The delete activity disrupts the to_dict function
    # by preventing the 'id' property of the dictionary
    # from being generated. This confuses recieving servers.

    delivery_message = base_activity.to_dict()

    if inbound_json['type'] == 'Delete':
        err_response = handle_delete(inbound_json, actor)
        if err_response is not None:
            return err_response

    elif inbound_json['type'] == 'Undo':
        err_response = handle_undo(inbound_json, actor)
        if err_response is not None:
            return err_response

    #finally, commit changes to database and then deliver the objects.
    db.session.commit()

    deliver(actor, delivery_message)

    return make_response('', 201)



@app.route('/api/v1/actors/<actor_name>/outbox', methods=['GET', 'POST'])
def route_user_outbox(actor_name):
    '''
        Post requests to an actor's outbox can come from either a C2S or S2S
        interaction. Here we determine which type of request is being received
        and act accordingly. GET requests are also permitted.
    '''
    if request.method == 'GET':
        return get_outbox(actor_name)
    elif request.method == 'POST' and 'uid' in session:
        return post_outbox_c2s(actor_name)
    else:
        return error('Invalid request')



@app.route('/api/v1/actors/<actor_name>/outbox/<int:page>')
def route_user_outbox_paginated(actor_name, page):

    # Make sure actor exists
    actor = db.session.query(Actor).filter(db.func.lower(
        Actor.username) == db.func.lower(actor_name)).first()

    if actor is None:
        return error('Actor not found', 404)

    # Variables
    total_items = db.session.query(Activity).filter(Activity.internal_actor_id == actor.id).count()
    api_url = os.environ['API_URL']
    items_per_page = 20
    max_id = None
    if 'maxId' in request.args:
        max_id = int(request.args['maxId'])

    # Create base query
    base_query = db.session.query(Activity).filter(
        Activity.internal_actor_id == actor.id)

    if max_id is not None:
        base_query = base_query.filter(Activity.id <= int(request.args['maxId']))

    base_query = base_query.order_by(Activity.published.desc()).paginate(page, 20)

    activities = base_query.items

    ordered_items = []

    for activity in activities:
        ordered_items.append(activity.to_dict())

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{api_url}/actors/{actor_name}/outbox/{page}',
        'partOf': f'{api_url}/actors/{actor_name}/outbox',
        'type': 'OrderedCollectionPage',
        'orderedItems': ordered_items
    }

    # Add optional maxId parameter
    if max_id is not None:
        output['id'] = output['id'] + f'?maxId={max_id}'

    # add optional 'prev' page
    if page > 1:
        prev = f'{api_url}/actors/{actor_name}/outbox/{page-1}'
        if max_id is not None:
            prev = prev + f'?maxId={max_id}'
        output['prev'] = prev

    # add optional 'next' page
    if total_items > items_per_page * page:
        _next = f'{api_url}/actors/{actor_name}/outbox/{page+1}'
        if max_id is not None:
            _next = _next + f'?maxId={max_id}'
        output['next'] = _next

    output = make_response(output, 200)
    output.headers['Content-Type'] = 'application/activity+json'
    return output



def get_outbox(username):

    username = username.lower()

    actor = db.session.query(Actor).filter_by(username=username).first()
    if not actor:
        return error('Actor not found', 404)

    items_per_page = 20
    total_items = db.session.query(Activity).filter(Activity.internal_actor_id == actor.id).count()

    max_id_object = db.session.query(Activity).filter(
        Activity.internal_actor_id == actor.id).order_by(Activity.id.desc()).first()
    max_id = 0
    if max_id_object is not None:
        max_id = max_id_object.id

    max_page = ceil(total_items / items_per_page)
    api_url = os.environ['API_URL']

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{api_url}/actors/{username}/outbox',
        'type': 'OrderedCollection',
        'totalItems': total_items,
        'first': f'{api_url}/actors/{username}/outbox/1?maxId={max_id}',
        'last': f'{api_url}/actors/{username}/outbox/{max_page}?maxId={max_id}'
    }

    response = make_response(output, 200)
    response.headers['Content-Type'] = 'application/activity+json'
    return response
