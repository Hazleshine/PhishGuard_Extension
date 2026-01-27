🛡️ PhishGuard AI

AI-Driven Phishing Detection Chrome Extension

PhishGuard AI is a full-stack cybersecurity project designed to detect phishing threats in real time using a combination of AI-based analysis and rule-based security heuristics.
The system integrates a cloud-hosted FastAPI backend with a Chrome Extension (Manifest V3) that works reliably on modern, dynamic websites such as Gmail.

This project focuses on real-world security constraints, including browser sandboxing, CORS policies, and AI rate limits.

🚀 Key Capabilities

🔍 Real-time phishing risk analysis for active web pages

🤖 AI-powered URL inspection using Google Gemini

🧠 Rule-based fallback detection when AI is unavailable

📧 Gmail-compatible warning banner (SPA-aware)

☁️ Secure cloud backend deployed on Render

🔐 Server-side API key protection

📊 Scan history logging for analysis and debugging

🧱 System Architecture
Chrome Extension (Manifest V3)
 ├── content.js        → UI banner injection (Gmail-safe)
 ├── background.js     → Secure backend communication
 └── manifest.json     → Permissions & service worker
        |
        v
FastAPI Backend (Render Cloud)
 ├── Manual phishing heuristics
 ├── Google Gemini AI integration
 ├── History persistence
 └── REST API endpoints

Design Rationale

Network requests are handled by a background service worker to bypass browser loopback and CORS restrictions

API keys remain fully isolated on the backend

Gmail’s dynamic DOM is handled using SPA-aware observers

🛠️ Technology Stack
Frontend (Chrome Extension)

JavaScript (Chrome Extension Manifest V3)

MutationObserver for SPA navigation

Secure message-passing architecture

Backend

Python + FastAPI

Google Gemini API

Requests, Pydantic

Cloud deployment via Render (Free Tier)

🌐 Deployed Backend

Base URL:

https://phishguard-backend-upyk.onrender.com

Available Endpoints

GET / – Service health check

POST /analyze – Analyze a URL for phishing risk

GET /history – Retrieve scan history

📦 Local Setup
Backend
cd backend
pip install -r requirements.txt
python main.py


Create a .env file:

GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash

Chrome Extension

Open chrome://extensions

Enable Developer Mode

Click Load unpacked

Select the extension/ directory

Visit any website or open Gmail to view alerts

🧪 Detection Methodology
Manual Heuristic Analysis

HTTPS enforcement checks

Suspicious top-level domains

IP-based URLs

URL length and obfuscation patterns

Brand impersonation indicators

AI-Based Analysis

Context-aware phishing classification

Risk scoring from 0–100

Human-readable explanation of verdict

If the AI service is temporarily unavailable, the system automatically falls back to manual detection logic.

⚠️ Known Limitations

Render free tier may introduce cold-start delays

Google Gemini free tier has daily request limits

Extension is not yet published on the Chrome Web Store

These limitations are documented intentionally to reflect real production constraints.

📈 Planned Enhancements

VirusTotal reputation integration

External link scanning inside email bodies

Chrome Web Store publication

Advanced threat intelligence feeds

User-level analytics dashboard

👩‍💻 Author

Sana Yasmine
Cybersecurity & Software Engineering


GitHub: https://github.com/Hazleshine