from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, DateField
from wtforms.validators import DataRequired, NumberRange

class ProductForm(FlaskForm):
    name = StringField('اسم الدواء', validators=[DataRequired()])
    quantity_in_shelf = IntegerField('الكمية على الرف', validators=[DataRequired(), NumberRange(min=0)])
    quantity_in_stock = IntegerField('الكمية في المخزون', validators=[DataRequired(), NumberRange(min=0)])
    shelf_number = IntegerField('رقم الرف')
    purchase_price = DecimalField('سعر الشراء', validators=[DataRequired()])
    sell_price = DecimalField('سعر البيع', validators=[DataRequired()])
    expiry_date = DateField('تاريخ الانتهاء', validators=[DataRequired()])