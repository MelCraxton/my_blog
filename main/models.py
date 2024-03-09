from datetime import datetime
from main import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    about_author = db.Column(db.String(1000), nullable=False, default='About info goes here')
    # Creates a relationship to the Posts class for author, one post can have one author
    # One author can have many posts, lazy will let SQLAlchemy load the
    # data in one go. 'Post' references the class below.
    posts = db.relationship('Post', backref='author', lazy=True)

    # What we want this to look like when we print a user object
    def __repr__(self):
        return f'User({self.username}, {self.email}, {self.image_file})'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    introduction = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(100), nullable=False)
    image_filename = db.Column(db.String(20), nullable=False, default='images/background_images/default.png')
    image_title = db.Column(db.String(120), nullable=False, default='Place title here')
    # The id of the user that authored the post, 'user.id' references
    # the table name in the User class above
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'User({self.title}, {self.date_posted})'