# PhishGuard AI 🛡️

License: MIT — see [LICENSE](LICENSE)

AI-driven phishing detection Chrome extension (Manifest V3) with a FastAPI backend.

PhishGuard AI detects phishing risks in real time using Google Gemini + fallback manual heuristics. The design keeps API keys on the server, avoids browser CORS/sandboxing issues, and works reliably w[...]

Live backend: https://phishguard-backend-upyk.onrender.com

---

## Table of Contents
- [Features](#features)
- [Demo / Screenshots](#demo--screenshots)
- [Architecture](#architecture)
- [API (Endpoints)](#api-endpoints)
- [Local Setup](#local-setup)
  - [Backend](#backend)
  - [Chrome extension](#chrome-extension)
- [Detection Methodology](#detection-methodology)
- [Known Limitations & Troubleshooting](#known-limitations--troubleshooting)
- [Roadmap / Future Enhancements](#roadmap--future-enhancements)
- [Contributing](#contributing)
- [License & Author](#license--author)

---

## Features
- Real-time phishing risk detection for active web pages
- AI-powered URL/context analysis via Google Gemini
- Heuristic fallback detection if AI is unavailable
- Gmail-safe warning banner injection (SPA-aware using MutationObserver)
- Scan history logging for transparency
- Secure architecture: API keys kept server-side

---

## Demo / Screenshots

Included screenshots (placed in assets/screenshots/):
- assets/screenshots/screenshot1.png — Extension panel on a suspicious movie-streaming site
- assets/screenshots/screenshot2.png — Injected warning banner inside Gmail (SPA-aware)
- assets/screenshots/screenshot3.png — Backend Swagger / API docs (intel endpoints)

Below are the three screenshots displayed with captions. If you prefer side-by-side thumbnails, we can switch to a two- or three-column layout.

<figure>
  <img src="assets/screenshots/screenshot1.png" alt="Extension panel on a suspicious movie-streaming site" width="420"/>
  <figcaption><strong>Screenshot 1:</strong> Extension panel on a suspicious movie-streaming site</figcaption>
</figure>

<figure>
  <img src="assets/screenshots/screenshot2.png" alt="Injected warning banner inside Gmail (SPA-aware)" width="420"/>
  <figcaption><strong>Screenshot 2:</strong> Injected warning banner inside Gmail (SPA-aware)</figcaption>
</figure>

<figure>
  <img src="assets/screenshots/screenshot3.png" alt="Backend Swagger / API docs (intel endpoints)" width="420"/>
  <figcaption><strong>Screenshot 3:</strong> Backend Swagger / API docs (intel endpoints)</figcaption>
</figure>

(Replace or add higher-resolution images/GIFs to this folder to improve the demo section.)

---

## Architecture

High-level flow:

flowchart LR
    A[User Browses Website or Gmail] --> B[content.js]
    B --> C[background.js]
    C --> D[FastAPI Backend]
    D --> E[Gemini AI]
    D --> F[Manual Heuristics]
    E --> G[Risk Verdict]
    F --> G[Risk Verdict]
    G --> B

- content.js injects phishing alert banners into the page.
- background.js mediates messages between the extension UI and backend.
- FastAPI backend performs analysis (AI + heuristics).
- Gemini provides context-aware scoring; heuristics run as fallback.

---

## API (Endpoints)

Base URL: https://phishguard-backend-upyk.onrender.com

- GET  /          → Health check
- POST /analyze   → Analyze a URL (request body: JSON with url and optional context)
- GET  /history   → View scan history

Example analyze request:
```bash
curl -X POST "https://phishguard-backend-upyk.onrender.com/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://example.com/login","context":"email link clicked by user@example.com"}'
```

Response (example):
```json
{
  "risk_score": 78,
  "verdict": "suspicious",
  "explanation": "Domain uses an impersonated brand + IP-based URL.",
  "heuristics": { /* details */ }
}
```

---

## Local Setup

Prerequisites:
- Python 3.10+ recommended
- Node/Chrome for extension testing
- (Optional) virtualenv or venv

Backend
1. cd backend
2. Create and activate a venv:
   - Linux/macOS: python -m venv venv && source venv/bin/activate
   - Windows: python -m venv venv && venv\Scripts\activate
3. Install dependencies:
   - pip install -r requirements.txt
4. Create a .env file in backend/ with:
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash
# any other env vars used by your app (e.g., DB, logging)
```
5. Run the app (development):
   - uvicorn main:app --reload --host 0.0.0.0 --port 8000
   - Or: python main.py (if main.py starts the app)

Note: If you rely on Render deployment-specific config, check those env values in Render dashboard.

Chrome Extension
1. Open chrome://extensions
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension/` folder (or the folder where your manifest.json lives)
5. Visit any website or Gmail to see phishing alerts

Testing the extension with the local backend
- If testing against local backend, ensure background.js points to your local backend URL, or use a small proxy. Be careful with CORS — the extension runs in the browser context, but message passing[...]

---

## Detection Methodology

Manual Heuristics (fallback)
- HTTPS / TLS enforcement
- Suspicious TLDs and brand typos
- IP-based URLs
- Long/obfuscated URL patterns
- Brand impersonation signs (homoglyphs, path-lookup tricks)

AI-Based Analysis
- Context-aware risk scoring using Google Gemini
- Risk score: 0–100 and human-readable explanation
- If AI is unavailable or rate-limited, heuristics are used automatically

---

## Known Limitations & Troubleshooting
- Render free tier may cause cold-start delays — add retries in client/backoff logic.
- Gemini free tier has daily limits — implement rate-limiting and caching of recent verdicts.
- Chrome Web Store publishing not completed — extension must be loaded unpacked for now.
- If banners do not appear in Gmail: check MutationObserver code, ensure extension has correct host permissions.
- If AI requests fail locally: verify GEMINI_API_KEY, model name, and network connectivity.

---

## Roadmap / Future Enhancements
- VirusTotal reputation checks
- Email body & embedded link analysis
- Chrome Web Store publication
- Threat-intel feeds & aggregation
- User analytics dashboard

---

## Contributing
- Open issues for bugs or feature requests
- Fork → branch → PR. Use clear commit messages and include tests if applicable.
- Add a CONTRIBUTING.md if you expect external contributors.

---

## License & Author
License: MIT — see the full text in the [LICENSE](LICENSE) file.

Author: Sana Yasmine — Final-Year Capstone Project  
GitHub: https://github.com/Hazleshine

Contributors:
- Riyaz Shaik — GitHub: https://github.com/RiyazShaik27

---

## Acknowledgements
- Google Gemini
- FastAPI
- Browser extension docs and SPA handling best practices
```
