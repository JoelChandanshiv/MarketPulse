import json
import joblib
import pandas as pd
from collections import deque
from kafka import KafkaConsumer, KafkaProducer

from ml.features.build_features import build_features

# =========================
# CONFIG
# =========================
MODEL_PATH = "ml/models/isolation_forest.joblib"
BROKER = "localhost:9092"
PRICE_WINDOW = 30
FEATURE_COLUMNS = [
    "log_return",
    "volatility_10",
    "volatility_30",
    "z_score",
    "momentum_10"
]

# =========================
# LOAD MODEL
# =========================
model = joblib.load(MODEL_PATH)
print("🤖 ML model loaded")

# =========================
# KAFKA
# =========================
consumer = KafkaConsumer(
    "market_prices",
    bootstrap_servers=BROKER,
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# =========================
# STATE
# =========================
price_buffer = deque(maxlen=PRICE_WINDOW)

print("🚀 Real-time ML inference started")

# =========================
# STREAM LOOP
# =========================
for msg in consumer:
    price = float(msg.value["price"])
    price_buffer.append(price)

    # wait until we have enough prices
    if len(price_buffer) < PRICE_WINDOW:
        continue

    # 1️⃣ Build dataframe from rolling window
    df = pd.DataFrame({"price": list(price_buffer)})
    features_df = build_features(df)

    if features_df.empty:
        continue

    latest_features = features_df[
        ["log_return", "volatility_10", "volatility_30", "z_score", "momentum_10"]
    ].iloc[-1:]

    prediction = model.predict(latest_features)[0]
    score = model.decision_function(latest_features)[0]

    if prediction == -1:
        alert = {
            "asset": "BTC",
            "price": price,
            "risk": "ANOMALY",
            "score": float(score)
        }
        producer.send("risk_alerts", alert)
        print("🚨 ANOMALY DETECTED:", alert)
