from flask import render_template, redirect, url_for, flash, request, make_response, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app import csrf
from app import db, create_app
from app.auth import auth_bp
from app.models import Manager, LoginActivity, Pharmacy, Pharmacist
from app.auth.forms import LoginForm, RegisterForm

app = create_app()

with app.app_context():
    hashed_password = generate_password_hash("666666")
    new_pharmacist = Pharmacist(
        name="Hassan",
        email="hassan@example.com",
        password_hash=hashed_password,
        pharmacy_id=2,
        created_at=datetime.now(timezone.utc)
    )
    db.session.add(new_pharmacist)
    db.session.commit()
    print("Pharmacist added successfully!")

