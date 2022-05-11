from flask_sqlalchemy import SQLAlchemy
import datetime
import string 
import random

db = SQLAlchemy()

class User(db.Model):
    id = db.column(db.Integer, primary_key=1)
    username = db.column(db.String(80), unique=True, nullable=False)
    email = db.column(db.String(80), unique=True, nullable=False)
    password = db.column(db.Text(), nullable=False)
    created_at = db.column(db.DateTime, default=datetime.now())
    updated_at = db.column(db.DateTime, onupdate=datetime.now())
    
    bookmarks = db.relationship('Bookmark', backref='user')

    def generate_short_characters(self):
        
        characters = string.digits+string.ascii_letters
        pick = ''.join(random.choices(characters, k=3))

        link = self.query.filter_by(short_url=pick).first()
        
        if link: 
            self.generate_short_characters() 
        else:
            return pick



    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        self.short_url = self.generate_short_characters()

    def __repr__(self) -> str:
        return 'User >>> {self.username}'

class Bookmark(db.Model):
    id = db.column(db.Integer, primary_key=1)
    body = db.column(db.Text(), nullable=True)
    url = db.column(db.Text(), nullable=False)
    short_url = db.column(db.String(3), nullable=False)
    vistits = db.column(db.Integer, default=0)
    user_id = db.column(db.ForeignKey('user.id'))
    created_at = db.column(db.DateTime, default=datetime.now())
    updated_at = db.column(db.DateTime, onupdate=datetime.now())


    def __repr__(self) -> str:
        return 'Bookmark >>> {self.url}'


    
