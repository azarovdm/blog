from os import urandom
from flask import render_template, request, redirect, url_for 
from app import my_app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from datetime import datetime
from flask_mail import Message
from app import mail

@my_app.route('/index/<int:page>')
@my_app.route('/', methods=['get', 'post'])
@my_app.route('/index', methods=['get', 'post'])
@login_required
def index(page = 1):
    if request.method == 'GET':
        all_posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, 5, False)
        return render_template('index.html', posts = all_posts)#функция представления

    if request.method == 'POST':
        form = request.form
        post = Post(text = form.get('post_text'), author = current_user, timestamp = datetime.utcnow())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    



@my_app.route('/login', methods=['get', 'post'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('log_in.html')
    if request.method == 'POST':
        form = request.form
        inputed_username = form.get('username')
        inputed_password = form.get('password')
        inputed_remember = bool(form.get('remember'))
        user = User.query.filter_by(username = inputed_username).first()
        if user is None or not user.chek_password(inputed_password):
            return redirect(url_for('login'))
        login_user(user, remember = inputed_remember)
        return redirect(url_for('index'))


@my_app.route('/log_out')
def log_out():
    logout_user()
    return redirect(url_for('login'))

@my_app.route('/register', methods=['get', 'post'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        form = request.form
        inputed_username = form.get('username')
        inputed_password = form.get('pass')#to do уже сущёствует?
        inputed_email = form.get('email')
        user = User(username=inputed_username, email=inputed_email)
        user.set_password(inputed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

@my_app.route('/user/<requested_username>/<int:page>')
@my_app.route('/user/<requested_username>')
def user(requested_username, page = 1):
    found_user = User.query.filter_by(username = requested_username).first_or_404()
    all_posts = found_user.posts.order_by(Post.timestamp.desc()).paginate(page, 5, False)
    return render_template('user_profile.html', user=found_user, posts=all_posts)


@my_app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

@my_app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

@my_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@my_app.route('/edit_profile', methods = ['get', 'post'])
def edit_profile():
    if request.method == 'GET':
        return render_template("Edit profile.html")

    if request.method == 'POST':
        form = request.form
        new_username = form.get('username')
        about = form.get('about')
        if new_username is not None and new_username.isalnum():
            current_user.username = new_username
        current_user.about_me = about
        db.session.commit()
        return redirect(url_for('index'))

@my_app.route('/reset_password', methods = ['get', 'post'])
def reset_password():
    if request.method == 'GET':
        return render_template("reset_password.html")

    if request.method == 'POST':
        form = request.form
        _email = form.get('email')
        found_user = User.query.filter_by(email = _email).first()
        if found_user is not None:
            password = generate_password()
            found_user.set_password(password)
            db.session.commit()
            send_email(found_user, password)
        return redirect(url_for('login'))


@my_app.route('/delete_post')
def delete_post():
    post_id = request.args["post_id"]
    post = Post.query.get(post_id)
    if post.author == current_user:
        db.session.delete(post)
        db.session.commit()
    return redirect(request.referrer)

def send_email(to, new_password):
    msg = Message("reset password[Microblog]", recipients = [to.email])
    msg.body = f"""Здравствуйте, {to.username}
    Ваш новый пороль -{new_password}"""
    mail.send(msg)



def generate_password(length = 8):
    if not isinstance(length, int) or length < 8:
        raise ValueError("temp password must have positive length")
 
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(chars[c % len(chars)] for c in urandom(length))

