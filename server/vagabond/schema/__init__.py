from vagabond.regex import MIME_TYPE
from vagabond.regex import XSD_DATE
from vagabond.regex import XSD_DURATION

def ap_object():
    return {
            'attachment': {
                'type': ['string', 'dict'],
                'required': False,
            },

            'attributedTo': {
                'type': ['string', 'dict'],
                'required': False,
            },

            'audience': {
                'type': ['string', 'dict'],
                'required': False,
            },

            'content': {
                'type': ['string'],  #xsd:string or rdf:langString
                'required': False,  
            },

            'context': {
                'type': ['string', 'dict'],
                'required': False,
            },

            'name': {
                'type': ['string'], #xsd:string or rdf:langString
                'required': False,
            },

            'endTime': {
                'type': ['string'], #xsd:dateTime regex datetime *
                'required': False,
                'regex': XSD_DATE
                
            },

            'generator': {
                'type': ['string', 'dict'],
                'required': False
            },

            'icon': {
                'type': ['string', 'dict'], #Image or Link
                'required': False
            },

            'image': {
                'type': ['dict'], #Extends Document, and inherits all properties from Document
                'required': False
            },

            'inReplyTo': {
                'type': ['string', 'dict'],
                'required': False
            },

            'location': {
                'type': ['string', 'dict'],
                'required': False
            },

            'preview': {
                'type': ['string', 'dict'],
                'required': False
            },

            'published': {
                'type': ['string'], #xsd:dateTime should have xsddate regex *
                'required': False,
                'regex': XSD_DATE
            },

            'replies': {
                'type': ['dict'], 
                'required': False
            },

            'startTime': {
                'type': ['string'], #xsd:dateTime *
                'required': False,
                'regex': XSD_DATE
            },

            'summary': {
                'type': ['string'], #xsd:string or rdf:langstring
                'required': False
            },

            'tag': {
                'type': ['string', 'dict'],
                'required': False

            },

            'updated': {
                'type': ['string', 'dict'],
                'required': False
            },

            'url': {
                'type': ['string'],    
                'required': False

            },
            'to': {
                'type': ['string', 'list'],
                'required': False

            },
            'bto': {
                'type': ['string', 'list'],
                'required': False

            },
            'cc': {
                'type': ['string', 'list'],
                'required': False

            },
            'bcc': {
                'type': ['string', 'list'],
                'required': False

            },
            'mediaType': {
                'type': ['string'], #MIME Media Type, or if not specified can be text/html content * something forwardslash something
                'required': False,
                'regex': MIME_TYPE

            },
            'duration': {
                'type': ['string'], #The value must be expressed as an xsd:duration
                'required': False,
                'regex': XSD_DURATION
            }
    }

def actor():
    output = ap_object()
    output['inbox'] = {
        'type': 'string',
        'required': True
    }
    output['outbox'] = {
        'type': 'string',
        'required': True
    }
    output['following'] = {
        'type': 'string',
        'required': True
    }
    output['followers'] = {
        'type': 'string',
        'required': True
    }
    output['publicKey'] = {
        'type': 'dict',
        'required': True
    }
    output['liked'] = {
        'type': 'string',
        'required': False
    }
    output['devices'] = {
        'type': 'string',
        'required': False
    }
    output['manuallyApprovesFollowers'] = {
        'type': 'string',
        'required': False
    }
    output['discoverable'] = {
        'type': 'string',
        'required': False
    }
    return output

NOTE = ap_object()
NOTE['type'] = {
        'type': 'string',
        'required': True,
        'allowed': ['Note']
        }

ACTIVITY = ap_object()
ACTIVITY['type'] = {
            'type': 'string',
            'required': True,
            'allowed': ['Follow', 'Undo', 'Delete', 'Create', 'Like', 'Accept', 'Remove']
        }