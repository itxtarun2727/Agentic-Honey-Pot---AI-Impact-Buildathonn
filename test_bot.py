import requests

# 1. The URL of your bot (Localhost)
url = "http://127.0.0.1:8000/chat"

# 2. The Password you set in .env
headers = {"x-api-key": "buildathon2026"}  # This should match API_SECRET_KEY in your .env file

# 3. The Fake Scam Message
payload = {
    "sessionId": "test-123",
    "message": {
        "sender": "scammer",
        "text": "Hello, I am from the bank. Give me your UPI PIN immediately.",
        "timestamp": 123456
    },
    "conversationHistory": []
}

# 4. Send the message
print("⏳ Sending message to Ramesh...")
try:
    response = requests.post(url, json=payload, headers=headers)
    
    # 5. Print the Answer
    if response.status_code == 200:
        print("\n✅ SUCCESS! Ramesh replied:")
        print("------------------------------------------------")
        print(response.json()['reply'])
        print("------------------------------------------------")
    else:
        print(f"\n❌ ERROR {response.status_code}: {response.text}")

except Exception as e:
    print(f"\n❌ CONNECTION FAILED: {e}")