import asyncio
from datetime import datetime
from typing import List

import httpx
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import os

from indicators import generate_signals
from alerts import AlertHub

load_dotenv()

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000").split(",")

app = FastAPI(title="Crypto AI Dashboard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# symbols mapped to CoinGecko ids
SYMBOLS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "MATIC": "matic-network"
}

alert_hub = AlertHub()

class PricePoint(BaseModel):
    ts: datetime
    price: float

class SignalResponse(BaseModel):
    signal: str
    reasons: List[str]
    trend: str
    rsi: float | None
    zscore: float | None
    sentiment: dict

@app.get("/api/news")
async def get_news():
    API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={API_KEY}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

@app.get("/symbols")
def list_symbols():
    return {"symbols": list(SYMBOLS.keys())}

@app.get("/price/{symbol}")
async def get_price(symbol: str):
    symbol = symbol.upper()
    cg_id = SYMBOLS.get(symbol)
    if not cg_id:
        return {"error": "Unsupported symbol"}
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url)
        data = r.json()
    return {"symbol": symbol, "usd": data.get(cg_id, {}).get("usd")}

@app.get("/ohlc/{symbol}")
async def get_ohlc(symbol: str, days: int = 1):
    symbol = symbol.upper()
    cg_id = SYMBOLS.get(symbol)
    if not cg_id:
        return {"error": "Unsupported symbol"}
    url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=usd&days={days}&interval=hourly"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        data = r.json()
    prices = data.get("prices", [])
    series = [PricePoint(ts=datetime.fromtimestamp(p[0]/1000.0), price=p[1]) for p in prices]
    return {"symbol": symbol, "series": [s.dict() for s in series]}

@app.get("/signal/{symbol}", response_model=SignalResponse)
async def signal(symbol: str, days: int = 2):
    symbol = symbol.upper()
    cg_id = SYMBOLS.get(symbol)
    if not cg_id:
        return {"error": "Unsupported symbol"}
    url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=usd&days={days}&interval=hourly"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        data = r.json()
    prices = data.get("prices", [])
    if not prices:
        return {"signal": "HOLD", "reasons": ["No data"], "trend": "Unknown", "rsi": None, "zscore": None, "sentiment": {"positive":0,"negative":0,"neutral":100}}
    df = pd.DataFrame(prices, columns=["ts", "price"])
    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    out = generate_signals(df)
    return out
# =========================
# Learning Section API
# =========================

class Lesson(BaseModel):
    id: int
    title: str
    category: str  # "stock", "crypto", "finance"
    content: str
    contentPreview: str

# Mock lessons (you can expand later)
LESSONS = [
    Lesson(
        id=1,
        title="Introduction to Stock Market",
        category="stock",
        content="The stock market is where buyers and sellers trade shares of companies. It is essential for investment and wealth creation.",
        contentPreview="Learn the basics of how the stock market works..."
    ),
    Lesson(
        id=2,
        title="What is Cryptocurrency?",
        category="crypto",
        content="Cryptocurrency is a type of digital money that uses blockchain technology to secure transactions and control supply.",
        contentPreview="Understand the fundamentals of crypto and blockchain..."
    ),
    Lesson(
        id=3,
        title="Personal Finance Basics",
        category="finance",
        content="Personal finance involves managing your income, expenses, savings, and investments to secure your financial future.",
        contentPreview="Start learning how to manage your money wisely..."
    ),
]

@app.get("/api/lessons", response_model=List[Lesson])
async def get_lessons():
    return LESSONS

@app.get("/api/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(lesson_id: int):
    for lesson in LESSONS:
        if lesson.id == lesson_id:
            return lesson
    return {"error": "Lesson not found"}

@app.post("/api/lessons", response_model=Lesson)
async def add_lesson(lesson: Lesson):
    LESSONS.append(lesson)
    return lesson


# New endpoint to get Binance market data
@app.get("/binance/price/{symbol}")
async def get_binance_price(symbol: str):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol.upper()}"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url)
        if response.status_code != 200:
            return {"error": "Failed to fetch data from Binance"}
        data = response.json()
    return {
        "symbol": data.get("symbol"),
        "price": data.get("lastPrice"),
        "priceChangePercent": data.get("priceChangePercent"),
        "highPrice": data.get("highPrice"),
        "lowPrice": data.get("lowPrice"),
        "volume": data.get("volume")
    }

# WebSocket for live alerts (client subscribes with symbol/target/stop)
@app.websocket("/ws/alerts")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            sub = await ws.receive_json()
            print("Received subscription:", sub)

            # Example: forward subscription to your AlertHub
            await alert_hub.handle_subscription(ws, sub)

    except WebSocketDisconnect:
        print("Client disconnected")
        await alert_hub.remove(ws)
    except Exception as e:
        print("WebSocket error:", e)
        await ws.close(code=1000)
