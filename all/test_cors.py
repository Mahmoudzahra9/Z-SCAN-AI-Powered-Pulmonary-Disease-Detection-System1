import requests

try:
    resp = requests.options('http://127.0.0.1:5000/predict')
    print("OPTIONS headers:")
    for k, v in resp.headers.items():
        if 'access-control' in k.lower():
            print(f"{k}: {v}")
    
    resp = requests.get('http://127.0.0.1:5000/')
    print("\nGET headers:")
    for k, v in resp.headers.items():
        if 'access-control' in k.lower():
            print(f"{k}: {v}")
except Exception as e:
    print("Error:", e)
