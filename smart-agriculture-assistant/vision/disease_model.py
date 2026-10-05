import torch
import torch.nn as nn
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights

class DiseaseDetectionModel(nn.Module):
    def __init__(self, num_classes=10):
        super(DiseaseDetectionModel, self).__init__()
        # Load PRE-TRAINED MobileNetV2 (Transfer Learning)
        weights = MobileNet_V2_Weights.DEFAULT
        self.model = mobilenet_v2(weights=weights)

        # Freeze early layers to act as feature extractor
        for param in self.model.features.parameters():
            param.requires_grad = False

        # Replace the classifier for our specific disease classes
        self.model.classifier[1] = nn.Linear(self.model.last_channel, num_classes)

    def forward(self, x):
        return self.model(x)

def get_disease_classes():
    return [
        "Apple___Apple_scab", "Apple___Black_rot", "Apple___healthy",
        "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
        "Tomato___Leaf_Mold", "Tomato___Target_Spot", "Tomato___Tomato_mosaic_virus",
        "Tomato___healthy"
    ]
