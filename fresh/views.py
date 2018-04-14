from flask import jsonify, render_template, redirect, request, url_for

from . import app, db
from .models import ColorData, SensorData
from .helpers import insert

from forms.data_forms import ChooseDeviceForm, ChooseStatForm
from forms.login_forms import ForgotForm, LoginForm


@app.route('/', methods=["GET", "POST"])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email
        password = form.password
        return redirect(url_for('current'))
    return render_template('index.html', form=form)

@app.route('/forgot', methods=["GET", "POST"])
def forgot():
    form = ForgotForm()
    if form.validate_on_submit():
        email = form.email
    print 'rendering forgot page'
    return render_template('forgot.html', form=form)

@app.route('/current', methods=["GET"])
def current():
    return render_template('current.html')

@app.route('/showSignal', methods=["GET", "POST"])
def showSignal():
    form = ChooseDeviceForm(request.form)
    if request.method == 'POST':
        signals = SensorData.query.filter_by(device_id=form.data['device_id']).all()
        return render_template('signal_data.html', query_results=signals, form=form)
    else:
        signals = SensorData.query.all()
        return render_template('signal_data.html', query_results=signals, form=form)

@app.route('/showColor', methods=["GET", "POST"])
def showColor():
    form = ChooseDeviceForm(request.form)
    if request.method == 'POST':
        colors = ColorData.query.filter_by(device_id=form.data['device_id']).all()
        return render_template('color_data.html', query_results=colors, form=form)
    else:
        colors = ColorData.query.all()
        return render_template('color_data.html', query_results=colors, form=form)

@app.route('/history', methods=["GET", "POST"])
def history():
    form = ChooseStatForm(request.form)
    if request.method == 'POST':
        stat = form.data['stat_type']
        return render_template('history.html', stat=stat, form=form)
    else:
        stat = "Unchosen"
        return render_template('history.html', stat=stat, form=form)

@app.route('/insertData', methods=["GET", "POST"])
def insertData():
    if not request.json:
        return "No JSON in post request\n", 403
    try:
        # Receive and parse the incoming JSON data
        packet = request.get_json(force=True)
        deviceId = int(packet['device_id'])
        temperature = float(packet['temperature'])
        humidity = float(packet['humidity'])
        pH = float(packet['pH'])
        light_comp = int(packet['light_comp'], 0)
        battery = int(packet['battery'])

        # Create a sensor data row
        sData = SensorData(device_id=deviceId, temperature=temperature, humidity=humidity, pH=pH, light_composition=light_comp, battery_level=battery)

        # Create a color data row
        red = int(packet['light_comp'][2:4], 16)
        green = int(packet['light_comp'][4:6], 16)
        blue = int(packet['light_comp'][6:8], 16)
        cData = ColorData(device_id=deviceId, red=red, green=green, blue=blue, color_hex=packet['light_comp'])
    except:
        return "Invalid field in JSON\n", 403

    try:
        # Try to instert the added data
        insert(sData)
        insert(cData)
    except:
        return "Cannot put into db\n", 403

    return "DB Insert Success\n", 201

@app.route('/getColor/<int:device_id>', methods=["GET"])
def getColor(device_id):
    color_row = ColorData.query.filter_by(device_id=device_id).order_by(ColorData.datetime.desc()).first()
    if not color_row:
        return 'Device not found', 403
    else:
        print 'DB Row:', color_row
        print 'Color:', color_row.color_hex
        return color_row.color_hex, 200
