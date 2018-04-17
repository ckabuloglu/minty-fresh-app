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
