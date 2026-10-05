import torch
import os
from disease_model import DiseaseDetectionModel

def create_transfer_learning_model():
    print("Creating a Pre-trained Transfer Learning model...")
    num_classes = 10

    # This automatically downloads the pre-trained weights from ImageNet
    model = DiseaseDetectionModel(num_classes=num_classes)

    # Save the model with the pre-trained feature extractor + randomly initialized final classifier
    # In a full project, this model would now be trained on the PlantVillage dataset
    model_path = os.path.join(os.path.dirname(__file__), "disease_model.pth")
    torch.save(model.state_dict(), model_path)
    print(f"Transfer learning disease model saved to {model_path}")

if __name__ == "__main__":
    create_transfer_learning_model()
