from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import asyncio

from backend.database import engine, Base, get_db
from backend import models
from backend.routers import crop_router, iot_router, weather_router, irrigation_router, disease_router, yield_router, assistant_router
from backend.mqtt_subscriber import init_mqtt

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Agriculture Assistant API")

# Setup MQTT Subscriber on startup
@app.on_event("startup")
def startup_event():
    init_mqtt()

app.include_router(crop_router.router, prefix="/api", tags=["Crop Recommendation"])
app.include_router(iot_router.router, prefix="/api", tags=["IoT Monitoring"])
app.include_router(weather_router.router, prefix="/api", tags=["Weather"])
app.include_router(irrigation_router.router, prefix="/api", tags=["Irrigation"])
app.include_router(disease_router.router, prefix="/api", tags=["Disease Detection"])
app.include_router(yield_router.router, prefix="/api", tags=["Yield Prediction"])
app.include_router(assistant_router.router, prefix="/api", tags=["AI Assistant"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Agriculture Assistant API"}

@app.get("/farms")
def get_farms(db: Session = Depends(get_db)):
    return db.query(models.Farm).all()
