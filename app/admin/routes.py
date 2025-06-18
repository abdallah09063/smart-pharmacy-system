from flask import render_template, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import role_required


from . import admin_bp

@admin_bp.route('/dashboard')
@jwt_required()
@role_required('Admin')  #***
def admin_dashboard():
    current_admin = get_jwt_identity()
    return jsonfy({"massage" : "welcome to dashboard"})