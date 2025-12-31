import boto3
import json
import pandas as pd
from datetime import datetime, timezone
from sklearn.ensemble import IsolationForest

# ==========================
# CONFIG
# ==========================
BUCKET_NAME = "real-time-risk-data-joel-2025"
ASSET_NAME = "bitcoin"

s3 = boto3.client("s3")


# ==========================
# LOAD PROCESSED DATA
# ==========================
def load_processed_data(year, month, day):
    key = (
        f"processed/{ASSET_NAME}/"
        f"year={year}/month={month:02d}/day={day:02d}/"
        f"processed_data.json"
    )

    obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    data = json.loads(obj["Body"].read())
    return pd.DataFrame(data)


# ==========================
# RISK METRICS
# ==========================
def calculate_risk_metrics(df):
    df["moving_avg"] = df["price_usd"].rolling(window=5).mean()
    df["volatility"] = df["price_usd"].rolling(window=5).std()
    df.fillna(0, inplace=True)
    return df


# ==========================
# ML ANOMALY DETECTION
# ==========================
def detect_anomalies(df):
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    df["anomaly"] = model.fit_predict(df[["price_usd"]])
    df["is_anomaly"] = df["anomaly"].apply(lambda x: 1 if x == -1 else 0)
    df.drop(columns=["anomaly"], inplace=True)

    return df


# ==========================
# UPLOAD RISK DATA
# ==========================
def upload_risk_data(df, year, month, day):
    key = (
        f"risk/{ASSET_NAME}/"
        f"year={year}/month={month:02d}/day={day:02d}/"
        f"risk_metrics.json"
    )

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=df.to_json(orient="records", indent=2),
        ContentType="application/json"
    )

    print(f"✅ Risk metrics uploaded to s3://{BUCKET_NAME}/{key}")


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    today = datetime.now(timezone.utc)

    year, month, day = today.year, today.month, today.day

    print("📥 Loading processed data...")
    df = load_processed_data(year, month, day)

    print("📊 Calculating risk metrics...")
    df = calculate_risk_metrics(df)

    print("🤖 Detecting anomalies...")
    df = detect_anomalies(df)

    upload_risk_data(df, year, month, day)
