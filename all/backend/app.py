import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import numpy as np

app = Flask(__name__)
CORS(app)

# Classes
CLASSES = ['COVID-19', 'LUNG CANCER', 'NORMAL', 'PNEUMONIA', 'PNEUMOTHORAX', 'TUBERCULOSIS']

# Advice, Diet Recommendations, and Doctors
RECOMMENDATIONS = {
    'NORMAL': {
        'advice_ar': 'حافظ على نمط حياة صحي، مارس الرياضة بانتظام، وتجنب التدخين.',
        'advice_en': 'Maintain a healthy lifestyle, exercise regularly, and avoid smoking.',
        'diet_ar': 'تناول وجبات متوازنة غنية بالفواكه والخضروات والحبوب الكاملة والبروتينات.',
        'diet_en': 'Eat a balanced diet rich in fruits, vegetables, whole grains, and proteins.',
        'doctors_ar': 'لا توجد حاجة لزيارة طبيب في الوقت الحالي. استمر في الفحوصات الدورية.',
        'doctors_en': 'No doctor visit needed at this time. Continue routine check-ups.',
        'videos': [
            {'title': 'نصائح لنمط حياة صحي (عربي)', 'url': 'https://www.youtube.com/results?search_query=نصائح+لنمط+حياة+صحي+للرئتين'},
            {'title': 'Healthy Lifestyle Tips (English)', 'url': 'https://www.youtube.com/results?search_query=healthy+lungs+lifestyle'}
        ]
    },
    'COVID-19': {
        'advice_ar': 'اعزل نفسك، خذ قسطاً كافياً من الراحة، حافظ على رطوبة جسمك، وراقب مستويات الأكسجين لديك. استشر طبيباً فوراً.',
        'advice_en': 'Isolate yourself, get plenty of rest, stay hydrated, and monitor your oxygen levels. Consult a doctor immediately.',
        'diet_ar': 'اشرب سوائل دافئة بكثرة، تناول الشوربة، الحمضيات (غنية بفيتامين سي)، والأطعمة الخفيفة سهلة الهضم.',
        'diet_en': 'Drink plenty of warm fluids, eat soups, citrus fruits (rich in Vitamin C), and easily digestible foods.',
        'doctors_ar': 'أخصائي أمراض معدية أو أخصائي أمراض صدرية.',
        'doctors_en': 'Infectious Disease Specialist or Pulmonologist.',
        'videos': [
            {'title': 'أعراض كورونا وطرق الوقاية (عربي)', 'url': 'https://www.youtube.com/results?search_query=كورونا+الاعراض+وطرق+الوقاية'},
            {'title': 'COVID-19 Causes and Prevention (English)', 'url': 'https://www.youtube.com/results?search_query=COVID-19+causes+and+prevention'},
            {'title': 'تمارين تنفس للتعافي (عربي)', 'url': 'https://www.youtube.com/results?search_query=تمارين+تنفس+كورونا'}
        ]
    },
    'PNEUMONIA': {
        'advice_ar': 'احصل على الكثير من الراحة، التزم بتعليمات الطبيب والأدوية الموصوفة، واستخدم مرطب للهواء لتسهيل التنفس.',
        'advice_en': 'Get plenty of rest, strictly follow doctor instructions and prescribed medications, and use a humidifier to ease breathing.',
        'diet_ar': 'اشرب الكثير من الماء والسوائل الدافئة، تناول أطعمة تعزز المناعة مثل العسل، الزنجبيل، والخضروات الورقية.',
        'diet_en': 'Drink plenty of water and warm fluids. Eat immune-boosting foods like honey, ginger, and leafy greens.',
        'doctors_ar': 'أخصائي أمراض صدرية (طبيب تنفسية).',
        'doctors_en': 'Pulmonologist (Respiratory Physician).',
        'videos': [
            {'title': 'التهاب الرئة: الأسباب والعلاج (عربي)', 'url': 'https://www.youtube.com/results?search_query=التهاب+الرئة+الاسباب+والعلاج'},
            {'title': 'Pneumonia: Causes, Signs & Prevention (English)', 'url': 'https://www.youtube.com/results?search_query=Pneumonia+causes+signs+prevention'},
            {'title': 'كيف تقي نفسك من التهاب الرئة (عربي)', 'url': 'https://www.youtube.com/results?search_query=الوقاية+من+التهاب+الرئة'}
        ]
    },
    'TUBERCULOSIS': {
        'advice_ar': 'التزم تماماً بكورس العلاج الذي يصفه الطبيب دون انقطاع. ارتدِ كمامة وتجنب الأماكن المزدحمة لمنع نقل العدوى.',
        'advice_en': 'Strictly adhere to the treatment course prescribed by the doctor without interruption. Wear a mask and avoid crowded places.',
        'diet_ar': 'اتبع نظاماً غذائياً عالي البروتين والسعرات الحرارية (اللحوم، البيض، الحليب) لتعويض فقدان الوزن وبناء الأنسجة.',
        'diet_en': 'Follow a high-protein, high-calorie diet (meat, eggs, milk) to recover weight loss and rebuild tissue.',
        'doctors_ar': 'أخصائي أمراض صدرية متخصص في السل أو أخصائي أمراض معدية.',
        'doctors_en': 'Pulmonologist specializing in TB or Infectious Disease Specialist.',
        'videos': [
            {'title': 'مرض السل: أسبابه وطرق علاجه (عربي)', 'url': 'https://www.youtube.com/results?search_query=مرض+السل+أسبابه+وطرق+علاجه'},
            {'title': 'Tuberculosis (TB) Causes and Prevention (English)', 'url': 'https://www.youtube.com/results?search_query=Tuberculosis+causes+and+prevention'},
            {'title': 'كيف تحمي نفسك من مرض السل (عربي)', 'url': 'https://www.youtube.com/results?search_query=الوقاية+من+مرض+السل'}
        ]
    },
    'LUNG CANCER': {
        'advice_ar': 'استشر طبيب أورام مختص فوراً لمناقشة خيارات العلاج (جراحة، علاج كيميائي، إشعاعي). احصل على دعم نفسي.',
        'advice_en': 'Consult a specialized oncologist immediately to discuss treatment options (surgery, chemotherapy, radiation). Seek psychological support.',
        'diet_ar': 'نظام غذائي متوازن غني بمضادات الأكسدة والبروتينات لدعم الجسم أثناء العلاج.',
        'diet_en': 'A balanced diet rich in antioxidants and proteins to support the body during treatment.',
        'doctors_ar': 'طبيب أورام (Oncologist) أو جراح صدر.',
        'doctors_en': 'Oncologist or Thoracic Surgeon.',
        'videos': [
            {'title': 'سرطان الرئة: الأعراض والأسباب (عربي)', 'url': 'https://www.youtube.com/results?search_query=سرطان+الرئة+الأعراض+والأسباب'},
            {'title': 'Lung Cancer: Causes and Prevention (English)', 'url': 'https://www.youtube.com/results?search_query=Lung+cancer+causes+and+prevention'},
            {'title': 'طرق الوقاية من سرطان الرئة (عربي)', 'url': 'https://www.youtube.com/results?search_query=طرق+الوقاية+من+سرطان+الرئة'}
        ]
    },
    'PNEUMOTHORAX': {
        'advice_ar': 'تجنب المجهود البدني الشاق، السفر بالطائرة، أو الغوص حتى يسمح لك الطبيب. راقب أي ألم مفاجئ في الصدر.',
        'advice_en': 'Avoid strenuous physical effort, air travel, or diving until your doctor permits. Monitor for sudden chest pain.',
        'diet_ar': 'تناول وجبات خفيفة ومغذية وتجنب الإفراط في الأكل الذي قد يضغط على الحجاب الحاجز.',
        'diet_en': 'Eat light, nutritious meals and avoid overeating to prevent pressure on the diaphragm.',
        'doctors_ar': 'أخصائي جراحة صدر أو طبيب طوارئ.',
        'doctors_en': 'Thoracic Surgeon or Emergency Physician.',
        'videos': [
            {'title': 'الاسترواح الصدري (ثقب الرئة): الأسباب (عربي)', 'url': 'https://www.youtube.com/results?search_query=الاسترواح+الصدري+أسبابه'},
            {'title': 'Pneumothorax Causes and Treatments (English)', 'url': 'https://www.youtube.com/results?search_query=Pneumothorax+causes+and+treatments'},
            {'title': 'كيفية التعامل مع الاسترواح الصدري (عربي)', 'url': 'https://www.youtube.com/results?search_query=التعامل+مع+الاسترواح+الصدري'}
        ]
    }
}

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the model (UPGRADED: DenseNet121 for superior X-ray classification, with ResNet18 fallback)
try:
    state_dict = torch.load('chest_xray_model.pth', map_location=device)
    if 'fc.weight' in state_dict:
        print("--------------------------------------------------")
        print("Detected ResNet18 weights in chest_xray_model.pth. Initializing ResNet18.")
        print("--------------------------------------------------")
        model = models.resnet18(weights=None)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, 6)
    else:
        print("--------------------------------------------------")
        print("Detected DenseNet121 weights in chest_xray_model.pth. Initializing DenseNet121.")
        print("--------------------------------------------------")
        model = models.densenet121(weights=None)
        num_ftrs = model.classifier.in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.4),
            nn.Linear(num_ftrs, 6)
        )
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()
    print("--------------------------------------------------")
    print(f"Model loaded successfully on device: {device}")
    print(f"Supported classes: {CLASSES}")
    print("--------------------------------------------------")
except Exception as e:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"CRITICAL ERROR loading model: {e}")
    print("Check if 'chest_xray_model.pth' is in the same directory.")
    print("After retraining with DenseNet121, run: python train.py")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    model = None

# ----- Image Preprocessing Pipeline -----
# MUST match val/test transforms in train.py exactly!
# Grayscale → Resize(256) → CenterCrop(224) → Normalize
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),  # Strips false colors, keeps structure
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def is_valid_xray(image_bytes):
    """Quick heuristic: real X-rays are nearly grayscale.
    If the image has too much color variation between R/G/B channels,
    it's likely a photo/screenshot — not a medical X-ray.
    Returns (is_valid: bool, error_msg: str)"""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        arr = np.array(img, dtype=np.float32)
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        # Compute mean absolute deviation between channels
        rg_diff = np.mean(np.abs(r - g))
        rb_diff = np.mean(np.abs(r - b))
        gb_diff = np.mean(np.abs(g - b))
        color_score = (rg_diff + rb_diff + gb_diff) / 3
        # Threshold: >30 means strong color → not a grayscale X-ray
        if color_score > 30:
            return False, (
                'The uploaded image does not appear to be a valid chest X-ray.\n'
                'الصورة المرفوعة لا تبدو صورة أشعة سينية صحيحة.\n'
                'Please upload a proper grayscale medical X-ray image. / '
                'من فضلك ارفع صورة أشعة طبية واضحة بالأبيض والأسود.'
            )
        return True, ''
    except Exception:
        return True, ''  # Allow through if check fails

def predict_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            confidence, predicted_idx = torch.max(probabilities, dim=0)
            
        prediction = CLASSES[predicted_idx.item()]
        conf_score = confidence.item()
        
        return prediction, conf_score
    except Exception as e:
        print(f"Prediction error: {e}")
        return None, None

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        if model is None:
            return jsonify({'error': 'Model not loaded on server.'}), 500

        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request.'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected.'}), 400
            
        try:
            img_bytes = file.read()

            # Quality filter: reject non-X-ray images before prediction
            valid, err_msg = is_valid_xray(img_bytes)
            if not valid:
                return jsonify({'error': err_msg}), 400

            prediction, confidence = predict_image(img_bytes)
            
            if prediction is not None:
                rec = RECOMMENDATIONS.get(prediction, {})
                return jsonify({
                    'prediction': prediction,
                    'confidence': confidence,
                    'advice_ar': rec.get('advice_ar', ''),
                    'advice_en': rec.get('advice_en', ''),
                    'diet_ar': rec.get('diet_ar', ''),
                    'diet_en': rec.get('diet_en', ''),
                    'doctors_ar': rec.get('doctors_ar', ''),
                    'doctors_en': rec.get('doctors_en', ''),
                    'videos': rec.get('videos', [])
                })
            else:
                return jsonify({'error': 'Error during prediction process.'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "healthy", "message": "AI Medical Imaging API is running."})

if __name__ == '__main__':
    # Run on all available IP addresses
    app.run(host='0.0.0.0', port=5000)
