from . import db

def insert(row):
    db.session.add(row)
    db.session.commit()
