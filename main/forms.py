from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
# for wtforms validators - Email ensures the email is valid, Length ensures the username, password, etc.
from flask_wtf.file import FileField, FileAllowed
# is a min or max length, EqualTo ensures confrim_password is the same as password
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import User
from flask_ckeditor import CKEditorField

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken, please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken, please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    about_author = TextAreaField('About', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('That username is taken, please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken, please choose a different one.')

def validate_category(form, field):
    valid_categories = ['Python', 'SQL', 'Concepts', 'Other']
    if field.data not in valid_categories:
        raise ValidationError('Category must be Python, SQL, Concepts or Other.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    introduction = TextAreaField('Introduction', validators=[DataRequired()])
    content = CKEditorField('Post Content', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired(), validate_category])
    image_filename = FileField('Background Image', validators=[FileAllowed(['jpg','png'])])
    image_title = StringField('Image title')
    submit = SubmitField('Post')



