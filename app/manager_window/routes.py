from flask import render_template, redirect, url_for, flash, request,session, jsonify
from app import db
from app.models import Product, Sale, SaleItem, Report, Manager, Pharmacist, LoginActivity
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from app.manager_window.forms import PharmacistForm
from datetime import datetime, date, timedelta
from . import manager_bp


@manager_bp.route('/dashboard')
def manager_dashboard():
    if 'manager_id' not in session:
        return redirect(url_for('auth.manager_login'))

    pharmacy_id = session.get('pharmacy_id')
    # إجمالي المستخدمين (مدير + صيادلة)
    total_pharmacists = db.session.query(Pharmacist).filter_by(pharmacy_id=pharmacy_id, active=True).count()
    # إجمالي المبيعات اليوم
    today = date.today()
    today_sales = db.session.query(func.coalesce(func.sum(Sale.total_price), 0)).join(Pharmacist).filter(
        Pharmacist.pharmacy_id == pharmacy_id,
        Pharmacist.active == True,
        func.date(Sale.created_at) == today
    ).scalar()
    # إجمالي أرباح اليوم (هنا نفترض الربح = المبيعات - الشراء)
    today_profit = db.session.query(
        func.coalesce(func.sum((SaleItem.subtotal_price - (SaleItem.quantity_sold * Product.purchase_price))), 0)
    ).join(Sale).join(Product).join(Pharmacist).filter(
        Pharmacist.pharmacy_id == pharmacy_id,
        func.date(Sale.created_at) == today
    ).scalar()
    # المستخدمين النشطين (صيادلة متصلين اليوم من صيدلية المدير فقط)
    active_pharmacists = db.session.query(Pharmacist).join(LoginActivity).filter(
        Pharmacist.pharmacy_id == pharmacy_id,
        func.date(LoginActivity.login_time) == today
    ).distinct().all()
    # إجمالي الأدوية
    total_products = db.session.query(Product).filter_by(pharmacy_id=pharmacy_id).count()
    # مبيعات الأسبوع
    week_start = today - timedelta(days=today.weekday())
    week_sales = db.session.query(func.coalesce(func.sum(Sale.total_price), 0)).join(Pharmacist).filter(
        Pharmacist.pharmacy_id == pharmacy_id,
        Sale.created_at >= week_start
    ).scalar()

    return render_template(
        'manager/dashboard.html',
        total_pharmacists=total_pharmacists,
        today_sales=today_sales,
        today_profit=today_profit,
        active_pharmacists=active_pharmacists,
        total_products=total_products,
        week_sales=week_sales
    )


# ========== Pharmacists Management =============
@manager_bp.route('/pharmacists')
def pharmacists_list():
    if 'manager_id' not in session:
        return redirect(url_for('auth.manager_login'))
    pharmacy_id = session.get('pharmacy_id')
    today = date.today()
    pharmacists = db.session.query(Pharmacist).filter(
        Pharmacist.pharmacy_id == pharmacy_id,
        Pharmacist.active == True).all()
    pharmacist_data = []
    for p in pharmacists:
        login_count_today = db.session.query(LoginActivity).filter(
            LoginActivity.pharmacist_id == p.id,
            func.date(LoginActivity.login_time) == today
        ).count()
        sales_today = db.session.query(func.coalesce(func.sum(Sale.total_price), 0)).filter(
            Sale.pharmacist_id == p.id,
            func.date(Sale.created_at) == today
        ).scalar()
        pharmacist_data.append({
            'id': p.id,
            'name': p.name,
            'email': p.email,
            'login_count_today': login_count_today,
            'sales_today': sales_today
        })
    return render_template('manager/pharmacists.html', pharmacists=pharmacist_data, total_pharmacists=len(pharmacists))


# Add Pharmacist (GET/POST)
@manager_bp.route('/pharmacists/add', methods=['GET', 'POST'])
def add_pharmacist():
    if 'manager_id' not in session:
        return redirect(url_for('auth.manager_login'))
    form = PharmacistForm()
    if form.validate_on_submit():
        pharmacy_id = session.get('pharmacy_id')
        hashed_password = generate_password_hash(form.password.data)
        # Check if the pharmacist is inactive
        existing = Pharmacist.query.filter_by(email=form.email.data).first()
        if existing:
            existing.active = True
            existing.password_hash = hashed_password
            db.session.commit()
            flash('The pharmacist has been activated successfuly', 'succes')
            return render_template('manager/pharmacists.html', form=form)
        
        else:
            new_pharmacist = Pharmacist(
                name=form.pharmacist_name.data,
                email=form.email.data,
                password_hash=hashed_password,
                pharmacy_id=pharmacy_id
            )
            db.session.add(new_pharmacist)
            try:
                db.session.commit()
                flash('تمت إضافة الصيدلي بنجاح', 'success')
                return redirect(url_for('manager.pharmacists_list'))
            except Exception as e:
                db.session.rollback()
                flash('حدث خطأ أثناء إضافة الصيدلي: {}'.format(str(e)), 'danger')
    return render_template('manager/add_pharmacist.html', form=form)

# Pharmacist Details
@manager_bp.route('/pharmacists/<int:pharmacist_id>')
def pharmacist_details(pharmacist_id):
    if 'manager_id' not in session:
        return redirect(url_for('auth.manager_login'))
    pharmacist = Pharmacist.query.get_or_404(pharmacist_id)
    # Sales history
    sales = Sale.query.filter_by(pharmacist_id=pharmacist_id).order_by(Sale.created_at.desc()).all()
    # Login activities
    logins = LoginActivity.query.filter_by(pharmacist_id=pharmacist_id).order_by(LoginActivity.login_time.desc()).all()
    return render_template('manager/pharmacist_details.html', pharmacist=pharmacist, sales=sales, logins=logins)

@manager_bp.route('/delete_pharmacist')
def delete_pharmacist():
    pharmacist_id = session.get('pharmacist_id')

    pharmacist = Pharmacist.query.get(pharmacist_id)
    if pharmacist:
        pharmacist.active = False
        db.session.commit()

    flash('The pharmacist has been deleted successfully', 'success')

    return render_template('/manager/pharmacists.html')