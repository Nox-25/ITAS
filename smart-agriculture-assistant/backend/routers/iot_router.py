from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models
import datetime

router = APIRouter()

@router.get("/sensors/latest/{farm_id}")
def get_latest_readings(farm_id: int, limit: int = 10, db: Session = Depends(get_db)):
    readings = db.query(models.SensorReading)\
                 .filter(models.SensorReading.farm_id == farm_id)\
                 .order_by(models.SensorReading.timestamp.desc())\
                 .limit(limit)\
                 .all()

    # Reverse to make them chronological
    return list(reversed(readings))

@router.get("/sensors/current/{farm_id}")
def get_current_reading(farm_id: int, db: Session = Depends(get_db)):
    reading = db.query(models.SensorReading)\
                .filter(models.SensorReading.farm_id == farm_id)\
                .order_by(models.SensorReading.timestamp.desc())\
                .first()
    return reading
