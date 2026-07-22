import requests
from io import BytesIO
from PIL import Image

API_URL = 'http://127.0.0.1:5000'

def test_valid_xray():
    print("\n--- Test 1: Valid Chest X-ray (lung_cancer.png) ---")
    try:
        with open('test_images/lung_cancer.png', 'rb') as f:
            files = {'file': ('lung_cancer.png', f.read(), 'image/png')}
        res = requests.post(f'{API_URL}/predict', files=files)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json().get('prediction')} (Unknown: {res.json().get('unknown_disease')})")
        print(f"Advice Ar: {res.json().get('advice_ar')[:50]}...")
    except Exception as e:
        print(f"Failed: {e}")

def test_blank_image():
    print("\n--- Test 2: Blank/Solid White Image (Should fail detail/std check) ---")
    try:
        img = Image.new('RGB', (224, 224), color='white')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        files = {'file': ('blank.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
        res = requests.post(f'{API_URL}/predict', files=files)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json().get('prediction')} (Unknown: {res.json().get('unknown_disease')})")
        print(f"Advice Ar: {res.json().get('advice_ar')}")
    except Exception as e:
        print(f"Failed: {e}")

def test_bright_corners():
    print("\n--- Test 3: Grayscale Image with Bright Corners (Should fail corner check) ---")
    try:
        # Create a 224x224 grayscale image where top corners are bright white (255)
        # and middle is darker.
        img = Image.new('L', (224, 224), color=50) # Dark background
        # Make top corners white
        for x in range(30):
            for y in range(30):
                img.putpixel((x, y), 255) # Top-Left
                img.putpixel((224 - 1 - x, y), 255) # Top-Right
        
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        files = {'file': ('cat_mockup.jpg', img_byte_arr.getvalue(), 'image/jpeg')}
        res = requests.post(f'{API_URL}/predict', files=files)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json().get('prediction')} (Unknown: {res.json().get('unknown_disease')})")
        print(f"Advice Ar: {res.json().get('advice_ar')}")
    except Exception as e:
        print(f"Failed: {e}")

def test_google_auth():
    print("\n--- Test 4: Google Auth Endpoint (/auth/google) ---")
    try:
        payload = {'id_token': 'dummy_google_jwt_token_for_testing'}
        res = requests.post(f'{API_URL}/auth/google', json=payload)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    print("Starting automated tests against local Flask server...")
    test_valid_xray()
    test_blank_image()
    test_bright_corners()
    test_google_auth()
