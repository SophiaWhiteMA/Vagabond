from vagabond.__main__ import db
from vagabond.models import APObject, APObjectType

class Note(APObject):

    __mapper_args__ = {
        'polymorphic_identity': APObjectType.NOTE
    }
