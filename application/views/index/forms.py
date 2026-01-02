from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddItemForm(FlaskForm):
    weapon = StringField('Weapon', validators=[DataRequired()])
    skin = StringField('Skin', validators=[DataRequired()])
    paint_index = IntegerField('Paint Index', validators=[DataRequired()])
    submit = SubmitField('Add Item')
