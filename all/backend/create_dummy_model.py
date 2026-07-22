import os
import torch
from torchvision import models
import torch.nn as nn

try:
    model = models.densenet121(weights=None)
    num_ftrs = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4),
        nn.Linear(num_ftrs, 6)
    )
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, 'chest_xray_model.pth')
    torch.save(model.state_dict(), output_path)
    print(f"Baseline 6-class DenseNet121 model saved to {output_path}!")
except Exception as e:
    print(f"Error: {e}")
