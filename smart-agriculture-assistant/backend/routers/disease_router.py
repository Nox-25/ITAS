from fastapi import APIRouter, UploadFile, File, HTTPException
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import os
import sys

# Add vision module to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from vision.disease_model import DiseaseDetectionModel, get_disease_classes

router = APIRouter()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../vision/disease_model.pth")
classes = get_disease_classes()
model = None

def load_model():
    global model
    try:
        if os.path.exists(MODEL_PATH):
            model = DiseaseDetectionModel(num_classes=len(classes))
            model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
            model.eval()
    except Exception as e:
        print(f"Error loading disease model: {e}")

load_model()

def transform_image(image_bytes):
    try:
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return transform(image).unsqueeze(0)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image format")

@router.post("/detect-disease")
async def detect_disease(file: UploadFile = File(...)):
    if model is None:
        load_model()
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded. Please ensure the disease model exists.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    try:
        image_bytes = await file.read()
        tensor = transform_image(image_bytes)

        with torch.no_grad():
            outputs = model(tensor)
            # Add softmax to get pseudo-probabilities (this is a mock model, so results will be random-ish)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

        top_prob, top_class_idx = torch.max(probabilities, 0)
        class_idx = top_class_idx.item()
        confidence = top_prob.item() * 100

        predicted_class = classes[class_idx]
        parts = predicted_class.split("___")
        crop = parts[0]
        disease = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"

        return {
            "crop": crop,
            "disease": disease,
            "confidence": round(confidence, 2),
            "is_healthy": "healthy" in disease.lower()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
