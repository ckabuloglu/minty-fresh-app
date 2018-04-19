import random
from datetime import datetime, timedelta

from flask import jsonify, render_template, redirect, request, url_for

import pygal

from sqlalchemy.orm import load_only

from . import app, db
from .models import ColorData, SensorData
from .helpers import insert, getDeviceIds
from forms.data_forms import ChooseDeviceForm, ChooseColorForm, ChooseStatForm
from forms.login_forms import ForgotForm, LoginForm

# Main login page
@app.route('/', methods=["GET", "POST"])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email
        password = form.password
        return redirect(url_for('current'))
    return render_template('index.html', form=form)

# Forgot Password Page
@app.route('/forgot', methods=["GET", "POST"])
def forgot():
    form = ForgotForm()
    if form.validate_on_submit():
        email = form.email
    print 'rendering forgot page'
    return render_template('forgot.html', form=form)

# Main dashboard page, shows the latest conditions as well as allowing
# the change the light composition and color of the LED panel
@app.route('/current', methods=["GET", "POST"])
def current():
    device_form = ChooseDeviceForm(request.form)
    device_form.device_id.choices = getDeviceIds(SensorData.query.all())
    color_form = ChooseColorForm()

    #  If a device is chosen from the list
    if request.method == 'POST' and "device_id" in request.form:
        device = device_form.data['device_id']
    elif request.method == 'POST' and "red" in request.form:
        device = color_form.data['device']
        red = color_form.data['red']
        green = color_form.data['green']
        blue = color_form.data['blue']

        color_hex = "0x"
        for color in [red, green, blue]:
            st = str(hex(int(color))[2:]).upper()
            if len(st) < 2:
                st = '0' + st
            color_hex = color_hex + st

        try:
            cData = ColorData(device_id=device, red=red, green=green, blue=blue, color_hex=color_hex, by_user=True)
            insert(cData)
            print "DB Insert Succesful"
        except:
            return "Cannot put into DB\n", 403

    # If no data or whatsoever is present, initiate by adding 1 row to each table with dummy variable
    elif len(SensorData.query.all()) == 0:
        sData = SensorData(device_id=1, temperature=78, humidity=50, pH=7, light_composition="0xFF00FF", lux=2500, battery_level=100)
        cData = ColorData(device_id=1, red=255, green=0, blue=255, color_hex="0xFF00FF", by_user=True)
        insert(sData)
        insert(cData)
        device = 1
    else:
        device = 1      # Default device id is 1
        
    sensor_row = SensorData.query.filter_by(device_id=device).order_by(SensorData.datetime.desc()).first()

    color_row = ColorData.query.filter_by(device_id=device).order_by(ColorData.datetime.desc()).first()
    color_form.red.default = color_row.red
    color_form.green.default = color_row.green
    color_form.blue.default = color_row.blue
    color_form.color_hex.default = '#' + color_row.color_hex[2:]

    return render_template('current.html', row=sensor_row, form=device_form, color_form=color_form)

# Shows database rows of the signal table
@app.route('/showSensor', methods=["GET", "POST"])
def showSensor():
    form = ChooseDeviceForm(request.form)
    form.device_id.choices = getDeviceIds(SensorData.query.all())
    if request.method == 'POST':
        signals = SensorData.query.filter_by(device_id=form.data['device_id']).all()
    else:
        signals = SensorData.query.all()
    return render_template('sensor_data.html', query_results=signals, form=form)

# Shows the database rows of the color table
@app.route('/showColor', methods=["GET", "POST"])
def showColor():
    form = ChooseDeviceForm(request.form, coerce=int)
    form.device_id.choices = getDeviceIds(ColorData.query.all())
    if request.method == 'POST':
        colors = ColorData.query.filter_by(device_id=form.data['device_id']).all()
    else:
        colors = ColorData.query.all()
    return render_template('color_data.html', query_results=colors, form=form)

# Shows the graphs (Work in Progress) of past data
@app.route('/history', methods=["GET", "POST"])
def history():
    form = ChooseStatForm(request.form, coerce=int)
    form.device_id.choices = getDeviceIds(SensorData.query.all())

    if request.method == 'POST':
        stat = form.data['stat_type']
        device = form.data['device_id']
    else:
        stat = "temperature"           # Default is Temperature
        device = 1

    stat_data = SensorData.query.filter_by(device_id=device).options(load_only(stat))
    
    rows = []
    for row in stat_data:
        rows.append((row.datetime, getattr(row, stat)))

    statRanges = {'temperature':(32, 100), 
                  'humidity':(0, 100), 
                  'pH':(0, 14), 
                  'battery_level':(0, 105),
                  'lux':(0, 10000) }

    statTitles = {'temperature': "Water Temperature (C)", 
                  'humidity': "Humidity (%)", 
                  'pH': "pH", 
                  'battery_level': "Battery Level (%)",
                  'lux': "Lux (lum / m^2) "}

    # Create the chart
    title = '%s for device %s' % (stat, device)
    chart = pygal.Line(width=1000, height=500,
                          explicit_size=True, title=title,
                          range=statRanges[stat],
                          show_dots=False,
                          disable_xml_declaration=True)
    chart.x_labels = [row[0] for row in rows]
    chart.add(statTitles[stat], [row[1] for row in rows])

    return render_template('history.html', stat=stat, form=form, rows=rows, chart=chart)

# Allows the POST requests to be made by the client device
@app.route('/insertData', methods=["GET", "POST"])
def insertData():
    if not request.json:
        return "No JSON in post request\n", 403
    try:
        # Receive and parse the incoming JSON data
        packet = request.get_json(force=True)
        device = int(packet['device_id'])
        temperature = float(packet['temperature'])
        humidity = float(packet['humidity'])
        pH = float(packet['pH'])
        battery = 97

        redData = int(packet['red'], 16)
        greenData= int(packet['green'], 16)
        blueData = int(packet['blue'], 16)

        print "Data received"
        redLux = (redData / 100.0) * 260
        greenLux = (greenData / 100.0) * 679
        blueLux = (blueData / 100.0) * 94

        print "Converted to lux"
        maxLux = max([redLux, greenLux, blueLux])
        totalLux = redLux + greenLux + blueLux

        print "TMax:", maxLux
        print redLux, greenLux, blueLux

        redHex = hex(int((redLux / maxLux) * 255))[2:]
        greenHex = hex(int((greenLux / maxLux) * 255))[2:]
        blueHex = hex(int((blueLux / maxLux) * 255))[2:]

        if len(redHex) < 2:
            redHex = '0' + redHex

        if len(greenHex) < 2:
            greenHex = '0' + greenHex

        if len(blueHex) < 2:
            blueHex = '0' + blueHex

        print "Generated the hex", redHex, greenHex, blueHex

        light_comp = '0x' + redHex.upper() + greenHex.upper() + blueHex.upper()

        # Create a sensor data row
        sData = SensorData(device_id=device, temperature=temperature, humidity=humidity, pH=pH, light_composition=light_comp, lux=totalLux, battery_level=battery)
        cData = None

        print cData
        c = ColorData.query.filter_by(device_id=device).all()
        print c
        print len(c)
        
        if len(c) == 0:
            # Create a color data row
            red = int(redHex, 16)
            green = int(greenHex, 16)
            blue = int(blueHex, 16)
            print red, green, blue
            cData = ColorData(device_id=device, red=red, green=green, blue=blue, color_hex=light_comp)

    except:
        return "Invalid field in JSON\n", 403
    try:
        # Try to instert the added data
        insert(sData)
        if cData:
            insert(cData)
    except:
        return "Cannot put into DB\n", 403

    color_row = ColorData.query.filter_by(device_id=device).order_by(ColorData.datetime.desc()).first()
    return color_row.color_hex, 201



#  ----- NON RENDERING PAGES ------ #
#  either are used for administrative purposes or used by the device (greenhouse unit)



# Allows the client device to inquire the latest color setting, either edited by the user or posted by the device
@app.route('/getColor/<int:device_id>', methods=["GET"])
def getColor(device_id):
    color_row = ColorData.query.filter_by(device_id=device_id).order_by(ColorData.datetime.desc()).first()
    if not color_row:
        return 'Device not found', 403
    else:
        return color_row.color_hex, 201

@app.route('/randomData/<int:device_id>', methods=["GET"])
def randomData(device_id):
    today = datetime.today()
    weekAgo = today - timedelta(days=7)
    timeInst = weekAgo
    d = timedelta(minutes=15)
    battery = 100
    light_comp = "0x1A1A1A"

    while timeInst < today:
        if timeInst.hour > 9 and timeInst.hour < 17:
            temperature = (random.randint(0, 40) + 40)
            humidity = (random.randint(0, 30) + 35)
            pH = (random.randint(0, 50) + 50) / 10
            battery = 100 - 3 * random.random()
        else:
            temperature = (random.randint(0, 20) + 50)
            humidity = (random.randint(0, 30) + 35)
            pH = (random.randint(0, 50) + 50) / 10
            battery = battery - 1.3 * random.random()
        
        sData = SensorData(device_id=device_id,
                temperature=temperature,
                humidity=humidity,
                pH=pH,
                light_composition=light_comp,
                battery_level=int(battery),
                datetime=timeInst
        )

        db.session.add(sData)
        timeInst = timeInst + d
    
    db.session.commit()

    responseStr = "Data created for device: " + str(device_id)
    return responseStr, 201

