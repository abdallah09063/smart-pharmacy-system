from flask import render_template, redirect, url_for, flash, request,session
from app import db
from app.models import Product
from sqlalchemy import func
from app.pharmacist_window.forms import ProductForm
from datetime import datetime
from . import pharmacist_bp

@pharmacist_bp.route('/') 
def pharmacist_dashboard():
    product_count = db.session.query(func.count(func.distinct(Product.name))).scalar()
    return render_template('pharmacist/dashboard.html', product_count=product_count ,form=ProductForm())

@pharmacist_bp.route('/add-product', methods=['POST'])
def add_product():
    form = ProductForm()
    pharmacy_id = session.get('pharmacy_id')
    if not form.validate_on_submit():
        flash("يرجى ملء جميع الحقول المطلوبة بشكل صحيح", "danger")
        return redirect(url_for('pharmacist.pharmacist_dashboard'))
    
    elif form.validate_on_submit():
        product = Product(
            name=form.name.data,
            pharmacy_id=pharmacy_id,
            quantity_in_shelf=form.quantity_in_shelf.data,
            quantity_in_stock=form.quantity_in_stock.data,
            shelf_number=form.shelf_number.data,
            purchase_price=form.purchase_price.data,
            sell_price=form.sell_price.data,
            expiry_date=form.expiry_date.data
        )
        db.session.add(product)
        db.session.commit()
        flash("تمت إضافة الدواء بنجاح", "success")
    else:
        flash("حدث خطأ في إدخال البيانات", "danger")
    
    return redirect(url_for('pharmacist.pharmacist_dashboard'))

@pharmacist_bp.route('/increase-product', methods=['POST'])
def increase_product():
    name = request.form.get('name')  # product name from form input
    qty_shelf = request.form.get('quantity_in_shelf', type=int)
    qty_stock = request.form.get('quantity_in_stock', type=int)

    pharmacy_id = session.get('pharmacy_id')

    if not name or qty_shelf is None or qty_stock is None:
        flash("يرجى إدخال اسم الدواء والكميات بشكل صحيح", "danger")
        return redirect(url_for('pharmacist.pharmacist_dashboard'))

    # Find the product by name and pharmacy_id
    product = Product.query.filter(
        db.func.lower(Product.name) == name.lower(),
        Product.pharmacy_id == pharmacy_id
    ).first()

    if not product:
        flash("الدواء غير موجود في قاعدة البيانات", "danger")
        return redirect(url_for('pharmacist.pharmacist_dashboard'))

    # Increase quantities
    product.quantity_in_shelf += qty_shelf
    product.quantity_in_stock += qty_stock

    db.session.commit()
    flash("تم تحديث الكميات بنجاح", "success")

    return redirect(url_for('pharmacist.pharmacist_dashboard'))


@pharmacist_bp.route('/search-product', methods=['POST'])
def search_product():
    name = request.form.get('name', '').strip()
    pharmacy_id = session.get('pharmacy_id')

    if not name:
        flash("يرجى إدخال اسم الدواء للبحث", "danger")
        return redirect(url_for('pharmacist.pharmacist_dashboard'))

    # Find matching products (case-insensitive, partial match)
    products = Product.query.filter(
        Product.pharmacy_id == pharmacy_id,
        Product.name.ilike(f"%{name}%")
    ).all()

    if not products:
        flash("لم يتم العثور على أي دواء بهذا الاسم", "warning")
        return redirect(url_for('pharmacist.pharmacist_dashboard'))

    return render_template(
        'pharmacist/search_results.html',
        products=products
    )


    



