from flask import render_template, redirect, url_for, flash, request, make_response, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import csrf
from app import db
from app.models import User, LoginActivity, Role
from .forms import LoginForm, RegisterForm
from . import auth_bp

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل.', 'danger')

        role_name = form.role.data  # "admin" أو "pharmacist"

        role = Role.query.filter_by(role=role_name).first()
        if not role:
            flash('الدور المحدد غير موجود في قاعدة البيانات', 'danger')
            return render_template('auth/register.html', form=form)

        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role_id=role.id,
            last_login=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()

        flash('تم إنشاء الحساب بنجاح. يمكنك تسجيل الدخول الآن.', 'success')
        #return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            # Record login time
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Add login activity
            login_record = LoginActivity(
                user_id=user.id,
                login_time=datetime.utcnow()
            )
            db.session.add(login_record)
            db.session.commit()

            # Set session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role.role

            flash('تم تسجيل الدخول بنجاح!', 'success')

            if user.role.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role.role == 'pharmacist':
                return redirect(url_for('pharmacist.pharmacist_dashboard'))
            else:
                flash('نوع المستخدم غير معروف، الرجاء التواصل مع الدعم.', 'warning')
                return redirect(url_for('auth.login'))
        else:
            flash(' اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')

    if user_id:
        # تحديث وقت الخروج في سجل النشاط
        last_login = LoginActivity.query.filter_by(user_id=user_id).order_by(LoginActivity.login_time.desc()).first()
        if last_login and last_login.logout_time is None:
            last_login.logout_time = datetime.utcnow()
            db.session.commit()

        # حذف بيانات الجلسة
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('role', None)

        flash('تم تسجيل الخروج بنجاح', 'info')

    return redirect(url_for('auth.login'))

# API TESTING ROUTES
@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()

    if not data:
        return {"error": "Missing JSON body"}, 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password:
        return {"error": "Username and password are required"}, 400

    if len(username) < 3 or len(password) < 6:
        return {"error": "Validation failed: username or password too short"}, 400

    if User.query.filter_by(username=username).first():
        return {"error": "Username already exists"}, 400

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        role_id=2,
        last_login=datetime.utcnow(),
        created_at=datetime.utcnow()
    )

    db.session.add(new_user)
    db.session.commit()

    return {"message": "User registered successfully"}, 201

csrf.exempt(api_register)