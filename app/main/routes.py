from flask import render_template, jsonify
from flask_jwt_extended import jwt_required

from . import main_bp

@main_bp.route('/')
@jwt_required()
def home():
    return jsonfy({"massage" : "welcome to the smart pharmacy system"})