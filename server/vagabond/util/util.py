'''
    Collectin of Vagabond utility functions.
'''

import requests

from vagabond.models import APObject

from bs4 import BeautifulSoup
from datetime import datetime


def resolve_ap_object(url, iteration=0, original_url = None):
    '''

        ActivityPub objects can be represented by inline objects
        or by links to other ActivityPub objects. This function 
        ensures that whether an inline object or URL is provided
        as input, the resolved object is returned.

        If this function finds a text/html document instead of
        a JSON document, it will attempt to locate the JSON
        document using a few common alternative locations.

        Input: URL representing an ActivityPub object | Dictionary

        Returns: ActivityPub object as a dictionary

    '''

    # Return objects that have already been resolved
    if isinstance(url, dict):
        return url

    # prevent stack overflow
    if iteration > 2:
        return None

    # Used for recursive calls
    if original_url is None:
        original_url = url

    response = requests.get(url)

    # If we get an HTML document, we need to
    # attempt to locate an alternate link. 
    if response.headers['Content-Type'].find('text/html') >= 0:
        soup = BeautifulSoup(response.text)
        links = soup.find_all('link')
        alt_url = None
        for link in links:

            if 'alternate' in link.get('rel') and link.get('type') == 'application/activity+json':
                alt_url = link.get('href')
                break

        if alt_url is None:
            return None

        # Mastodon appends .json to most documents
        with_json =  resolve_ap_object(alt_url + '.json', iteration=iteration+1, original_url=original_url)

        if with_json is not None:
            return with_json
        
        without_json =  resolve_ap_object(alt_url, iteration=iteration+1, original_url=original_url)
        return without_json

    # If we find the right content type on the first try,
    # great!
    elif response.headers['Content-Type'].find('application/activity+json') >= 0:
        return response.json()

    #Something has gone horribly wrong
    else:
        return None



def xsd_datetime(day=None):
    '''
        Returns: xsd:date formatted string

        Input: datetime.datetime object
    '''
    if day is None:
        day = datetime.now()
    xsd = '%Y-%m-%dT%H:%M:%SZ'
    return day.strftime(xsd)

