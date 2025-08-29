from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# This file handle register and login for the manager 

class RegisterForm(FlaskForm):
    # Register Form for the manager to register the owner and the pharmacy
    manager_name = StringField('الإسم', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    pharmacy_name = StringField('إسم الصيدلية', validators=[DataRequired(), Length(min=2, max=30)])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password', message='كلمة المرور غير متطابقة')])
    submit = SubmitField('تسجيل')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')
