from vagabond.__main__ import db
from vagabond.models import APObject, APObjectType, Activity

class Follow(Activity):

    __mapper_args__ = {
        'polymorphic_identity': APObjectType.FOLLOW
    }