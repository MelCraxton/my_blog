from flask import render_template, flash, redirect, url_for, request, abort
from main import app, db, bcrypt
from main.models import User, Post
from main.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image
from datetime import datetime
import random


# Context processor to make categories available to all templates
@app.context_processor
def inject_categories():
    page = request.args.get('page', default=1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    categories = db.session.query(Post.category).distinct().all()
    categories = [category[0] for category in categories]
    return dict(categories=categories, posts=posts)


# Context processor to make posts available to all templates
@app.context_processor
def inject_posts():
    page = request.args.get('page', default=1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return dict(posts=posts)

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', default=1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', title='Home', posts=posts)


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', default=1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    title = f'Author - {user.username.lower()}'
    image_file = url_for('static', filename='images/profile_pics/' + user.image_file)
    about_author = user.about_author
    return render_template('author.html', title=title, posts=posts, user=user, image_file=image_file, about_author=about_author)


@app.route('/category/<string:category>')
def category(category):
    page = request.args.get('page', default=1, type=int)
    posts = Post.query.filter_by(category=category).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    title = f'{category}'  # Use the input parameter directly for the title
    return render_template('category.html', title=title, posts=posts, category=category)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    # This will tell is form validated on submit
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created you are now able to login!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# # Kept for reference
# @app.route('/login', methods=['GET','POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         if form.email.data == 'm@gmail.com' and form.password.data == '1234':
#             flash('You have been successfully logged in!', 'success')
#             return redirect(url_for('home'))
#         else:
#             flash('Login Unsuccessful. Please try again', 'danger')
#     return render_template('login.html', title='Login', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        # form.email.data is the email that the user entered into the login form
        # we want to filter to see if the email exists in the db
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please try again', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/profile_pics', picture_fn)

    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_author = form.about_author.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_author.data = current_user.about_author
    image_file = url_for('static', filename='images/profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


def save_background_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/background_images', picture_fn)

    output_size = (800, 654)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    image_filename = None
    if form.validate_on_submit():
        if form.image_filename.data:
            picture_file = save_background_picture(form.image_filename.data)
            image_filename = 'images/background_images/' + picture_file
            db.session.commit()
        post = Post(title=form.title.data, introduction=form.introduction.data,
                    category=form.category.data, content=form.content.data,
                    author=current_user, image_filename=image_filename,
                    image_title=form.image_title.data)
        db.session.add(post)
        db.session.commit()

        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New post',
                           form=form, image_filename=image_filename,
                           page_title='Create Post', page_subtitle='Create a new post')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.introduction = form.introduction.data
        post.category = form.category.data
        # post.image_title = form.image_title.data
        # post.image_filename = form.image_filename.data
        post.content = form.content.data
        # Dont need to do db.session.add() as the post is already in db
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.introduction.data = post.introduction
        form.category.data = post.category
        form.image_title.data = post.image_title
        form.image_filename.data = post.image_filename
        form.content.data = post.content
    return render_template('create_post.html', title='Update post', form=form,
                           page_title='Update Post', page_subtitle='Update existing post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))