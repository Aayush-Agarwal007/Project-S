from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import json
import os
from typing import List, Dict, Any
import time
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API Keys from environment
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')

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

# AI Recommendation Functions
def analyze_portfolio_sentiment(portfolio: Dict) -> Dict:
    """Analyze sentiment for portfolio holdings"""
    symbols = list(portfolio.keys())
    sentiment_scores = {}
    
    for symbol in symbols:
        # In a real implementation, this would use a proper sentiment analysis API
        # For demo purposes, we'll generate random sentiment scores
        sentiment_scores[symbol] = {
            'score': random.uniform(0.1, 0.9),
            'trend': random.choice(['bullish', 'bearish', 'neutral'])
        }
    
    return sentiment_scores

def generate_ai_recommendations(portfolio_data: Dict) -> List[Dict]:
    """Generate AI-powered recommendations based on portfolio data"""
    recommendations = []
    
    # Sample recommendations (in a real app, these would come from ML models)
    sample_recommendations = [
        {
            "title": "Diversify Portfolio",
            "description": "Your portfolio is heavily weighted towards large caps. Consider adding some mid-cap assets for better diversification.",
            "priority": "medium",
            "action": {
                "type": "suggest_diversification",
                "symbol": "MIDCAP",
                "label": "View Mid-Cap Options"
            }
        },
        {
            "title": "Profit Taking Opportunity",
            "description": "BTC has gained 15% in the last week. Consider taking some profits.",
            "priority": "high",
            "action": {
                "type": "sell",
                "symbol": "BTC",
                "label": "Sell 25% of BTC"
            }
        },
        {
            "title": "Rebalance Suggested",
            "description": "Your ETH allocation is below target. Consider adding to your position.",
            "priority": "medium",
            "action": {
                "type": "buy",
                "symbol": "ETH",
                "label": "Buy More ETH"
            }
        }
    ]
    
    # Select 2-3 random recommendations for demo purposes
    num_recommendations = random.randint(2, 3)
    selected_recommendations = random.sample(sample_recommendations, num_recommendations)
    
    return selected_recommendations
# Add to your Flask app
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def home():
    return jsonify({"message": "Crypto Portfolio API with AI Features", "status": "active"})

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

# AI Recommendation Endpoints
@app.route('/ai/sentiment')
def get_portfolio_sentiment():
    """Endpoint to get sentiment analysis for portfolio holdings"""
    # Get portfolio data from query parameters
    portfolio_json = request.args.get('portfolio', '{}')
    
    try:
        portfolio = json.loads(portfolio_json)
        sentiment_scores = analyze_portfolio_sentiment(portfolio)
        return jsonify(sentiment_scores)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid portfolio data"}), 400

@app.route('/ai/recommendations')
def get_ai_recommendations():
    """Endpoint to get AI-powered portfolio recommendations"""
    # Get portfolio data from query parameters
    portfolio_json = request.args.get('portfolio', '{}')
    balance = request.args.get('balance', default=10000, type=float)
    
    try:
        portfolio = json.loads(portfolio_json)
        portfolio_data = {
            "holdings": portfolio,
            "balance": balance
        }
        
        recommendations = generate_ai_recommendations(portfolio_data)
        return jsonify(recommendations)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid portfolio data"}), 400

@app.route('/api/news')
def get_crypto_news():
    """Endpoint to fetch crypto news from News API"""
    if not NEWS_API_KEY:
        return jsonify({"error": "News API key not configured"}), 500
    
    try:
        url = f"https://newsapi.org/v2/everything?q=cryptocurrency&sortBy=publishedAt&pageSize=20&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return jsonify({"error": "Failed to fetch news"}), 500

if __name__ == '__main__':
    print("Starting CryptoSense AI Backend...")
    print(f"News API configured: {'Yes' if NEWS_API_KEY else 'No'}")
    app.run(debug=True, port=8000)