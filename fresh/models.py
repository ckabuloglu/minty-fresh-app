from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from fresh.database import Base

class SensorData(Base):
    __tablename__ = 'sensor_data'
    signal_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, nullable=False)
    temperature = Column(Float, default=None)
    humidity = Column(Float, default=None)
    light_composition = Column(String, default=None)
    lux = Column(Integer, default=None)
    pH = Column(Float, default=None)
    battery_level = Column(Integer, default=None)
    datetime = Column(DateTime(timezone=True), nullable=False, default=func.now())

    def __repr__(self):
        return '<Data %r>' % self.signal_id

class ColorData(Base):
    __tablename__ = 'color_data'
    color_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, nullable=False)
    red = Column(Integer, default=0, nullable=False)
    green = Column(Integer, default=0, nullable=False)
    blue = Column(Integer, default=0, nullable=False)
    color_hex = Column(String, default="0x000000", nullable=False)
    by_user = Column(Boolean, default=False, nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False, default=func.now())

    def __repr__(self):
        return '<Color %r>' % self.color_id