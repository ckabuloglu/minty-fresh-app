from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import DataRequired, Email

from ..models import SensorData


class ChooseDeviceForm(FlaskForm):
    device_id = SelectField('device_id')

class ChooseStatForm(FlaskForm):
    device_id = SelectField('device_id')
    stat_type = SelectField('stat_type', choices=[('temperature', 'Temperature'),
            ('humidity', 'Humidity'),
            ('pH', 'pH'),
            ('battery_level', 'Battery Level'),
            ('lux', 'Lux')])

class ChooseColorForm(FlaskForm):
    red = DecimalRangeField('Red', default=0)
    green = DecimalRangeField('Green', default=0)
    blue = DecimalRangeField('Blue', default=0)
    color_hex = StringField('color_hex')
    device = HiddenField('device')
