"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

   
class Follows(db.Model):

    __tablename__ = 'follows'
    
    id = db.Column(db.Integer,primary_key=True)
    user_following_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))
    user_being_followed_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"))

class Favorite(db.Model):
    
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    image_url = db.Column(db.Text)
    address1 = db.Column(db.String)
    city = db.Column(db.String)
    zip_code = db.Column(db.String)
    state = db.Column(db.String)
    phone = db.Column(db.String)
    business_id = db.Column(db.Text)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id', ondelete='cascade'))
    

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True,)
    email = db.Column(db.Text,nullable=False,unique=True,)
    username = db.Column(db.Text,nullable=False,unique=True,)
    image_url = db.Column(db.Text)
    header_image_url = db.Column(db.Text)
    bio = db.Column(db.Text)
    location = db.Column(db.Text)
    password = db.Column(db.Text,nullable=False,)
    messages = db.relationship('Message')
    followers = db.relationship("User",secondary="follows",primaryjoin=(Follows.user_being_followed_id == id),secondaryjoin=(Follows.user_following_id == id))
    following = db.relationship("User",secondary="follows",primaryjoin=(Follows.user_following_id == id),secondaryjoin=(Follows.user_being_followed_id == id))


    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer,primary_key=True,)
    text = db.Column(db.String(140),nullable=False,)
    image_url = db.Column(db.Text,default="/static/images/default-pic.png",)
    timestamp = db.Column(db.DateTime,nullable=False,default=datetime.utcnow(),)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id', ondelete='CASCADE'),nullable=False,)
    user = db.relationship('User')


def connect_db(app):
    db.app = app
    db.init_app(app)
