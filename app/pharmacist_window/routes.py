from flask import render_template, redirect, url_for, flash, request,session, jsonify
from app import db
from app.models import Product, Sale, SaleItem
from sqlalchemy import func
from app.pharmacist_window.forms import ProductForm
from datetime import datetime, date
from . import pharmacist_bp

@pharmacist_bp.route('/') 
def pharmacist_dashboard():
    pharmacy_id = session.get('pharmacy_id')
    product_count = db.session.query(func.count(func.distinct(Product.name))).scalar()
    today_sales = ( db.session.query(func.sum(SaleItem.quantity_sold))
                    .join(Sale, SaleItem.sale_id == Sale.id)
                    .filter(func.date(Sale.created_at) == date.today())
                    .scalar() 
                    ) or 0
    expired_products = ( db.session.query(func.count(Product.id))
                        .filter(Product.expiry_date < date.today())
                        .scalar()
                        ) or 0 
    few_products = Product.query.filter(Product.pharmacy_id == pharmacy_id,
                                        Product.quantity_in_shelf < 10 
                                     ).all()
    return render_template('pharmacist/dashboard.html', product_count=product_count, today_sales=today_sales, expired_products=expired_products, 
                           few_products=few_products,
                           form=ProductForm())

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
        Product.pharmacy_id == pharmacy_id,
        db.func.lower(Product.name) == name.lower()
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

    products_list = [p.name for p in products]

    if not products:
        flash("لم يتم العثور على أي دواء بهذا الاسم", "warning")
        return redirect(url_for('pharmacist.pharmacist_dashboard'))

    return render_template(
        'pharmacist/search_results.html',
        products=products,
        products_list=products_list
    )

@pharmacist_bp.route('/product-suggestions')
def product_suggestions():
    query = request.args.get("query", "").strip()
    pharmacy_id = session.get("pharmacy_id")

    if not query:
        return jsonify([])

    products = Product.query.filter(
        Product.pharmacy_id == pharmacy_id,
        Product.name.ilike(f"%{query}%")
    ).limit(5).all()  # نجيب فقط 5 اقتراحات

    return jsonify([p.name for p in products])


@pharmacist_bp.route('/veiw-all-products', methods=['GET'])
def veiw_all_products():
    pharmacy_id = session.get('pharmacy_id')
    products = Product.query.filter(
        Product.pharmacy_id == pharmacy_id
    ).all()
    return render_template(
        'pharmacist/all_products.html',
        products=products
    )
    

@pharmacist_bp.route('/sell-product', methods=['POST'])
def sell_product():
    names = request.form.getlist('productName[]')
    quantities = request.form.getlist('productQty[]')
    pharmacy_id = session.get('pharmacy_id')
    pharmacist_id = session.get('pharmacist_id')

    if not names or not quantities or len(names) != len(quantities):
        flash("يرجى إدخال أسماء المنتجات والكميات بشكل صحيح", "danger")
        return redirect(url_for('pharmacist.pharmacist_dashboard'))

    total_price = 0
    products_to_update = []
    sale_items_data = []

    # Validate and prepare data
    for name, qty in zip(names, quantities):
        try:
            quantity = int(qty)
        except ValueError:
            flash(f"الكمية للدواء {name} غير صحيحة", "danger")
            return redirect(url_for('pharmacist.pharmacist_dashboard'))

        if quantity <= 0:
            flash(f"الكمية للدواء {name} يجب أن تكون أكبر من 0", "danger")
            return redirect(url_for('pharmacist.pharmacist_dashboard'))

        product = Product.query.filter(
            Product.pharmacy_id == pharmacy_id,
            db.func.lower(Product.name) == name.lower()
        ).first()

        if not product:
            flash(f"الدواء {name} غير موجود في قاعدة البيانات", "danger")
            return redirect(url_for('pharmacist.pharmacist_dashboard'))

        if product.quantity_in_shelf < quantity:
            flash(f"الكمية المطلوبة من {name} غير متوفرة في الرف الرجاء مراجعة المخزن", "danger")
            return redirect(url_for('pharmacist.pharmacist_dashboard'))

        # Update total price and prepare stock update
        total_price += product.sell_price * quantity
        products_to_update.append((product, quantity))
        sale_items_data.append({'product': product, 'quantity': quantity})

    # Update stock in one transaction
    for product, quantity in products_to_update:
        product.quantity_in_shelf -= quantity

    # Create sale record
    sale = Sale(
        pharmacist_id=pharmacist_id,
        total_price=total_price,
        created_at=datetime.now()
    )
    db.session.add(sale)
    db.session.flush()  # Get sale.id without committing yet

    # Create sale items
    for item in sale_items_data:
        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=item['product'].id,
            quantity_sold=item['quantity'],
            unit_price=item['product'].sell_price,
            subtotal_price=item['product'].sell_price * item['quantity']
        )
        db.session.add(sale_item)

    db.session.commit()  # Commit everything once
    flash("تم بيع الأدوية بنجاح", "success")
    return redirect(url_for('pharmacist.pharmacist_dashboard'))


@pharmacist_bp.route('/today-sales', methods=['POST', "GET"])
def today_sales():
    pharmacist_id = session.get('pharmacist_id')

    sales = Sale.query.filter(
        Sale.pharmacist_id == pharmacist_id,
        func.date(Sale.created_at) == date.today()
    ).all()

    return render_template('/pharmacist/today_sales.html', sales=sales)


@pharmacist_bp.route('/today-sales/<int:id>', methods=['POST', 'GET'])
def sale_detail(id):
    sale = Sale.query.get_or_404(id)
    sold_items = sale.items

    return render_template('/pharmacist/sold_items.html', sold_items=sold_items)


