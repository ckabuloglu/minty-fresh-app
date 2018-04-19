from datetime import datetime
import random

from . import db

def insert(row):
    db.session.add(row)
    db.session.commit()

def getDeviceIds(rows):
    idSet = set()
    ids = []
    for row in rows:
        if row.device_id not in idSet:
            ids.append((row.device_id, str(row.device_id)))
            idSet.add(row.device_id)

    return sorted(ids)

def getBatteryLevel(dt):
    battery_level = 0
    h = dt.hour
    m = dt.minute
    noise = (random.random() * 4.0) - 2.0

    if h < 6:
        base_level = 56
        power = ((h * 60 + m) / 359) * 5.17
        battery_level = base_level - pow(2, power) + noise
    elif h < 14:
        base_level = 19
        power = (((h - 6) * 60 + m) / 479) * 6.32
        battery_level = base_level + pow(2, power) + noise
    elif h < 18:
        base_level = 98
        battery_level = base_level + noise
    elif h < 20:
        base_level = 98
        power = (((h - 18) * 60 + m) / 119) * 4.32
        battery_level = base_level - pow(2, power) + noise
    else:
        base_level = 80
        power = (((h - 20) * 60 + m) / 239) * 4.58
        battery_level = base_level - pow(2, power) + noise

    return int(battery_level)
