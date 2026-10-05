from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pickle
import os
import numpy as np

router = APIRouter()

ML_DIR = os.path.join(os.path.dirname(__file__), "../../ml")
MODEL_PATH = os.path.join(ML_DIR, "yield_model.pkl")

yield_model = None

def load_model():
    global yield_model
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                yield_model = pickle.load(f)
    except Exception as e:
        print(f"Error loading yield model: {e}")

load_model()

class YieldInput(BaseModel):
    rainfall: float
    temperature: float
    fertilizer: float

@router.post("/predict-yield")
def predict_yield(data: YieldInput):
    if yield_model is None:
        load_model()
        if yield_model is None:
            raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")

    input_data = np.array([[data.rainfall, data.temperature, data.fertilizer]])

    try:
        predicted_yield = yield_model.predict(input_data)[0]

        return {
            "predicted_yield_tonnes_per_hectare": round(float(predicted_yield), 2),
            "expected_range_min": round(float(predicted_yield) - 0.5, 2),
            "expected_range_max": round(float(predicted_yield) + 0.5, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
