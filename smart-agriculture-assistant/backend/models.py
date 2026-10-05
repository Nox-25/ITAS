from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.database import Base
from datetime import datetime

class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location_lat = Column(Float)
    location_lon = Column(Float)
    soil_type = Column(String)

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float)
    humidity = Column(Float)
    soil_moisture = Column(Float)
    soil_ph = Column(Float)
    nitrogen = Column(Float)
    phosphorus = Column(Float)
    potassium = Column(Float)
