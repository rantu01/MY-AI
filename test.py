import requests

# 1. Apnar notun key (jeta terminal-e use korchen)
API_KEY = "AIzaSyBCiKubEw-7Nu3C7w54AV0I2a7EMaqHxqY"

# 2. Terminal-e Gemini 2.5 Flash dekha geche, tai oita use korbo
MODEL_NAME = "gemini-2.5-flash"

# 3. URL structure (v1 use korun, karon terminal-e v1 status 200 dekhachhe)
url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

payload = {
    "contents": [{
        "parts": [{"text": "Hello Jarvis! Are you version 2.5?"}]
    }]
}

headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("🎉 SUCCESS! Jarvis is using Gemini 2.5.")
        print("Response:", response.json()['candidates'][0]['content']['parts'][0]['text'])
    else:
        print(f"Status Code: {response.status_code}")
        print("Error Details:", response.text)
        
except Exception as e:
    print(f"Error: {e}")