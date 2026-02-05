import requests

# our Live URL
url = "https://agentic-honey-pot-ai-impact-buildathonn.onrender.com/chat"

# The data we are sending (just like the judges)
payload = {
    "sessionId": "test-session-123",
    "message": {
        "sender": "scammer",
        "text": "Hello, I am calling from your bank.",
        "timestamp": 1234567890
    },
    "conversationHistory": [],
    "metadata": {"channel": "SMS", "language": "en"}
}

# The secret key
headers = {
    "x-api-key": "buildathon2026",
    "Content-Type": "application/json"
}

try:
    print(f"📡 Sending request to: {url}...")
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📜 Response: {response.text}")
    
    if response.status_code == 200:
        print("\n🎉 SUCCESS! Your bot is FIXED and replying correctly.")
    else:
        print("\n❌ STILL FAILING. Check the error above.")

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")