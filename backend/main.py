import os
import json
import re
import ipaddress
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Set in .env like:
# GEMINI_MODEL=models/gemini-2.5-flash
MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
MODEL_NAME_CLEAN = MODEL_NAME.replace("models/", "")

GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME_CLEAN}:generateContent"
    f"?key={GEMINI_API_KEY}"
)

HISTORY_FILE = "history.json"

app = FastAPI(title="PhishGuard Backend", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Request schema
# -----------------------------
class AnalyzeRequest(BaseModel):
    url: str


# -----------------------------
# Helpers: history storage
# -----------------------------
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def add_to_history(entry: Dict[str, Any]):
    history = load_history()
    history.insert(0, entry)  # newest first
    save_history(history)


# -----------------------------
# URL helpers
# -----------------------------
def extract_domain(url: str) -> Dict[str, str]:
    u = url.strip()

    # Add scheme if missing
    if not u.startswith(("http://", "https://")):
        u = "https://" + u

    parsed = urlparse(u)
    host = parsed.netloc.lower()

    # Remove credentials if any (user:pass@host)
    if "@" in host:
        host = host.split("@")[-1]

    # Remove port if any
    if ":" in host:
        host = host.split(":")[0]

    return {"normalized_url": u, "host": host}


# -----------------------------
# Manual URL phishing checks
# -----------------------------
SUSPICIOUS_TLDS = {".zip", ".top", ".xyz", ".click", ".loan", ".tk", ".ml", ".ga", ".cf", ".gq"}
BRAND_KEYWORDS = [
    "google", "gmail", "microsoft", "office", "outlook", "apple", "icloud",
    "facebook", "instagram", "whatsapp", "telegram", "amazon", "flipkart",
    "netflix", "paypal", "bank", "sbi", "hdfc", "icici"
]


def manual_phishing_check(url: str) -> Dict[str, Any]:
    score = 0
    reasons = []

    info = extract_domain(url)
    u = info["normalized_url"].lower()
    host = info["host"]

    if u.startswith("http://"):
        score += 15
        reasons.append("URL uses HTTP instead of HTTPS")

    if "@" in url:
        score += 20
        reasons.append("URL contains '@' (can hide real domain)")

    if len(u) > 120:
        score += 10
        reasons.append("Very long URL")

    for tld in SUSPICIOUS_TLDS:
        if host.endswith(tld):
            score += 10
            reasons.append(f"Suspicious TLD detected: {tld}")
            break

    try:
        ipaddress.ip_address(host)
        score += 25
        reasons.append("IP address used instead of a domain name")
    except Exception:
        pass

    if host.count("-") >= 3:
        score += 10
        reasons.append("Too many hyphens in domain")

    shorteners = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "cutt.ly"}
    if host in shorteners:
        score += 20
        reasons.append("URL shortener detected")

    if any(b in u for b in BRAND_KEYWORDS) and any(k in u for k in ["login", "verify", "secure", "update"]):
        official_safe = any(
            host.endswith(x)
            for x in ["google.com", "microsoft.com", "apple.com", "amazon.com", "paypal.com"]
        )
        if not official_safe:
            score += 25
            reasons.append("Possible brand impersonation + login/verify keywords")
        else:
            score += 5
            reasons.append("Brand keyword found but domain looks official")

    score = min(score, 100)

    verdict = "Safe"
    if score >= 70:
        verdict = "Phishing"
    elif score >= 40:
        verdict = "Suspicious"

    return {
        "verdict": verdict,
        "risk_score": score,
        "reasons": reasons if reasons else ["No strong phishing indicators found (manual check)."],
        "domain": host
    }


# -----------------------------
# Gemini AI analysis
# -----------------------------
def gemini_analyze_url(url: str) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not found. Add it to backend/.env")

    prompt = f"""
You are a cybersecurity assistant.
Analyze this URL for phishing risk and return STRICT JSON only.

URL: {url}

Return JSON in this format:
{{
  "verdict": "Safe" | "Suspicious" | "Phishing",
  "risk_score": 0-100,
  "reasons": ["reason1", "reason2", "reason3"]
}}

Rules:
- No markdown
- No extra text
- reasons must be an array of strings
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    r = requests.post(GEMINI_API_URL, json=payload, timeout=20)

    if r.status_code != 200:
        raise RuntimeError(f"Google API Error {r.status_code}: {r.text}")

    data = r.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        raise RuntimeError(f"Unexpected Gemini response format: {data}")

    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if not json_match:
        raise RuntimeError(f"Gemini did not return JSON: {text}")

    parsed = json.loads(json_match.group(0))

    verdict = parsed.get("verdict", "Suspicious")
    risk_score = int(parsed.get("risk_score", 50))
    reasons = parsed.get("reasons", [])

    if verdict not in ["Safe", "Suspicious", "Phishing"]:
        verdict = "Suspicious"

    risk_score = max(0, min(risk_score, 100))

    if not isinstance(reasons, list) or not reasons:
        reasons = ["AI analysis returned unclear reasons."]

    return {"verdict": verdict, "risk_score": risk_score, "reasons": reasons}


# -----------------------------
# Debug route: list available models
# -----------------------------
@app.get("/debug/models")
def debug_models():
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY not found in .env"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        return {"status": r.status_code, "error": r.text}

    data = r.json()

    models = []
    for m in data.get("models", []):
        methods = m.get("supportedGenerationMethods", [])
        if "generateContent" in methods:
            models.append({
                "name": m.get("name"),
                "displayName": m.get("displayName"),
                "methods": methods
            })

    return {"supported_models": models}


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def home():
    return {
        "status": "PhishGuard backend running",
        "model": MODEL_NAME,
        "ai_enabled": bool(GEMINI_API_KEY)
    }


@app.get("/history")
def get_history():
    return load_history()


@app.delete("/history")
def clear_history():
    save_history([])
    return {"status": "cleared"}


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    url = req.url.strip()
    print(f"Analyzing: {url}")

    used_ai = False
    error_msg = None

    try:
        result = gemini_analyze_url(url)
        used_ai = True
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ AI Failed - Using Manual Logic\n{error_msg}")
        result = manual_phishing_check(url)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "used_ai": used_ai,
        "model": MODEL_NAME if used_ai else None,
        "result": result
    }

    if error_msg:
        entry["ai_error"] = error_msg

    add_to_history(entry)
    return entry


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
