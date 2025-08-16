from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    jwt.init_app(app)

    from app.auth import auth_bp
    from app.manager_window import manager_bp
    from app.pharmacist_window import pharmacist_bp


    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(pharmacist_bp, url_prefix='/pharmacist')

    return app