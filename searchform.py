from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import Required
from wtforms_components import DateField, SelectField
from datetime import datetime, timedelta
import os

class SearchForm(FlaskForm):
    week_ago = datetime.today() - timedelta(days=7)

    start_date = DateField(label="Start Date", default=week_ago, validators=[Required])
    end_date = DateField(label="End Date", default=datetime.today, validators=[Required])
    user_name = StringField("User Name/Email Address")
    last_name = StringField("Last Name")
    org = SelectField("Organization", coerce=int)
    submit = SubmitField('Submit')
    csrf_token = HiddenField(default=os.environ.get("SECRET_KEY"))
