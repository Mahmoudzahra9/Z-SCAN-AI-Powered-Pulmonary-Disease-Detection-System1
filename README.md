# 🫁 Z-SCAN AI-Powered Pulmonary Disease Detection System

An intelligent medical diagnosis platform that utilizes **Deep Learning** and **Explainable AI (XAI)** to analyze Chest X-ray images and assist in the early detection of pulmonary diseases.

---

## 📌 Overview

Z-SCAN is an AI-powered system designed to help healthcare professionals analyze Chest X-ray images quickly and efficiently.

The platform uses advanced Deep Learning models to classify Chest X-rays into multiple pulmonary diseases while providing visual explanations using Grad-CAM to improve transparency and trust in AI predictions.

> **Note:** This system is intended to assist healthcare professionals and is not a replacement for professional medical diagnosis.

---

# ✨ Features

- 🧠 AI-powered Chest X-ray analysis
- 🫁 Detects multiple pulmonary diseases
- 📊 Displays prediction confidence
- 🔍 Image validation using OpenAI CLIP
- 🔥 Explainable AI using Grad-CAM
- 📄 Automatic medical PDF report generation
- 🌐 Web Interface
- 📱 Flutter Mobile Application
- ⚡ Fast prediction through Flask REST API

---

# 🦠 Supported Diseases

- COVID-19
- Lung Cancer
- Pneumonia
- Pneumothorax
- Tuberculosis
- Normal

---

# 🏗 System Architecture

```
                Chest X-ray
                     │
                     ▼
            Image Validation (CLIP)
                     │
                     ▼
              Image Preprocessing
                     │
                     ▼
          Deep Learning Model
      (ResNet18 / DenseNet121)
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     Disease Prediction     Grad-CAM
          │                     │
          └──────────┬──────────┘
                     ▼
             Medical PDF Report
```

---

# 🛠 Technologies Used

### Artificial Intelligence

- Python
- PyTorch
- TorchVision
- OpenAI CLIP
- Grad-CAM
- NumPy
- OpenCV

### Backend

- Flask
- REST API

### Frontend

- Flutter
- HTML
- CSS
- JavaScript

### Tools

- Google Colab
- Git
- GitHub
- VS Code

---

# 📂 Project Structure

```
project
│
├── backend
│   ├── app.py
│   ├── train.py
│   ├── requirements.txt
│   └── ...
│
├── frontend
│   ├── lib
│   ├── android
│   └── ...
│
├── web_page
│
├── images
│
└── README.md
```

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/Mahmoudzahra9/Z-SCAN-AI-Powered-Pulmonary-Disease-Detection-System1.git
```

---

## Backend Installation

```bash
cd backend

pip install -r requirements.txt

python app.py
```

---

## Flutter App

```bash
cd frontend

flutter pub get

flutter run
```

---

# 📷 Screenshots

## Home Page

> Add image here

```
images/home.png
```

---

## Upload X-ray

> Add image here

```
images/upload.png
```

---

## Prediction Result

> Add image here

```
images/result.png
```

---

## Grad-CAM Visualization

> Add image here

```
images/gradcam.png
```

---

## Medical Report

> Add image here

```
images/report.png
```

---

# 📊 AI Pipeline

1. Upload Chest X-ray
2. Validate image using OpenAI CLIP
3. Preprocess image
4. Deep Learning prediction
5. Generate Grad-CAM visualization
6. Generate PDF report

---

# 🎯 Future Improvements

- Deploy on cloud servers
- Doctor dashboard
- User authentication
- Medical history
- Multi-language support
- Higher accuracy using ensemble learning
- DICOM image support

---

# 📈 Project Highlights

- AI-powered diagnosis
- Explainable AI (Grad-CAM)
- Medical PDF Reports
- Flutter Mobile Application
- Flask REST API
- Modern User Interface

---

# 👨‍💻 Author

**Mahmoud Reda Ali Zahra**

Computer Science Student

GitHub:
https://github.com/Mahmoudzahra9

LinkedIn:
(Add your LinkedIn profile here)

---

# 📄 License

This project is intended for educational and research purposes.

---

## ⭐ Support

If you like this project, don't forget to **Star ⭐ the repository**.
