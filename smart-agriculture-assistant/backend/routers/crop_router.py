from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pickle
import os
import numpy as np

router = APIRouter()

# Load models
ML_DIR = os.path.join(os.path.dirname(__file__), "../../ml")
MODEL_PATH = os.path.join(ML_DIR, "crop_model.pkl")
ENCODER_PATH = os.path.join(ML_DIR, "label_encoder.pkl")

# Initialize models as None
crop_model = None
label_encoder = None

def load_models():
    global crop_model, label_encoder
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
            with open(MODEL_PATH, 'rb') as f:
                crop_model = pickle.load(f)
            with open(ENCODER_PATH, 'rb') as f:
                label_encoder = pickle.load(f)
    except Exception as e:
        print(f"Error loading models: {e}")

load_models()

class CropInput(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

@router.post("/recommend-crop")
def recommend_crop(data: CropInput):
    if crop_model is None or label_encoder is None:
        # Try loading again
        load_models()
        if crop_model is None or label_encoder is None:
            raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")

    input_data = np.array([[data.N, data.P, data.K, data.temperature, data.humidity, data.ph, data.rainfall]])

    try:
        # Check if the model has predict_proba
        if hasattr(crop_model, "predict_proba"):
            probs = crop_model.predict_proba(input_data)[0]
            # Get top 3 predictions
            top_3_indices = np.argsort(probs)[-3:][::-1]

            recommendations = []
            for idx in top_3_indices:
                crop_name = label_encoder.inverse_transform([idx])[0]
                confidence = float(probs[idx])
                recommendations.append({"crop": crop_name, "confidence": round(confidence * 100, 2)})

            return {
                "recommendation": recommendations[0]["crop"],
                "confidence": recommendations[0]["confidence"],
                "top_3": recommendations
            }
        else:
            # Fallback for models without predict_proba
            prediction_idx = crop_model.predict(input_data)[0]
            crop_name = label_encoder.inverse_transform([prediction_idx])[0]
            return {
                "recommendation": crop_name,
                "top_3": [{"crop": crop_name, "confidence": 100.0}]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
