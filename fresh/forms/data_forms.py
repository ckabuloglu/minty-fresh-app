from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired, Email

from ..models import SensorData


class ChooseDeviceForm(FlaskForm):
    device_id = SelectField('device_id')

class ChooseStatForm(FlaskForm):
    stat_type = SelectField('stat_type', choices=[('temperature', 'Temperature'),
            ('humidity', 'Humidity'),
            ('pH', 'pH'),
            ('light_composition', 'Light Composition'),
            ('battery_level', 'Battery Level')])