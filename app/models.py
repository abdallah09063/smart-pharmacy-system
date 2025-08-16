from app import db
from datetime import datetime, date, timezone

# ==============================
# Manager, Pharmacy
# ==============================

class Pharmacy(db.Model):
    __tablename__ = 'pharmacy'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

class Manager(db.Model):
    __tablename__ = 'manager'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    pharmacy = db.relationship('Pharmacy', backref='manager')


# ==============================
# Pharmacist, LoginActivity, Report
# ==============================

class Pharmacist(db.Model):
    __tablename__ = 'pharmacist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    pharmacy = db.relationship('Pharmacy', backref='pharmacists')

class LoginActivity(db.Model):
    __tablename__ = 'login_activity'
    id = db.Column(db.Integer, primary_key=True)
    pharmacist_id = db.Column(db.Integer, db.ForeignKey('pharmacist.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    logout_time = db.Column(db.DateTime)

    pharmacist = db.relationship('Pharmacist', backref='login_activities')

class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    generated_by = db.Column(db.Integer, db.ForeignKey('pharmacist.id'), nullable=False)
    report_date = db.Column(db.Date, default=date.today)
    total_sales = db.Column(db.Numeric(10, 2))
    most_sold_product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    generator = db.relationship('Pharmacist', foreign_keys=[generated_by])
    most_sold_product = db.relationship('Product', foreign_keys=[most_sold_product_id])

# ===========================
# Product, Sale, SaleItem
# ===========================

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacy.id'), nullable=False)
    quantity_in_shelf = db.Column(db.Integer, nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    shelf_number = db.Column(db.Integer, nullable=True)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    sell_price = db.Column(db.Numeric(10, 2), nullable=False)
    expiry_date = db.Column(db.Date)

    pharmacy = db.relationship('Pharmacy', backref='products')

class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.Integer, primary_key=True)
    pharmacist_id = db.Column(db.Integer, db.ForeignKey('pharmacist.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    pharmacist = db.relationship('Pharmacist', backref='sales')

class SaleItem(db.Model):
    __tablename__ = 'sale_item'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal_price = db.Column(db.Numeric(10, 2), nullable=False)

    sale = db.relationship('Sale', backref='items')
    product = db.relationship('Product')