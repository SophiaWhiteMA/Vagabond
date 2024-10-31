from flask import make_response, jsonify, request

from vagabond.__main__ import app, db
from vagabond.models import APObjectType, APObject, Actor
from vagabond.util import xsd_datetime
from vagabond.routes import error

from math import ceil

import os

@app.route('/api/v1/objects/<int:object_id>')
def route_get_object_by_id(object_id):

    ap_object = db.session.query(APObject).get(object_id)

    if ap_object is None:
        return error('Object not found', 404)
        
    response = make_response(ap_object.to_dict(), 200)
    response.headers['Content-Type'] = 'application/activity+json'
    return response


@app.route('/api/v1/objects/<int:object_id>/replies')
def route_get_object_replies_by_id(object_id):

    ap_object = db.session.query(APObject).get(object_id)

    if ap_object is None:
        return error('Object not found', 404)

    api_url = os.environ['API_URL']
    items_per_page = 20

    #determine total items
    total_items = db.session.query(APObject).filter(APObject.in_reply_to_internal_id == ap_object.id).count()

    #Calculate max ID
    max_id = 0
    max_id_object = db.session.query(APObject).filter(APObject.in_reply_to_internal_id == ap_object.id).order_by(APObject.id.desc()).first()
    if max_id_object is not None:
        max_id = max_id_object.id

    root_url = f'{api_url}/objects/{object_id}/replies'
    max_page = ceil(total_items / items_per_page)

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': root_url,
        'type': 'OrderedCollection',
        'totalItems': total_items,
    }

    if total_items > 0:
        output['first'] = f'{root_url}/1?maxId={max_id}'
        output['last'] = f'{root_url}/{max_page}?maxId={max_id}'
    

    output = make_response(output)
    output.headers['content-type'] = 'application/activity+json'

    return output
        
    
@app.route('/api/v1/objects/<int:object_id>/replies/<int:page>')
def route_get_object_replies_by_id_paginated(object_id, page):

    # Make sure object exists
    ap_object = db.session.query(APObject).get(object_id)

    if ap_object is None:
        return error('Object not found', 404)


    # set variables
    max_id = None
    if 'maxId' in request.args:
        max_id = int(request.args['maxId'])

    total_items = db.session.query(APObject).filter(APObject.in_reply_to_internal_id == ap_object.id)
    if max_id is not None:
        total_items = total_items.filter(APObject.id <= max_id)
    total_items = total_items.count()

    api_url = os.environ['API_URL']
    items_per_page = 20

    base_query = db.session.query(APObject).filter(APObject.in_reply_to_internal_id == object_id)

    if max_id is not None:
        base_query = base_query.filter(APObject.id <= int(request.args['maxId']))

    items = base_query.order_by(APObject.id.desc()).paginate(page, items_per_page).items

    ordered_items = []

    for item in items:
        ordered_items.append(item.to_dict())

    output = {
        '@context': 'https://www.w3.org/ns/activitystreams',
        'id': f'{api_url}/objects/{object_id}/replies/{page}',
        'type': 'OrderedCollectionPage',
        'orderedItems': ordered_items,
        'partOf': f'{api_url}/objects/{object_id}/replies'
    }

    # set optional maxId param
    if 'maxId' in request.args:
        max_id = int(request.args['maxId'])
        output['id'] = output['id'] + f'?maxId={max_id}'

    # set optional next page
    if total_items > items_per_page * page:
        output['next'] = f'{api_url}/objects/{object_id}/replies/{page+1}'
        if 'maxId' in request.args:
            max_id = int(request.args['maxId'])
            output['next'] = output['next'] + f'?maxId={max_id}'

    #set optinal 'prev' page
    if page > 1:
        output['prev'] = f'{api_url}/objects/{object_id}/replies/{page-1}'
        if 'maxId' in request.args:
            output['prev'] = output['prev'] + f'?maxId={max_id}'

    output = make_response(output)
    output.headers['content-type'] = 'application/activity+json'
    return output
