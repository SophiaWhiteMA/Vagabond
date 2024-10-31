from vagabond.__main__ import db

class FollowedBy(db.Model):

    '''
        Representation of who is following a local Vagabond actor. The inboxes
        (and shared inboxes, if they exist) of the followers are stored in this table
        as well.
    '''

    id = db.Column(db.Integer, primary_key=True)

    leader_id = db.Column(db.Integer, db.ForeignKey('ap_object.id'), nullable=False)
    leader = db.relationship('Actor', backref='followed_by')

    approved = db.Column(db.Boolean, nullable=False)

    follower = db.Column(db.String(256), nullable=False) #URL of follower

    follower_inbox = db.Column(db.String(256), nullable=False)
    follower_shared_inbox = db.Column(db.String(256), nullable=True)

    def __init__(self, leader_id, follower, follower_inbox, follower_shared_inbox=None, approved=True):
        '''
            leader_id: int
            follower: str
                URL of the follower
            follower_inbox: str
            ?follower_shared_inbox: str
        '''
        self.leader_id = leader_id
        self.follower = follower
        self.follower_inbox = follower_inbox
        self.follower_shared_inbox = follower_shared_inbox
        self.approved = approved