from flask import jsonify, render_template, redirect, request, url_for

from . import app, db
from .models import SensorData
from .helpers import insert

t1 = {"device_id":"3", "temperature":"76.5", "humidity":"4.5", "pH":"7.4", "light_comp":"0xFF45AA",  "battery":"4"}

@app.route('/', methods=["GET"])
def mainpage():
    return render_template('home.html')

@app.route('/showData', methods=["GET"])
def showData():
    signals = SensorData.query.all()
    return render_template('data.html', query_results=signals)
''
@app.route('/insertData', methods=["GET", "POST"])
def insertData():
    if not request.json:
        return "No JSON in post request\n", 403
    try:
        packet = request.json
        deviceId = packet['device_id']
        temperature = float(packet['temperature'])
        humidity = float(packet['humidity'])
        pH = float(packet['pH'])
        light_comp = int(packet['light_comp'], 0)
        battery = int(packet['battery'])

        sData = SensorData(device_id=deviceId, temperature=temperature, humidity=humidity, pH=pH, light_composition=light_comp, battery_level=battery)
        print "ID:", sData.signal_id
    except:
        return "Invalid field in JSON\n", 403

    try:
        insert(sData)
    except:
        return "Cannot put into db\n", 403

    return "DB Insert Success\n", 201
