import json
from kafka import KafkaProducer
from datetime import datetime, timezone
import websocket
import time

KAFKA_TOPIC = "market_prices"

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    api_version=(3, 6, 0),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

last_emit = 0
BUFFER = []

def on_message(ws, message):
    global last_emit, BUFFER

    data = json.loads(message)
    price = float(data["p"])
    BUFFER.append(price)

    now = time.time()

    # Emit once per second
    if now - last_emit >= 1:
        avg_price = sum(BUFFER) / len(BUFFER)
        BUFFER.clear()
        last_emit = now

        event = {
            "asset": "BTC",
            "source": "binance",
            "price": avg_price,
            "currency": "USDT",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        producer.send(KAFKA_TOPIC, event)
        print("📤 Sent (1s bar):", event)

def on_error(ws, error):
    print("❌ WebSocket error:", error)

def on_close(ws):
    print("🔌 WebSocket closed")

def on_open(ws):
    print("✅ Connected to Binance WebSocket")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@trade",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()
