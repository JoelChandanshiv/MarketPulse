import requests
import json
import time
from datetime import datetime, timezone
import boto3
import os

# ------------------------
# CONFIG
# ------------------------
API_URL = "https://api.coingecko.com/api/v3/simple/price"

PARAMS = {
    "ids": "bitcoin",
    "vs_currencies": "usd"
}

BUCKET_NAME = "real-time-risk-data-joel-2025"  # change to YOUR bucket
ASSET_NAME = "bitcoin"

s3 = boto3.client("s3")

# ------------------------
# FUNCTIONS
# ------------------------
def fetch_data():
    response = requests.get(API_URL, params=PARAMS)
    response.raise_for_status()
    data = response.json()

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "asset": ASSET_NAME,
        "price_usd": data[ASSET_NAME]["usd"]
    }
    return record


def upload_to_s3(record):
    timestamp = datetime.fromisoformat(record["timestamp"])

    file_name = timestamp.isoformat().replace(":", "-")

    s3_key = (
        f"raw/{ASSET_NAME}/"
        f"year={timestamp.year}/"
        f"month={timestamp.month:02d}/"
        f"day={timestamp.day:02d}/"
        f"data_{file_name}.json"
    )

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(record),
        ContentType="application/json"
    )

    print(f"Uploaded to S3: s3://{BUCKET_NAME}/{s3_key}")


# ------------------------
# MAIN
# ------------------------
if __name__ == "__main__":
    print("Starting data collection (Level 2 - S3)...")

    while True:
        data = fetch_data()
        upload_to_s3(data)
        print(f"Saved data: {data}")

        time.sleep(60)
