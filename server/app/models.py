from app import db
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from dataclasses import dataclass

@dataclass
class CallCard(db.Model):
    __tablename__ = 'calls'

    id: int
    text: list
    created_at: datetime
    nsfw: bool

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(ARRAY(db.String()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    nsfw = db.Column(db.Boolean)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_dict(self):
        return {
            "id": str(self.id),
            "text": self.text,
            "created_at": str(self.created_at),
            "nsfw": self.nsfw
        }

@dataclass
class ResponseCard(db.Model):
    __tablename__ = 'responses'

    id: int
    text: list
    created_at: datetime
    nsfw: bool

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(ARRAY(db.String()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    nsfw = db.Column(db.Boolean)

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def to_dict(self):
        return {
            "id": str(self.id),
            "text": self.text,
            "created_at": str(self.created_at),
            "nsfw": self.nsfw
        }
