from vagabond.__main__ import app, db

from vagabond.util import xsd_datetime

from datetime import datetime



class Notification(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)

    actor_id = db.Column(db.Integer, db.ForeignKey('ap_object.id'))
    content = db.Column(db.String(256), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    type = db.Column(db.String(16), nullable=False)

    actor = db.relationship('Actor')

    def __init__(self, actor, content, _type):
        '''
            actor: Actor to which this notification belongs
            content (str): Message contents of the notification
            _type (str): Type of notification (ie, Follow, Dislike, Mention, etc.)
        '''
        self.actor_id = actor.id
        self.content = content
        self.type = _type

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'published': xsd_datetime(self.date),
            'type': self.type
        }