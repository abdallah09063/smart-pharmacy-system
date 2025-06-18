from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from app import models

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user = User.query.filter_by(username=identity).first()
            if not user or user.role.role != required_role:
                return jsonify({"msg": "Access denied: Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
