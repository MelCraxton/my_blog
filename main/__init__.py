from flask import Flask
import os
#Used to interact with the database
from flask_sqlalchemy import SQLAlchemy
#This will encrpty the password in the db
from flask_bcrypt import Bcrypt
#This will help users login
from flask_login import LoginManager
# This is to send mail for forgot password

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Construct the PostgreSQL URI
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Tinker01#@localhost/unnest'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unnest.db'

# Create an instance
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view='login'
login_manager.login_message_category='info'


from main import routes