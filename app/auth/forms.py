from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[
        DataRequired(), Length(min=3, max=25)
    ])
    email = StringField('البريد الإلكتروني', validators=[
        DataRequired(), Email()
    ])
    role = SelectField('الدور', choices=[
        ('admin', 'مسؤول'),
        ('pharmacist', 'صيدلاني')
    ], validators=[DataRequired()
    ])
    password = PasswordField('كلمة المرور', validators=[
        DataRequired(), Length(min=6)
    ])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[
        DataRequired(), EqualTo('password', message='كلمة المرور غير متطابقة')
    ])
    submit = SubmitField('تسجيل')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')
