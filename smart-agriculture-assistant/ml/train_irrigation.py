import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pickle

def train_and_save_model():
    print("Generating synthetic dataset for irrigation (Decision Support Prototype)...")

    # We create a synthetic dataset since a perfect public one for these exact parameters is rare
    # Rule of thumb: If moisture is low, temp is high, and rain is low -> Irrigate
    np.random.seed(42)
    n_samples = 1000

    soil_moisture = np.random.uniform(10, 80, n_samples)
    temperature = np.random.uniform(15, 45, n_samples)
    humidity = np.random.uniform(20, 90, n_samples)
    expected_rainfall = np.random.uniform(0, 50, n_samples)

    # Simple logic to determine if irrigation is needed (1: Yes, 0: No)
    labels = []
    for i in range(n_samples):
        score = 0
        if soil_moisture[i] < 35: score += 2
        if soil_moisture[i] < 25: score += 2
        if temperature[i] > 30: score += 1
        if expected_rainfall[i] < 10: score += 1

        # If score > 3, irrigate
        labels.append(1 if score >= 3 else 0)

    df = pd.DataFrame({
        'soil_moisture': soil_moisture,
        'temperature': temperature,
        'humidity': humidity,
        'expected_rainfall': expected_rainfall,
        'irrigate': labels
    })

    data_path = os.path.join(os.path.dirname(__file__), "../data/irrigation_data.csv")
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    df.to_csv(data_path, index=False)

    X = df[['soil_moisture', 'temperature', 'humidity', 'expected_rainfall']]
    y = df['irrigate']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    rf_model = RandomForestClassifier(n_estimators=50, random_state=42)
    rf_model.fit(X_train, y_train)

    preds = rf_model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Irrigation Model Accuracy: {acc:.4f}")

    model_path = os.path.join(os.path.dirname(__file__), "irrigation_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(rf_model, f)

    print(f"Irrigation model saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()
