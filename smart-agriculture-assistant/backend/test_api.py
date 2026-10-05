from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Smart Agriculture Assistant API"}

def test_crop_recommendation():
    data = {
        "N": 90, "P": 42, "K": 43,
        "temperature": 20.8, "humidity": 82.0,
        "ph": 6.5, "rainfall": 202.9
    }
    response = client.post("/api/recommend-crop", json=data)
    assert response.status_code == 200
    assert "recommendation" in response.json()

def test_yield_prediction():
    data = {
        "rainfall": 300,
        "temperature": 25,
        "fertilizer": 60
    }
    response = client.post("/api/predict-yield", json=data)
    assert response.status_code == 200
    assert "predicted_yield_tonnes_per_hectare" in response.json()
