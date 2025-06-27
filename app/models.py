from app import db
from datetime import datetime

# ==============================
# Users, Roles and LoginActivity
# ==============================

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), unique=True, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship('Role', backref='users')


class LoginActivity(db.Model):
    __tablename__ = 'login_activity'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime)

    user = db.relationship('User', backref='login_activities')

# ===========================
# Drugs
# ===========================

class Drug(db.Model):
    __tablename__ = 'drugs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity_in_shelf = db.Column(db.Integer, nullable=False)
    quantity_in_stock = db.Column(db.Integer, nullable=False)
    shelf_number = db.Column(db.Integer, nullable=True)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    sell_price = db.Column(db.Numeric(10, 2), nullable=False)
    expiry_date = db.Column(db.Date)

# ===========================
# Sales and Sale Items
# ===========================

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    pharmacist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    pharmacist = db.relationship('User', backref='sales')

class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal_price = db.Column(db.Numeric(10, 2), nullable=False)

    sale = db.relationship('Sale', backref='items')
    drug = db.relationship('Drug')

# ===========================
# Reports
# ===========================

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_date = db.Column(db.Date, default=datetime.utcnow().date)
    total_sales = db.Column(db.Numeric(10, 2))
    most_sold_drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'))

    generator = db.relationship('User')
    most_sold_drug = db.relationship('Drug', foreign_keys=[most_sold_drug_id])

# ===========================
# Symptoms and Recommendations
# ===========================

class Symptom(db.Model):
    __tablename__ = 'symptoms'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)

class DrugRecommendation(db.Model):
    __tablename__ = 'drug_recommendations'
    id = db.Column(db.Integer, primary_key=True)
    symptom_id = db.Column(db.Integer, db.ForeignKey('symptoms.id'), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    confidence_score = db.Column(db.Numeric(5, 2))

    symptom = db.relationship('Symptom')
    drug = db.relationship('Drug')