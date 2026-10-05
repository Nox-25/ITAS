from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pickle
import os
import numpy as np

router = APIRouter()

ML_DIR = os.path.join(os.path.dirname(__file__), "../../ml")
MODEL_PATH = os.path.join(ML_DIR, "irrigation_model.pkl")

irrigation_model = None

def load_model():
    global irrigation_model
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                irrigation_model = pickle.load(f)
    except Exception as e:
        print(f"Error loading irrigation model: {e}")

load_model()

class IrrigationInput(BaseModel):
    soil_moisture: float
    temperature: float
    humidity: float
    expected_rainfall: float

@router.post("/predict-irrigation")
def predict_irrigation(data: IrrigationInput):
    if irrigation_model is None:
        load_model()
        if irrigation_model is None:
            raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")

    input_data = np.array([[data.soil_moisture, data.temperature, data.humidity, data.expected_rainfall]])

    try:
        prob = float(irrigation_model.predict_proba(input_data)[0][1])
        prediction = int(irrigation_model.predict(input_data)[0])

        needed = prediction == 1

        # Calculate suggested amount just as a simple rule-based estimate if needed
        suggested_amount = 0
        if needed:
            # Base of 20L/m2, modified by moisture deficit
            deficit = max(0, 40 - data.soil_moisture)
            suggested_amount = round(15 + (deficit * 0.5), 1)

        return {
            "irrigation_needed": needed,
            "confidence": round(prob * 100, 2) if needed else round((1 - prob) * 100, 2),
            "suggested_amount_liters_per_sqm": suggested_amount if needed else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
