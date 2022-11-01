from flask_wtf import FlaskForm
from wtforms import StringField, URLField, SubmitField
from wtforms.validators import DataRequired


class SheetyEndPointForm(FlaskForm):
    end_point = URLField('End Point URL', validators=[DataRequired()])
    auth_token = StringField('Sheety Authorisation', validators=[DataRequired()])
    submit = SubmitField('Update')


class CategoryURLForm(FlaskForm):
    brand = StringField('Brand', validators=[DataRequired()])
    locale = StringField('Locale', validators=[DataRequired()])
    currency = StringField('Currency', validators=[DataRequired()])
    URL = URLField('URL', validators=[DataRequired()])
    submit = SubmitField('Submit')



