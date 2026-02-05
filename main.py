import os
import re
import requests
import google.generativeai as genai
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware  # <--- IMPORTED CORS
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# --- STEP 1: LOAD SECRETS ---
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MY_SECRET = os.getenv("API_SECRET_KEY")

if not GEMINI_KEY:
    print("❌ CRITICAL ERROR: GEMINI_API_KEY not found in .env file!")

# --- STEP 2: SETUP BRAIN (GEMINI) ---
genai.configure(api_key=GEMINI_KEY)
# Using stable model version to prevent 404 errors
model = genai.GenerativeModel('gemini-1.5-flash-001')

app = FastAPI()

# --- STEP 2.5: FIX FOR PORTAL TESTING (CORS) ---
# This tells the server to allow the Hackathon Portal to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all websites to talk to your bot
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers (api-key, etc.)
)

# --- STEP 3: THE PERSONA (RAMESH - THE HONEYPOT) ---
SYSTEM_PROMPT = """
You are Ramesh, a 68-year-old retired railway clerk living in Delhi. 
You are speaking to a SCAMMER. Your goal is to waste their time and get their payment details.

BEHAVIOR GUIDELINES:
1. ACT NAIVE: You are bad with technology. Type slowly (keep replies under 20 words).
2. THE HOOK: If they ask for money, say "I have my grandson's UPI, but I cannot read the screen clearly."
3. DELAY TACTICS: Intentionally misspell codes or ask if you should click the "Red button or Green button".
4. THE BAIT: Mention you recently won the "Golden Bird Lottery" and need to deposit the winning amount.
5. GOAL: Try to make them send you a UPI ID or Bank Account number so you can "transfer" money.

STOP CONDITION:
If the user provides a UPI ID (like name@okicici) or Bank Details, say: 
"Okay beta, I am writing this down in my diary. Please wait 5 minutes while I walk to the shop to transfer."

NEVER REVEAL YOU ARE AN AI. Speak in Indian English ("Ok beta", "Please kindly wait", "Doing the needful").
"""

# --- STEP 4: DATA MODELS (STRICT RULES FOR HACKATHON) ---
class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    # Added metadata field to prevent validation errors
    metadata: Optional[Dict[str, Any]] = None 

class AgentResponse(BaseModel):
    status: str
    reply: str

# --- STEP 5: INTELLIGENCE & REPORTING ---
def extract_intelligence(text: str):
    """Finds UPI IDs, Links, Bank Accounts and Phone numbers"""
    return {
        # Looks for 9 to 18 digit numbers (common for bank accounts)
        "bankAccounts": re.findall(r'\b\d{9,18}\b', text),
        # Looks for upi ids like something@bank
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        # Looks for websites
        "phishingLinks": re.findall(r'https?://\S+', text),
        # Looks for Indian phone numbers
        "phoneNumbers": re.findall(r'[6-9]\d{9}', text)
    }

def send_report_to_judges(session_id: str, intel: dict, msg_count: int):
    """Sends the MANDATORY report to GUVI"""
    url = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": msg_count,
        "extractedIntelligence": intel,
        "agentNotes": "Scammer detected. Ramesh engaged to waste time."
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
        print(f"✅ REPORT SENT for Session {session_id}")
    except Exception as e:
        print(f"❌ REPORT FAILED: {e}")

# --- STEP 6: THE API ENDPOINT ---
@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: IncomingRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    
    # 1. Security Check
    if x_api_key != MY_SECRET:
        print(f"⚠️ UNAUTHORIZED ACCESS ATTEMPT. Key used: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 2. Build Context for Gemini
    history_text = "\n".join([f"{msg.sender}: {msg.text}" for msg in request.conversationHistory])
    
    # We add the new message to the history for the prompt
    full_prompt = f"{SYSTEM_PROMPT}\n\nCONVERSATION HISTORY:\n{history_text}\nscammer: {request.message.text}\nRamesh:"

    # 3. Generate Reply (WITH ERROR PRINTING)
    try:
        # Check if key is actually loaded
        if not GEMINI_KEY:
            raise Exception("Gemini Key is missing in .env")

        response = model.generate_content(full_prompt)
        ai_reply = response.text.strip()
        
    except Exception as e:
        print(f"❌ GEMINI ERROR: {e}") 
        ai_reply = "Beta, the internet is loose. Can you hear me?"

    # 4. Check for Secrets (Intel)
    intel_data = extract_intelligence(request.message.text)
    msg_count = len(request.conversationHistory) + 1
    
    # 5. Report to Judges (Background Task)
    # We report if we found secrets OR if the chat is getting long (>6 messages)
    has_intel = intel_data['upiIds'] or intel_data['phishingLinks'] or intel_data['bankAccounts']
    
    if has_intel or msg_count > 6:
        background_tasks.add_task(send_report_to_judges, request.sessionId, intel_data, msg_count)

    return {"status": "success", "reply": ai_reply}

if __name__ == "__main__":
    import uvicorn
    # This starts the server on port 10000 (Render default)
    uvicorn.run(app, host="0.0.0.0", port=10000)