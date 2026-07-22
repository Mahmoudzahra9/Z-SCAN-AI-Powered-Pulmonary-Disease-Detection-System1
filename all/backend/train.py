import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from tqdm import tqdm

"""
========================================================
CHEST X-RAY TRAINING SCRIPT - DenseNet121
========================================================

Dataset Structure:

dataset/
│
├── train/
│   ├── COVID-19/
│   ├── LUNG CANCER/
│   ├── NORMAL/
│   ├── PNEUMONIA/
│   ├── PNEUMOTHORAX/
│   └── TUBERCULOSIS/
│
├── val/
│   └── same folders
│
└── test/
    └── same folders

Run:
python train.py
"""

# ======================================================
# CONFIG
# ======================================================

DATA_DIR = "dataset"

MODEL_SAVE_PATH = "chest_xray_model.pth"

BATCH_SIZE = 32
NUM_EPOCHS = 20
LEARNING_RATE = 0.0001

CLASSES = [
    'COVID-19',
    'LUNG CANCER',
    'NORMAL',
    'PNEUMONIA',
    'PNEUMOTHORAX',
    'TUBERCULOSIS'
]

NUM_CLASSES = len(CLASSES)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("=" * 60)
print(f"Using device: {DEVICE}")
print("=" * 60)


# ======================================================
# TRANSFORMS
# ======================================================

train_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),

    transforms.Resize((256, 256)),
    transforms.RandomCrop(224),

    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),

    transforms.ColorJitter(
        brightness=0.3,
        contrast=0.3
    ),

    transforms.RandomAdjustSharpness(
        sharpness_factor=2,
        p=0.5
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

val_test_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),

    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

data_transforms = {
    "train": train_transform,
    "val": val_test_transform,
    "test": val_test_transform
}


# ======================================================
# DATA LOADING
# ======================================================

def load_datasets():

    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(
            f"Dataset folder not found: {DATA_DIR}"
        )

    phases = []

    for phase in ["train", "val", "test"]:
        phase_path = os.path.join(DATA_DIR, phase)

        if os.path.exists(phase_path):
            phases.append(phase)

    image_datasets = {
        phase: datasets.ImageFolder(
            os.path.join(DATA_DIR, phase),
            transform=data_transforms[phase]
        )
        for phase in phases
    }

    dataloaders = {
        phase: DataLoader(
            image_datasets[phase],
            batch_size=BATCH_SIZE,
            shuffle=(phase == "train"),
            num_workers=0
        )
        for phase in phases
    }

    dataset_sizes = {
        phase: len(image_datasets[phase])
        for phase in phases
    }

    return phases, image_datasets, dataloaders, dataset_sizes


# ======================================================
# MODEL
# ======================================================

def create_model():

    print("\nLoading DenseNet121 pretrained model...")

    model = models.densenet121(
        weights=models.DenseNet121_Weights.DEFAULT
    )

    num_ftrs = model.classifier.in_features

    model.classifier = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(num_ftrs, NUM_CLASSES)
    )

    model = model.to(DEVICE)

    return model


# ======================================================
# TRAIN FUNCTION
# ======================================================

def train_model():

    phases, image_datasets, dataloaders, dataset_sizes = load_datasets()

    print("\nClasses Found:")
    print(image_datasets["train"].classes)

    print("\nDataset Sizes:")
    print(dataset_sizes)

    model = create_model()

    criterion = nn.CrossEntropyLoss()

    optimizer = optim.Adam([
        {
            'params': model.features.parameters(),
            'lr': LEARNING_RATE * 0.1
        },
        {
            'params': model.classifier.parameters(),
            'lr': LEARNING_RATE
        }
    ])

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='max',
        factor=0.5,
        patience=3
    )

    best_acc = 0.0

    print("\n" + "=" * 60)
    print("Starting Training...")
    print("=" * 60)

    for epoch in range(NUM_EPOCHS):

        print(f"\nEpoch {epoch + 1}/{NUM_EPOCHS}")
        print("-" * 40)

        for phase in ["train", "val"]:

            if phase not in phases:
                continue

            if phase == "train":
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            loop = tqdm(dataloaders[phase])

            for inputs, labels in loop:

                inputs = inputs.to(DEVICE)
                labels = labels.to(DEVICE)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == "train"):

                    outputs = model(inputs)

                    _, preds = torch.max(outputs, 1)

                    loss = criterion(outputs, labels)

                    if phase == "train":
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)

                running_corrects += torch.sum(
                    preds == labels.data
                )

            epoch_loss = running_loss / dataset_sizes[phase]

            epoch_acc = (
                running_corrects.double() /
                dataset_sizes[phase]
            )

            print(
                f"{phase.upper()} "
                f"Loss: {epoch_loss:.4f} | "
                f"Accuracy: {epoch_acc:.4f} "
                f"({epoch_acc * 100:.2f}%)"
            )

            # ==========================================
            # SAVE BEST MODEL
            # ==========================================

            if phase == "val":

                scheduler.step(epoch_acc)

                if epoch_acc > best_acc:

                    best_acc = epoch_acc

                    torch.save(
                        model.state_dict(),
                        MODEL_SAVE_PATH
                    )

                    print("\n✅ Best model saved!")
                    print(
                        f"Validation Accuracy: "
                        f"{best_acc * 100:.2f}%"
                    )

    print("\n" + "=" * 60)
    print("TRAINING FINISHED")
    print("=" * 60)

    print(
        f"\nBest Validation Accuracy: "
        f"{best_acc * 100:.2f}%"
    )

    # ==================================================
    # FINAL TEST
    # ==================================================

    if "test" in phases:

        print("\nRunning Final Test...")

        model.load_state_dict(
            torch.load(
                MODEL_SAVE_PATH,
                map_location=DEVICE
            )
        )

        model.eval()

        running_corrects = 0

        class_correct = {
            cls: 0 for cls in CLASSES
        }

        class_total = {
            cls: 0 for cls in CLASSES
        }

        with torch.no_grad():

            for inputs, labels in tqdm(
                dataloaders["test"]
            ):

                inputs = inputs.to(DEVICE)
                labels = labels.to(DEVICE)

                outputs = model(inputs)

                _, preds = torch.max(outputs, 1)

                running_corrects += torch.sum(
                    preds == labels.data
                )

                for label, pred in zip(labels, preds):

                    class_name = CLASSES[label.item()]

                    class_total[class_name] += 1

                    if label == pred:
                        class_correct[class_name] += 1

        test_acc = (
            running_corrects.double() /
            dataset_sizes["test"]
        )

        print(
            f"\nFinal Test Accuracy: "
            f"{test_acc * 100:.2f}%"
        )

        print("\nPer-Class Accuracy:")
        print("-" * 40)

        for cls in CLASSES:

            if class_total[cls] > 0:

                acc = (
                    class_correct[cls] /
                    class_total[cls]
                )

                print(
                    f"{cls}: {acc * 100:.2f}%"
                )

    print("\n✅ Training Complete Successfully!")
    print(f"✅ Model saved as: {MODEL_SAVE_PATH}")


# ======================================================
# MAIN
# ======================================================

if __name__ == "__main__":
    train_model()