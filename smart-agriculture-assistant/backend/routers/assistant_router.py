from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from openai import OpenAI

from backend.database import get_db
from backend import models
from backend.weather import get_current_weather

router = APIRouter()

# Try to get API key, if not available we use fallback
api_key = os.environ.get("OPENAI_API_KEY")
client = None
if api_key:
    client = OpenAI(api_key=api_key)

class ChatRequest(BaseModel):
    farm_id: int
    message: str

def get_farm_context(farm_id: int, db: Session):
    # Fetch latest IoT reading
    reading = db.query(models.SensorReading).filter(models.SensorReading.farm_id == farm_id)\
                .order_by(models.SensorReading.timestamp.desc()).first()

    farm = db.query(models.Farm).filter(models.Farm.id == farm_id).first()

    weather_data = None
    if farm:
        lat = farm.location_lat if farm.location_lat else 20.5937
        lon = farm.location_lon if farm.location_lon else 78.9629
        weather_data = get_current_weather(lat, lon)

    context = "Farm Current Context:\n"
    if reading:
        context += f"- Soil Moisture: {reading.soil_moisture}%\n"
        context += f"- Temperature: {reading.temperature}°C\n"
        context += f"- Humidity: {reading.humidity}%\n"
        context += f"- NPK: N={reading.nitrogen}, P={reading.phosphorus}, K={reading.potassium}\n"
        context += f"- Soil pH: {reading.soil_ph}\n"
    else:
        context += "- No sensor readings available yet.\n"

    if weather_data:
        context += f"- Weather Forecast: {weather_data.get('daily_precipitation')}mm precipitation expected today.\n"

    # Calculate Risk Score
    risk_score = 0
    risk_factors = []

    if reading:
        if reading.soil_moisture < 30:
            risk_score += 25
            risk_factors.append("Low soil moisture (Drought risk)")
        if reading.temperature > 35:
            risk_score += 20
            risk_factors.append("High temperature (Heat stress risk)")

    if weather_data and weather_data.get('daily_precipitation', 0) > 50:
        risk_score += 20
        risk_factors.append("Heavy rainfall expected (Flood/Disease risk)")

    risk_score = min(risk_score, 100)

    context += f"\nRisk Score: {risk_score}/100"
    if risk_factors:
        context += "\nRisk Factors: " + ", ".join(risk_factors)

    return context, risk_score, risk_factors

@router.post("/chat")
def chat_with_assistant(req: ChatRequest, db: Session = Depends(get_db)):
    context, risk_score, risk_factors = get_farm_context(req.farm_id, db)

    system_prompt = f"""You are a Smart Agriculture Assistant.
You provide clear, expert, and actionable advice to farmers based on their current farm conditions.
Keep your answers concise and practical.

{context}
"""

    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": req.message}
                ]
            )
            return {
                "reply": response.choices[0].message.content,
                "risk_score": risk_score,
                "risk_factors": risk_factors
            }
        except Exception as e:
            # Fallback if API fails
            pass

    # Fallback rule-based logic
    msg = req.message.lower()
    reply = "I'm sorry, my AI capabilities are currently offline. However, I can still provide basic advice."

    if "irrigate" in msg or "water" in msg:
        if "Low soil moisture" in context:
            reply = f"Yes, your soil moisture is low and a drought risk is present. Irrigation is highly recommended. (Risk Score: {risk_score}/100)"
        else:
            reply = f"Your current soil moisture looks adequate. No immediate irrigation is needed unless conditions change. (Risk Score: {risk_score}/100)"
    elif "risk" in msg:
        reply = f"Your current Farm Risk Score is {risk_score}/100."
        if risk_factors:
            reply += " Pay attention to: " + ", ".join(risk_factors)

    return {
        "reply": reply,
        "risk_score": risk_score,
        "risk_factors": risk_factors
    }

@router.get("/risk-score/{farm_id}")
def get_risk_score(farm_id: int, db: Session = Depends(get_db)):
    _, risk_score, risk_factors = get_farm_context(farm_id, db)
    return {
        "risk_score": risk_score,
        "risk_factors": risk_factors
    }
