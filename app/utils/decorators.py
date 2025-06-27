from flask import jsonify, session, flash, redirect, url_for
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from app import models

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('غير مصرح لك بالدخول إلى هذه الصفحة', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
