from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique = True)
    email = db.Column(db.String(120), unique = True)
    password_hash = db.Column(db.String(128)) 
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default = datetime.utcnow())
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def chek_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_avatar(self, size):
        hashed_email = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://gravatar.com/avatar/{hashed_email}?d=identicon&s={size}"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default = datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))