import json
from kafka import KafkaConsumer, KafkaProducer
from collections import deque
import numpy as np
from datetime import datetime, timezone

# ==========================
# CONFIG
# ==========================
PRICE_TOPIC = "market_prices"
RISK_TOPIC = "risk_events"

WINDOW = 50          # rolling price window
VOL_WINDOW = 50      # rolling volatility window

prices = deque(maxlen=WINDOW)
vol_history = deque(maxlen=VOL_WINDOW)

# ==========================
# KAFKA CONSUMER
# ==========================
consumer = KafkaConsumer(
    PRICE_TOPIC,
    bootstrap_servers="localhost:9092",
    auto_offset_reset="latest",
    group_id="risk-engine",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

# ==========================
# KAFKA PRODUCER
# ==========================
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("🧠 Real-Time Risk Engine started...")

# ==========================
# MAIN LOOP
# ==========================
for msg in consumer:
    event = msg.value
    price = event["price"]

    prices.append(price)

    if len(prices) < WINDOW:
        continue

    # --------------------------
    # Compute returns & volatility
    # --------------------------
    returns = np.diff(np.log(prices))
    volatility = float(np.std(returns))
    vol_history.append(volatility)

    if len(vol_history) < VOL_WINDOW:
        continue

    # --------------------------
    # Adaptive baseline
    # --------------------------
    mean_vol = np.mean(vol_history)
    std_vol = np.std(vol_history)

    z_score = 0 if std_vol == 0 else (volatility - mean_vol) / std_vol

    # --------------------------
    # Risk classification
    # --------------------------
    if z_score < 1:
        risk_level = "LOW"
    elif z_score < 2:
        risk_level = "MEDIUM"
    elif z_score < 3:
        risk_level = "HIGH"
    else:
        risk_level = "EXTREME"

    # --------------------------
    # Emit risk event
    # --------------------------
    risk_event = {
        "asset": event["asset"],
        "price": price,
        "volatility": round(volatility, 8),
        "z_score": round(z_score, 2),
        "risk_level": risk_level,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": event["source"]
    }

    producer.send(RISK_TOPIC, risk_event)

    print(
        f"🚨 Risk Event | "
        f"Price={price} | "
        f"Vol={volatility:.8f} | "
        f"Z={z_score:.2f} | "
        f"Risk={risk_level}"
    )
