import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

"""
How to use this training script:
1. Ensure your dataset is structured like this:
   dataset/
       train/
           COVID-19/
           LUNG CANCER/
           NORMAL/
           PNEUMONIA/
           PNEUMOTHORAX/
           TUBERCULOSIS/
       val/
           <same 6 folders>
       test/
           <same 6 folders>
           
2. Update the `data_dir` variable below to point to your dataset folder.
3. Run this script: python train.py
"""

# ----------------- Configuration -----------------
data_dir = r"dataset" # Points to backend/dataset
batch_size = 32
num_epochs = 15
learning_rate = 0.001

# The 6 classes based on the app
CLASSES = ['COVID-19', 'LUNG CANCER', 'NORMAL', 'PNEUMONIA', 'PNEUMOTHORAX', 'TUBERCULOSIS']
num_classes = len(CLASSES)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ----------------- Data Augmentation -----------------
# Data augmentation increases accuracy by creating variations of the images
data_transforms = {
    'train': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'test': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

def train_model():
    if not os.path.exists(data_dir):
        print(f"Error: Directory {data_dir} not found. Please setup your dataset.")
        return

    # Load datasets (train, val, test)
    phases = [d for d in ['train', 'val', 'test'] if os.path.exists(os.path.join(data_dir, d))]
    image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x]) for x in phases}
    
    # We use num_workers=0 on Windows to avoid process spawning issues for a quick script
    dataloaders = {x: DataLoader(image_datasets[x], batch_size=batch_size, shuffle=(x == 'train'), num_workers=0) for x in phases}
    dataset_sizes = {x: len(image_datasets[x]) for x in phases}
    class_names = image_datasets['train'].classes
    
    print(f"Classes found: {class_names}")
    if set(class_names) != set(CLASSES):
        print("Warning: Dataset classes do not match expected expected list.")

    # Apply pretrained ResNet18 model
    # Using 'weights=models.ResNet18_Weights.DEFAULT' instead of deprecated 'pretrained=True'
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    model = model.to(device)

    # Loss function & Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    best_acc = 0.0

    print("Starting training...")
    for epoch in range(num_epochs):
        print(f'Epoch {epoch+1}/{num_epochs}')
        print('-' * 10)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in tqdm(dataloaders[phase], desc=phase):
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

            # deep copy the model
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                torch.save(model.state_dict(), 'resnet_model.pth')
                print('Found better model, saving...')
        print()

    print(f'Training complete. Best val Acc: {best_acc:4f}')

    # Final testing phase
    if 'test' in phases:
        print("\n" + "="*20)
        print("Starting Final Test...")
        model.load_state_dict(torch.load('resnet_model.pth'))
        model.eval()
        running_corrects = 0
        
        all_preds = []
        all_labels = []
        
        for inputs, labels in tqdm(dataloaders['test'], desc='test'):
            inputs = inputs.to(device)
            labels = labels.to(device)
            with torch.no_grad():
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
            running_corrects += torch.sum(preds == labels.data)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
        test_acc = running_corrects.double() / dataset_sizes['test']
        print(f'Final Test Accuracy: {test_acc:.4f}')

        # Generate Confusion Matrix
        print("Generating Confusion Matrix...")
        cm = confusion_matrix(all_labels, all_preds)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.title('Confusion Matrix - Test Set')
        plt.tight_layout()
        plt.savefig('confusion_matrix.png')
        print("Confusion Matrix saved as 'confusion_matrix.png'")

if __name__ == '__main__':
    train_model()
