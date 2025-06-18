from flask import render_template, redirect, url_for, flash, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import User, LoginActivity
from .forms import LoginForm, RegisterForm
from . import auth_bp

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password_hash=hashed_password, role_id=2)  # pharmacist by default
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            token = create_access_token(identity=user.id)
            # Record login
            activity = LoginActivity(user_id=user.id)
            db.session.add(activity)
            db.session.commit()

            response = make_response(redirect(url_for('main.dashboard')))
            response.set_cookie('access_token', token)
            return response
        flash('Invalid credentials', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    last_login = LoginActivity.query.filter_by(user_id=user_id).order_by(LoginActivity.login_time.desc()).first()
    if last_login and last_login.logout_time is None:
        last_login.logout_time = datetime.utcnow()
        db.session.commit()
    response = make_response(redirect(url_for('auth.login')))
    response.delete_cookie('access_token')
    flash('Logged out', 'info')
    return response
