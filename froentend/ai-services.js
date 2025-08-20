// Simple AI logic for buy/sell signals
function generateAISignal(symbol, priceData) {
  // Simple moving average strategy
  if (priceData.length < 10) return null;
  
  const shortPeriod = 5;
  const longPeriod = 10;
  
  // Calculate short and long moving averages
  const shortMA = calculateMA(priceData, shortPeriod);
  const longMA = calculateMA(priceData, longPeriod);
  
  const currentShort = shortMA[shortMA.length - 1];
  const currentLong = longMA[longMA.length - 1];
  const prevShort = shortMA[shortMA.length - 2];
  const prevLong = longMA[longMA.length - 2];
  
  // Buy signal: short MA crosses above long MA
  if (prevShort <= prevLong && currentShort > currentLong) {
    return {
      action: 'BUY',
      symbol: symbol,
      confidence: 0.7,
      message: `Buy ${symbol}: Short-term trend turning bullish`
    };
  }
  
  // Sell signal: short MA crosses below long MA
  if (prevShort >= prevLong && currentShort < currentLong) {
    return {
      action: 'SELL',
      symbol: symbol,
      confidence: 0.6,
      message: `Sell ${symbol}: Short-term trend turning bearish`
    };
  }
  
  return null;
}

// Calculate moving average
function calculateMA(data, period) {
  const result = [];
  for (let i = period - 1; i < data.length; i++) {
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close;
    }
    result.push(sum / period);
  }
  return result;
}