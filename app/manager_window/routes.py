from flask import render_template, redirect, url_for, flash, request,session, jsonify
from app import db
from app.models import Product, Sale, SaleItem, Report, Manager, Pharmacist, LoginActivity
from sqlalchemy import func
from app.manager_window.forms import PharmacistForm
from datetime import datetime, date, timedelta
from . import manager_bp


@manager_bp.route('/dashboard')
def manager_dashboard():
    if 'manager_id' not in session:
        return redirect(url_for('auth.manager_login'))

    pharmacy_id = session.get('pharmacy_id')
    # إجمالي المستخدمين (مدير + صيادلة)
    total_pharmacists = db.session.query(Pharmacist).filter_by(pharmacy_id=pharmacy_id).count()
    # إجمالي المبيعات اليوم
    today = date.today()
    today_sales = db.session.query(func.coalesce(func.sum(Sale.total_price), 0)).join(Pharmacist).filter(
        Pharmacist.pharmacy_id == pharmacy_id,
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