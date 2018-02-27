from . import db

def insert(sensordata):
    db.session.add(sensordata)
    db.session.commit()

