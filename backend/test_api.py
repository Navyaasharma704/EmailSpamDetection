import requests

url = "http://127.0.0.1:5000/predict"

data = {
    "email": "Congratulations! You have won ₹50000. Click here to claim your prize."
}

response = requests.post(url, json=data)

print(response.json())