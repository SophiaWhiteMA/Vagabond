from vagabond.__main__ import db
from vagabond.models import Activity, APObjectType


class Delete(Activity):

    __mapper_args__ = {
        'polymorphic_identity': APObjectType.DELETE
    }
