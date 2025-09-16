# app/auth/routes.py
from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app import db
from app.auth import auth_bp
from app.models import Manager, LoginActivity, Pharmacy, Pharmacist
from .forms import LoginForm, RegisterForm


# -------------------------
# Manager register & login
# -------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def manager_register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if Manager already exists
        existing_owner = Manager.query.filter_by(email=form.email.data).first()
        if existing_owner:
            flash('البريد الإلكتروني مستخدم بالفعل.', 'danger')
            return render_template('auth/manager_register.html', form=form)

        # create new Pharmacy
        new_pharmacy = Pharmacy(
            name=form.pharmacy_name.data
        )
        db.session.add(new_pharmacy)
        db.session.commit()

        # Create new Manager
        hashed_password = generate_password_hash(form.password.data)
        new_manager = Manager(
            name=form.manager_name.data,
            email=form.email.data,
            password_hash=hashed_password,
            pharmacy_id=new_pharmacy.id,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(new_manager)
        db.session.commit()

        flash('تم إنشاء الحساب بنجاح. يمكنك تسجيل الدخول الآن.', 'success')
        return redirect(url_for('auth.manager_login'))

    return render_template('auth/manager_register.html', form=form)


@auth_bp.route('/login/manager', methods=['GET', 'POST'])
def manager_login():
    form = LoginForm()
    if form.validate_on_submit():
        manager = Manager.query.filter_by(email=form.email.data).first()

        if manager and check_password_hash(manager.password_hash, form.password.data):
            # Set session
            session['manager_id'] = manager.id
            session['manager_name'] = manager.name
            session['pharmacy_name'] = manager.pharmacy.name
            session['pharmacy_id'] = manager.pharmacy.id

            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('manager.manager_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')

    return render_template('auth/manager_login.html', form=form)


# -------------------------
# Pharmacist login & logout
# -------------------------
@auth_bp.route('/login/pharmacist', methods=['GET', 'POST'])
def pharmacist_login():
    form = LoginForm()
    if form.validate_on_submit():
        # only allow active pharmacists to login
        pharmacist = Pharmacist.query.filter_by(email=form.email.data, active=True).first()

        if pharmacist and check_password_hash(pharmacist.password_hash, form.password.data):
            # Set session
            session['pharmacist_id'] = pharmacist.id
            session['pharmacist_name'] = pharmacist.name
            session['pharmacy_name'] = pharmacist.pharmacy.name
            session['pharmacy_id'] = pharmacist.pharmacy.id

            # Log login activity
            login_activity = LoginActivity(pharmacist_id=pharmacist.id)
            db.session.add(login_activity)
            db.session.commit()

            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(url_for('pharmacist.pharmacist_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')

    return render_template('auth/pharmacist_login.html', form=form)


@auth_bp.route('/logout_manager')
def logout_manager():
    # Clear manager session
    session.pop('manager_id', None)
    session.pop('manager_name', None)
    session.pop('pharmacy_name', None)
    session.pop('pharmacy_id', None)
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('auth.manager_login'))


@auth_bp.route('/logout_pharmacist')
def logout_pharmacist():
    # read pharmacist id BEFORE clearing session
    pharmacist_id = session.get('pharmacist_id')

    # Clear pharmacist session
    session.pop('pharmacist_id', None)
    session.pop('pharmacist_name', None)
    session.pop('pharmacy_name', None)
    session.pop('pharmacy_id', None)

    # Update logout time for the most recent login activity (if any)
    if pharmacist_id is not None:
        login_activity = LoginActivity.query.filter_by(
            pharmacist_id=pharmacist_id
        ).order_by(LoginActivity.login_time.desc()).first()

        if login_activity and login_activity.logout_time is None:
            login_activity.logout_time = datetime.now(timezone.utc)
            db.session.commit()

    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('auth.pharmacist_login'))
