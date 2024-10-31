from vagabond.__main__ import db
from vagabond.models import APObject, APObjectType, Actor

class Activity(APObject):

    internal_object_id = db.Column(db.ForeignKey('ap_object.id'))
    external_object_id = db.Column(db.String(1024))
    internal_actor_id = db.Column(db.ForeignKey('ap_object.id'))
    external_actor_id = db.Column(db.String(1024))
    
    internal_object = db.relationship('APObject', foreign_keys=[internal_object_id], remote_side=APObject.id, backref=db.backref('activities', cascade='all, delete-orphan'))


    __mapper_args__ = {
        'polymorphic_identity': APObjectType.ACTIVITY
    }


    def set_object(self, obj):
        '''
            Input: vagabond.models.APObject | str | dict

            Takes an instance of APObject, a URL representing the object,
            or a dictionary representing the object and wraps this instance
            of Activity around it.
        '''
        if isinstance(obj, db.Model):
            self.internal_object_id = obj.id
            

        elif isinstance(obj, str):
            interal_object = APObject.get_object_from_url(obj)
            if interal_object is not None:
                self.internal_object_id = interal_object.id

            self.external_object_id = obj

        elif isinstance(obj, dict) and 'id' in obj:
            interal_object = APObject.get_object_from_url(obj['id'])
            if interal_object is not None:
                self.internal_object_id = interal_object.id      
            self.external_object_id = obj['id']

        else:
            raise Exception('Activity#set_object method requires an APObject, a string, or a dictionary')
        

    def set_actor(self, actor):
        '''
            Input: vagabond.models.Actor | str | dict
        '''
        if isinstance(actor, db.Model):
            self.internal_actor_id = actor.id
        elif isinstance(actor, str):
            self.external_actor_id = actor
        elif isinstance(actor, dict) and 'id' in actor:
            self.external_actor_id = actor['id']
        else:
            raise Exception('Activity#set_actor method requires an Actor, a string, or a dictionary')


    def to_dict(self):
        output = super().to_dict()

        if self.internal_object_id is not None:
            _object = db.session.query(APObject).get(self.internal_object_id)
            if _object is not None:
                    output['object'] = _object.to_dict()

        elif self.external_object_id is not None:
            output['object'] = self.external_object_id
        else:
            raise Exception('Activites must have an internal or external object.')

        if self.internal_actor_id is not None:
            output['actor'] = db.session.query(APObject).get(self.internal_actor_id).to_dict()['id']
        elif self.external_actor_id is not None:
            output['actor'] = self.external_actor_id
        else:
            raise Exception('Activies must have an internal or external actor')

        return output