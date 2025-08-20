# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import requests
import json
from typing import List, Dict, Any
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Binance API base URL
BINANCE_API_BASE = "https://api.binance.com/api/v3"

def get_binance_ticker(symbol: str) -> Dict[str, Any]:
    """Get ticker data for a specific symbol from Binance"""
    try:
        response = requests.get(f"{BINANCE_API_BASE}/ticker/24hr?symbol={symbol}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ticker data for {symbol}: {e}")
        return None

def get_klines_data(symbol: str, interval: str = "1h", limit: int = 24) -> List[Dict]:
    """Get OHLC data for a specific symbol from Binance"""
    try:
        response = requests.get(f"{BINANCE_API_BASE}/klines?symbol={symbol}&interval={interval}&limit={limit}")
        response.raise_for_status()
        klines = response.json()
        
        # Format the response to match what the frontend expects
        formatted_data = []
        for kline in klines:
            formatted_data.append({
                "ts": kline[0],
                "price": float(kline[4])  # Use closing price
            })
        return formatted_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching klines data for {symbol}: {e}")
        return []

@app.route('/')
def home():
    return jsonify({"message": "Binance Market Data API", "status": "active"})

@app.route('/binance/price/<symbol>')
def get_price(symbol):
    """Endpoint to get price data for a specific symbol"""
    ticker_data = get_binance_ticker(symbol)
    if not ticker_data:
        return jsonify({"error": "Failed to fetch data from Binance"}), 500
    
    # Format the response to match what the frontend expects
    formatted_data = {
        "symbol": ticker_data["symbol"],
        "price": ticker_data["lastPrice"],
        "priceChange": ticker_data["priceChange"],
        "priceChangePercent": ticker_data["priceChangePercent"],
        "volume": ticker_data["volume"]
    }
    return jsonify(formatted_data)

@app.route('/ohlc/<symbol>')
def get_ohlc(symbol):
    """Endpoint to get OHLC data for a specific symbol"""
    # Get days parameter from query string, default to 1
    days = request.args.get('days', default=1, type=int)
    
    # Calculate appropriate limit based on days (assuming 24 data points per day)
    limit = days * 24
    
    klines_data = get_klines_data(symbol, limit=limit)
    if not klines_data:
        return jsonify({"error": "Failed to fetch OHLC data from Binance"}), 500
    
    return jsonify({"symbol": symbol, "series": klines_data})

@app.route('/market/overview')
def get_market_overview():
    """Endpoint to get data for multiple cryptocurrencies at once"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 'XRPUSDT']
    market_data = []
    
    for symbol in symbols:
        ticker_data = get_binance_ticker(symbol)
        if ticker_data:
            market_data.append({
                "symbol": ticker_data["symbol"],
                "price": ticker_data["lastPrice"],
                "priceChange": ticker_data["priceChange"],
                "priceChangePercent": ticker_data["priceChangePercent"],
                "volume": ticker_data["volume"]
            })
    
    return jsonify(market_data)

if __name__ == '__main__':
    app.run(debug=True, port=8000)