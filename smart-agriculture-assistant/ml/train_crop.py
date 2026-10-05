import pandas as pd
import numpy as np
import os
import urllib.request
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle
from sklearn.preprocessing import LabelEncoder

def train_and_save_model():
    # URL for Crop Recommendation dataset (NPK, temp, humidity, ph, rainfall)
    url = "https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv"
    data_path = os.path.join(os.path.dirname(__file__), "../data/crop_recommendation.csv")

    # Create data directory if not exists
    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    print("Downloading dataset...")
    try:
        urllib.request.urlretrieve(url, data_path)
    except Exception as e:
        print(f"Failed to download from main URL. Error: {e}")
        # fallback to a synthetic generation just in case download fails
        print("Generating synthetic data as fallback...")
        generate_synthetic_crop_data(data_path)

    print("Loading dataset...")
    df = pd.read_csv(data_path)

    # Features and Target
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']

    # Label Encoding for XGBoost
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    print(f"Random Forest Accuracy: {accuracy_score(y_test, rf_preds):.4f}")

    print("Training XGBoost...")
    xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    print(f"XGBoost Accuracy: {accuracy_score(y_test, xgb_preds):.4f}")

    # We will use Random Forest as it generally works well without much tuning for this dataset
    best_model = rf_model if accuracy_score(y_test, rf_preds) >= accuracy_score(y_test, xgb_preds) else xgb_model

    # Save model and label encoder
    model_path = os.path.join(os.path.dirname(__file__), "crop_model.pkl")
    encoder_path = os.path.join(os.path.dirname(__file__), "label_encoder.pkl")

    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)

    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)

    print(f"Model saved to {model_path}")

def generate_synthetic_crop_data(path):
    np.random.seed(42)
    crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
             'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
             'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple',
             'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']

    data = []
    for crop in crops:
        for _ in range(100):
            data.append({
                'N': np.random.uniform(0, 140),
                'P': np.random.uniform(5, 145),
                'K': np.random.uniform(5, 205),
                'temperature': np.random.uniform(8, 43),
                'humidity': np.random.uniform(14, 100),
                'ph': np.random.uniform(3.5, 9.9),
                'rainfall': np.random.uniform(20, 298),
                'label': crop
            })
    pd.DataFrame(data).to_csv(path, index=False)

if __name__ == "__main__":
    train_and_save_model()
