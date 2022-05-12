from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string 
import random

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=1)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    
    bookmarks = db.relationship('Bookmark', backref='user')

    def generate_short_characters(self):
        
        characters = string.digits+string.ascii_letters
        pick = ''.join(random.choices(characters, k=3))

        link = self.query.filter_by(short_url=pick).first()
        
        if link: 
            self.generate_short_characters() 
        else:
            return pick

    def __repr__(self) -> str:
        return 'User >>> {self.username}'

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=1)
    body = db.Column(db.Text(), nullable=True)
    url = db.Column(db.Text(), nullable=False)
    short_url = db.Column(db.String(3), nullable=False)
    vistits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())


    def __repr__(self) -> str:
        return 'Bookmark >>> {self.url}'

    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        self.short_url = self.generate_short_characters()


    
