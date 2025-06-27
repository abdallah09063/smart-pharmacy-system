from flask import render_template

from . import pharmacist_bp

@pharmacist_bp.route('/')
#@jwt_required()
def pharmacist_dashboard():
    return render_template('pharmacist/dashboard.html')