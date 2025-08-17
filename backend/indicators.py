import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(gain).rolling(period).mean()
    roll_down = pd.Series(loss).rolling(period).mean()
    rs = roll_up / (roll_down + 1e-9)
    return 100.0 - (100.0 / (1.0 + rs))


def zscore(series: pd.Series, window: int = 30) -> pd.Series:
    roll_mean = series.rolling(window).mean()
    roll_std = series.rolling(window).std(ddof=0)
    return (series - roll_mean) / (roll_std + 1e-9)


def generate_signals(df: pd.DataFrame) -> dict:
    """
    Expects df with columns: ['ts', 'price'] where ts is datetime-like.
    Returns a dict with AI-ish signals.
    """
    df = df.copy()
    df['sma_fast'] = sma(df['price'], 10)
    df['sma_slow'] = sma(df['price'], 30)
    df['rsi'] = rsi(df['price'], 14)
    df['z'] = zscore(df['price'], 30)

    signal = "HOLD"
    reasons = []

    if len(df) >= 30:
        if df['sma_fast'].iloc[-1] > df['sma_slow'].iloc[-1] and df['rsi'].iloc[-1] < 70:
            signal = "BUY"
            reasons.append("SMA fast crossed above SMA slow & RSI < 70")
        elif df['sma_fast'].iloc[-1] < df['sma_slow'].iloc[-1] and df['rsi'].iloc[-1] > 30:
            signal = "SELL"
            reasons.append("SMA fast below SMA slow & RSI > 30")

        if abs(df['z'].iloc[-1]) > 2:
            reasons.append(f"Anomaly detected (|z| > 2): {df['z'].iloc[-1]:.2f}")

    # Market condition (simple):
    trend = "Sideways"
    last_fast = df['sma_fast'].iloc[-1] if not pd.isna(df['sma_fast'].iloc[-1]) else None
    last_slow = df['sma_slow'].iloc[-1] if not pd.isna(df['sma_slow'].iloc[-1]) else None
    if last_fast and last_slow:
        if last_fast > last_slow:
            trend = "Uptrend"
        elif last_fast < last_slow:
            trend = "Downtrend"

    # Sentiment proxy (price momentum last N points)
    lookback = min(20, len(df)-1) if len(df) > 1 else 1
    pos = (df['price'].diff().tail(lookback) > 0).sum()
    neg = (df['price'].diff().tail(lookback) < 0).sum()
    total = max(1, pos + neg)
    sentiment = {
        "positive": round(100 * pos / total, 1),
        "negative": round(100 * neg / total, 1),
        "neutral": round(100 * (1 - (pos + neg) / max(1, lookback)), 1)
    }

    return {
        "signal": signal,
        "reasons": reasons,
        "trend": trend,
        "rsi": None if pd.isna(df['rsi'].iloc[-1]) else round(float(df['rsi'].iloc[-1]), 2),
        "zscore": None if pd.isna(df['z'].iloc[-1]) else round(float(df['z'].iloc[-1]), 2),
        "sentiment": sentiment
    }