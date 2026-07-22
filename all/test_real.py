import requests
from io import BytesIO
from PIL import Image

# Create a valid white image
img = Image.new('RGB', (224, 224), color = 'white')
img_byte_arr = BytesIO()
img.save(img_byte_arr, format='JPEG')
img_byte_arr = img_byte_arr.getvalue()

files = {'file': ('test.jpg', img_byte_arr, 'image/jpeg')}
try:
    print("Sending POST request to http://127.0.0.1:5000/predict ...")
    res = requests.post('http://127.0.0.1:5000/predict', files=files)
    print(f"Status Code: {res.status_code}")
    print(f"Response Body: {res.text}")
except Exception as e:
    print(f"Exception: {e}")
