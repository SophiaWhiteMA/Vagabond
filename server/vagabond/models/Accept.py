from vagabond.__main__ import db
from vagabond.models import Activity, APObjectType


class Accept(Activity):

    __mapper_args__ = {
        'polymorphic_identity': APObjectType.ACCEPT
    }
