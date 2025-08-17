from typing import Dict, List

class AlertHub:
    """In-memory alert subscriptions. For production, use Redis or DB."""
    def __init__(self):
        # {symbol: [{"target": float, "stop": float, "ws": websocket}]}
        self.subscribers: Dict[str, List[dict]] = {}

    def add(self, symbol: str, target: float, stop: float, ws) -> None:
        symbol = symbol.upper()
        self.subscribers.setdefault(symbol, []).append({
            "target": target, "stop": stop, "ws": ws
        })

    async def publish(self, symbol: str, price: float):
        symbol = symbol.upper()
        if symbol not in self.subscribers:
            return
        to_keep = []
        for sub in self.subscribers[symbol]:
            target = sub["target"]
            stop = sub["stop"]
            ws = sub["ws"]
            try:
                if price >= target:
                    await ws.send_json({"type": "ALERT", "event": "TARGET_HIT", "symbol": symbol, "price": price})
                elif price <= stop:
                    await ws.send_json({"type": "ALERT", "event": "STOP_LOSS", "symbol": symbol, "price": price})
                else:
                    to_keep.append(sub)
            except Exception:
                # client likely disconnected
                pass
        self.subscribers[symbol] = to_keep