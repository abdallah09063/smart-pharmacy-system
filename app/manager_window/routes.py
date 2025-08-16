from flask import render_template
#from app.utils.decorators import admin_required

from . import manager_bp

@manager_bp.route('/dashboard')
def manager_dashboard():
    return render_template('manager/dashboard.html')