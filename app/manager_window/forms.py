from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class PharmacistForm(FlaskForm):
    # Register Form for the pharmacist allowing managers to add pharmacists
    pharmacist_name = StringField('الإسم', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password', message='كلمة المرور غير متطابقة')])
    submit = SubmitField('تسجيل')