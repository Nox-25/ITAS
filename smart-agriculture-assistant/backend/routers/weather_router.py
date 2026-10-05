from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.weather import get_current_weather

router = APIRouter()

@router.get("/weather/{farm_id}")
def get_weather_for_farm(farm_id: int, db: Session = Depends(get_db)):
    farm = db.query(models.Farm).filter(models.Farm.id == farm_id).first()

    # Use default location if farm not found or no location set
    lat = farm.location_lat if farm and farm.location_lat else 20.5937
    lon = farm.location_lon if farm and farm.location_lon else 78.9629

    weather_data = get_current_weather(lat, lon)
    if not weather_data:
        raise HTTPException(status_code=500, detail="Could not fetch weather data")

    return weather_data
