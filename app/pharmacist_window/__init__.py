from flask import Blueprint

pharmacist_bp = Blueprint('pharmacist', __name__)

from . import routes