# CryptoSense AI

CryptoSense AI is a crypto market dashboard project with a Python backend and a multi-page HTML/Tailwind frontend.

It provides real-time-ish market views, chart-based exploration, news feeds, portfolio/demo trading interfaces, and basic AI-style recommendation endpoints.

## Features

- Live market data from Binance symbols (BTC, ETH, BNB, SOL, ADA, XRP)
- Historical OHLC series endpoint for charting
- Market overview table with 24h change and volume
- News page powered by News API
- Demo trading and portfolio-style UI pages
- AI-style sentiment and recommendation endpoints (demo logic)
- Utility modules for indicators and encrypted value handling

## Tech Stack

- Backend: Python, Flask, Flask-CORS, Requests
- Frontend: HTML, TailwindCSS, Chart.js, Axios
- Integrations: Binance public API, News API, Firebase

## Project Structure

```text
CryptoDash-/
	backend/
		main.py
		indicators.py
		alerts.py
		security.py
		requirements.txt
	froentend/
		index.html
		market.html
		realtime.html
		news.html
		demo.html
		portfolio.html
		learn.html
		auth.html
		ai-services.js
		notifications.js
		firebase-messaging-sw.js
	scripts/
		generate_key.py
	.env              # Environment variables (not committed)
	.gitignore
	readme.md
```

## Prerequisites

- Python 3.10+
- pip
- A modern browser

## Quick Start

1. Open the project folder:

```powershell
cd "C:\Users\asus\OneDrive\Desktop\portfolio\CryptoDash-"
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install backend dependencies:

```powershell
pip install -r backend\requirements.txt
```

4. Set up environment variables:

```powershell
copy .env.example .env
# Edit .env with your API keys
```

5. Start backend API server:

```powershell
python backend\main.py
```

Backend runs on `http://127.0.0.1:8000`.

6. Serve frontend files from the `froentend` folder:

```powershell
cd froentend
python -m http.server 5500
```

Then open `http://127.0.0.1:5500/index.html`.

## API Endpoints

- `GET /` : health/info message
- `GET /binance/price/<symbol>` : single ticker snapshot
- `GET /ohlc/<symbol>?days=1` : historical close series
- `GET /market/overview` : dashboard symbols overview
- `GET /ai/sentiment?portfolio=<json>` : demo sentiment scores
- `GET /ai/recommendations?portfolio=<json>&balance=10000` : demo recommendations

## Environment Variables

Create a `.env` file with:

```
NEWS_API_KEY=your_newsapi_key
FIREBASE_API_KEY=your_firebase_key
FLASK_SECRET_KEY=generate_with_scripts/generate_key.py
```

## License

MIT


