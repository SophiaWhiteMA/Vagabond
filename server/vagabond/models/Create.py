from vagabond.__main__ import db
from vagabond.models import APObjectType, Activity

class Create(Activity):

    __mapper_args__ = {
        'polymorphic_identity': APObjectType.CREATE
    }