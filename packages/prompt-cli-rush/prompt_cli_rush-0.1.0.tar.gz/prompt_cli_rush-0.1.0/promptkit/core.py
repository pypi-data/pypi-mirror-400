import requests
import os
from dotenv import load_dotenv

# ✅ Load .env file explicitly
load_dotenv()

# ✅ Read API key from .env
OPENROUTER_API_KEY = "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"

# if not OPENROUTER_API_KEY:
#     raise RuntimeError("OPENROUTER_API_KEY not found in .env file")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    # Recommended by OpenRouter
    "HTTP-Referer": "http://localhost",
    "X-Title": "promptkit"
}

def ask(prompt, history=None):
    messages = []
    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": prompt})

    payload = {
        # ✅ FREE & GOOD FOR CODING
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": messages,
        "temperature": 0.2
    }
    try:
        res = requests.post(API_URL, headers=HEADERS, json=payload)
        if res.status_code != 200:
            return f"Request failed: {res.text}"

        return res.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Request failed: {e}"