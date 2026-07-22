import requests
import sys

print("Testing Backend POST request...")
try:
    # We just create a dummy "image" byte stream
    dummy_image = b'MM\x00\x0a\x00\x00\x00\x00\x00\x00\x00\x00' # Some invalid bytes but it will hit the server
    files = {'file': ('dummy.jpg', dummy_image, 'image/jpeg')}
    res = requests.post('http://127.0.0.1:5000/predict', files=files)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"REQUEST FAILED: {e}")
