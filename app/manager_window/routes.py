# app/manager/routes.py
from flask import render_template, redirect, url_for, flash, request, session
from app import db
from app.models import Product, Sale, SaleItem, Report, Manager, Pharmacist, LoginActivity, Pharmacy
from sqlalchemy import func
from werkzeug.security import generate_password_hash
from app.manager_window.forms import PharmacistForm
from datetime import datetime, date, timedelta, timezone
from . import manager_bp


@manager_bp.route('/dashboard')
def manager_dashboard():
    if 'manager_id' not in session:
        return redirect(url_for('auth.manager_login'))

    pharmacy_id = session.get('pharmacy_id')
    # إجمالي المستخدمين (صيادلة)
    total_pharmacists = db.session.query(Pharmacist).filter_by(pharmacy_id=pharmacy_id, active=True).count()

    # إجمالي المبيعات اليوم
    today = date.today()
    today_sales = db.session.query(func.coalesce(func.sum(Sale.total_price), 0)).join(Pharmacist).filter(
        Pharmacist.pharmacy_id == pharmacy_id,
        Pharmacist.active == True,
        func.date(Sale.created_at) == today
    ).scalar() or 0

    # إجمالي أرباح اليوم (نفترض الربح = مبيعات - تكلفة الشراء)
    today_profit = db.session.query(
        func.coalesce(func.sum(SaleItem.subtotal_price - (SaleItem.quantity_sold * Product.purchase_price)), 0)
    ).join(Sale).join(Product).filter(
        Sale.pharmacy_id == pharmacy_id,
        func.date(Sale.created_at) == today
    ).scalar() or 0

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
    ).scalar() or 0

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

    manager = Manager.query.get(session['manager_id'])
    pharmacy_id = manager.pharmacy_id   # دايماً مضمون مش None
    today = date.today()

    pharmacists = Pharmacist.query.filter_by(pharmacy_id=pharmacy_id, active=True).all()

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

    return render_template(
        'manager/pharmacists.html',
        pharmacists=pharmacist_data,
        total_pharmacists=len(pharmacists)
    )



# Add Pharmacist (GET/POST)
@manager_bp.route('/pharmacists/add', methods=['GET', 'POST'])
def add_pharmacist():
    if 'manager_id' not in session:
        return redirect(url_for('auth.manager_login'))

    form = PharmacistForm()
    if form.validate_on_submit():
        manager = Manager.query.get(session['manager_id'])
        if not manager:
            flash('لم يتم العثور على المدير', 'danger')
            return redirect(url_for('auth.manager_login'))

        pharmacy_id = manager.pharmacy_id
        hashed_password = generate_password_hash(form.password.data)

        # Check if the pharmacist already exists
        existing = Pharmacist.query.filter_by(email=form.email.data).first()
        if existing:
            # If exists and is inactive -> reactivate
            if not existing.active:
                existing.active = True
                existing.password_hash = hashed_password
                existing.pharmacy_id = pharmacy_id  # Ensure linked to this pharmacy
                db.session.commit()
                flash('تمت إعادة تفعيل الصيدلي بنجاح', 'success')
            else:
                flash('هذا البريد مستخدم من قبل صيدلي نشط بالفعل.', 'warning')
            return redirect(url_for('manager.pharmacists_list'))

        # Create new pharmacist
        new_pharmacist = Pharmacist(
            name=form.pharmacist_name.data,
            email=form.email.data,
            password_hash=hashed_password,
            pharmacy_id=pharmacy_id,
            active=True,
            created_at=datetime.now(timezone.utc)
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


# Deactivate (soft-delete) pharmacist
@manager_bp.route('/pharmacists/<int:pharmacist_id>/deactivate', methods=['GET', 'POST'])
def deactivate_pharmacist(pharmacist_id):
    # Using GET here for convenience if you want to call via link; in production prefer POST.
    if 'manager_id' not in session:
        return redirect(url_for('auth.manager_login'))

    pharmacist = Pharmacist.query.get_or_404(pharmacist_id)
    pharmacist.active = False
    db.session.commit()

    flash('تم تعطيل الصيدلي بنجاح', 'success')
    return redirect(url_for('manager.pharmacists_list'))


# ========== Pharmacy Management =============
@manager_bp.route('/pharmacy', methods=['GET'])
def manage_pharmacy():
    pharmacy_id = session.get('pharmacy_id')
    pharmacy = Pharmacy.query.filter(Pharmacy.id == pharmacy_id).first()
    pharmacists = Pharmacist.query.filter_by(pharmacy_id=pharmacy_id, active=True).all()
    total_pharmacists = len(pharmacists)
    total_products = Product.query.filter_by(pharmacy_id=pharmacy_id).count()

    # Filtering sales
    pharmacist_id = request.args.get('pharmacist_id', type=int)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    query = Sale.query.filter_by(pharmacy_id=pharmacy_id)
    if pharmacist_id:
        query = query.filter(Sale.pharmacist_id == pharmacist_id)
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            query = query.filter(Sale.created_at >= from_dt)
        except ValueError:
            pass
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Sale.created_at <= to_dt)
        except ValueError:
            pass
    sales = query.order_by(Sale.created_at.desc()).all()
    total_sales = sum(s.total_price or 0 for s in sales)

    return render_template(
        'manager/pharmacy.html',
        pharmacists=pharmacists,
        total_pharmacists=total_pharmacists,
        pharmacy=pharmacy,
        sales=sales,
        total_sales=total_sales,
        total_products=total_products
    )

@manager_bp.route('/sales-report')
def sales_report():
    pharmacist_id = request.args.get('pharmacist_id', type=int)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    # Base query
    query = Sale.query

    # Filter by pharmacist
    if pharmacist_id:
        query = query.filter(Sale.pharmacist_id == pharmacist_id)

    # Filter by date range
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            query = query.filter(Sale.created_at >= from_dt)
        except ValueError:
            pass

    if to_date:
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            # نضيف يوم واحد علشان يشمل التاريخ كامل
            to_dt = to_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Sale.created_at <= to_dt)
        except ValueError:
            pass

    sales = query.order_by(Sale.created_at.desc()).all()
    pharmacists = Pharmacist.query.all()

    return render_template(
        "manager/sales_report.html",  # عدل حسب مكان ملف HTML
        sales=sales,
        pharmacists=pharmacists
    )

# Products List for Pharmacy
@manager_bp.route('/pharmacy/products')
def products_list():
    pharmacy_id = session.get('pharmacy_id')
    products = Product.query.filter_by(pharmacy_id=pharmacy_id).all()
    pharmacy = Pharmacy.query.filter_by(id=pharmacy_id).first()
    return render_template('manager/products_list.html', products=products, pharmacy=pharmacy)