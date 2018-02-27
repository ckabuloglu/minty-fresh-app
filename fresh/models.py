from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from fresh.database import Base

class SensorData(Base):
    __tablename__ = 'sensor_data'
    signal_id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, nullable=False)
    temperature = Column(Float, default=None)
    humidity = Column(Float, default=None)
    light_composition = Column(Integer, default=None)
    pH = Column(Float, default=None)
    battery_level = Column(Integer, default=None)
    datetime = Column(DateTime(timezone=True), nullable=False, default=func.now())

    def __repr__(self):
        return '<Data %r>' % self.signal_id