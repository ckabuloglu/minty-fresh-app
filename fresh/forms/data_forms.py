from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired, Email

from ..models import SensorData

def updateDeviceIdList(updated_before=True):
    query = SensorData.query.distinct()
    idSet = set()
    ids = []
    for row in query:
        if row.device_id not in idSet:
            ids.append((row.device_id, str(row.device_id)))
            idSet.add(row.device_id)

    if updated_before:
        ChooseDeviceForm.device_id.choices=ids
    else:
        return ids

class ChooseDeviceForm(FlaskForm):
    device_id = SelectField('device_id', choices=updateDeviceIdList(updated_before=False))

class ChooseStatForm(FlaskForm):
    stat_type = SelectField('stat_type', choices=[('temperature', 'Temperature'),
            ('humidity', 'Humidity'),
            ('pH', 'pH'),
            ('light_composition', 'Light Composition'),
            ('battery_level', 'Battery Level')])