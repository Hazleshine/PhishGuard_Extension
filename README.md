# 🛡️ PhishGuard AI
### AI-Driven Phishing Detection Chrome Extension

PhishGuard AI is a full-stack cybersecurity project that detects phishing risks in real time using a combination of **AI-based analysis** and **rule-based security heuristics**.  
It integrates a **Chrome Extension (Manifest V3)** with a **cloud-deployed FastAPI backend**, and is designed to work reliably on modern dynamic platforms such as **Gmail**.

This project focuses on **real-world security constraints**, including browser sandboxing, CORS restrictions, secure API key handling, and AI rate-limit management.

---

## 🚀 Key Features

- 🔍 Real-time phishing detection for active web pages  
- 🤖 AI-powered URL analysis using **Google Gemini**  
- 🧠 Manual heuristic-based fallback detection  
- 📧 Gmail-safe warning banner injection (SPA-aware)  
- ☁️ Secure cloud backend deployment (Render)  
- 🔐 API keys protected on the server side  
- 📊 Scan history logging for transparency and debugging  

---

## 🧱 System Architecture

### High-Level Workflow

```mermaid
flowchart LR
    A[User Browses Website / Gmail] --> B[content.js]
    B --> C[background.js]
    C --> D[FastAPI Backend]
    D --> E[Gemini AI]
    D --> F[Manual Heuristics]
    E --> G[Risk Verdict]
    F --> G[Risk Verdict]
    G --> B
Architecture Explanation

content.js injects phishing warning banners into the page

background.js securely communicates with the backend API

FastAPI backend performs phishing analysis

Gemini AI provides intelligent risk classification

Manual heuristics act as a fallback when AI is unavailable

This architecture:

Avoids CORS and browser sandbox limitations

Keeps sensitive API keys out of the extension

Works reliably on Single Page Applications (SPAs) like Gmail

Follows industry-standard Chrome extension design patterns

🛠️ Technology Stack
Frontend (Chrome Extension)

JavaScript

Chrome Extension (Manifest V3)

MutationObserver for SPA navigation

Secure message-passing architecture

Backend

Python

FastAPI

Google Gemini API

Requests, Pydantic

Cloud

Render (Free Tier)

🌐 Live Backend

Base URL

https://phishguard-backend-upyk.onrender.com

Available Endpoints
GET  /          → Health check
POST /analyze   → Analyze a URL
GET  /history   → View scan history

📦 Local Setup
Backend Setup
cd backend
pip install -r requirements.txt
python main.py


Create a .env file inside backend/:

GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash

Chrome Extension Setup

Open chrome://extensions

Enable Developer Mode

Click Load unpacked

Select the extension/ folder

Visit any website or open Gmail to view phishing alerts

🧪 Detection Methodology
Manual Heuristic Checks

HTTPS enforcement

Suspicious top-level domains

IP-based URLs

URL length and obfuscation patterns

Brand impersonation indicators

AI-Based Analysis

Context-aware phishing detection

Risk score from 0–100

Human-readable explanation for each verdict

If the AI service is unavailable or rate-limited, the system automatically falls back to manual detection logic.

⚠️ Known Limitations

Render free tier may introduce cold-start delays

Google Gemini free tier has daily request limits

Chrome Web Store publication is not yet completed

These limitations are documented intentionally to reflect real production environments.

📈 Future Enhancements

VirusTotal reputation integration

Email body and embedded link analysis

Chrome Web Store deployment

Threat-intelligence feeds

User analytics dashboard

👩‍💻 Author

Sana Yasmine
Cybersecurity & Software Engineering
Final-Year Capstone Project

🔗 GitHub: https://github.com/Hazleshine

⭐ Project Significance

PhishGuard AI demonstrates:

Secure Chrome extension architecture

Practical AI integration with graceful degradation

Cloud-native backend deployment

Awareness of real-world browser and security constraints

This project is built using production-oriented engineering principles, not tutorial shortcuts.