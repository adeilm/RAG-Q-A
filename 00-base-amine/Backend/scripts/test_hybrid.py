import requests
import json

url = "http://localhost:8000/query"
headers = {"Content-Type": "application/json"}
payload = {
    "query": "Quelles fondations ont été utilisées pour les pylônes de type treillis de plus de 40m de hauteur ?",
    "top_k": 5,
    "session_id": "global"
}

print("Testing Hybrid Search via Natural Language Intent Extraction...")
try:
    response = requests.post(url, json=payload, headers=headers, stream=True)
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                print(line.decode("utf-8"))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Exception: {e}")
