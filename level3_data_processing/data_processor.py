import boto3
import json
from datetime import datetime, timezone

# ==========================
# CONFIG
# ==========================
BUCKET_NAME = "real-time-risk-data-joel-2025"   # change if needed
ASSET_NAME = "bitcoin"

s3 = boto3.client("s3")


# ==========================
# FETCH RAW DATA FROM S3
# ==========================
def get_raw_data_for_day(year, month, day):
    prefix = (
        f"raw/{ASSET_NAME}/"
        f"year={year}/month={month:02d}/day={day:02d}/"
    )

    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=prefix
    )

    records = []

    if "Contents" not in response:
        return records

    for obj in response["Contents"]:
        try:
            obj_data = s3.get_object(
                Bucket=BUCKET_NAME,
                Key=obj["Key"]
            )

            body = obj_data["Body"].read().decode("utf-8").strip()

            # Skip empty files
            if not body:
                continue

            record = json.loads(body)
            records.append(record)

        except json.JSONDecodeError:
            print(f"⚠️ Skipping invalid JSON file: {obj['Key']}")
        except Exception as e:
            print(f"⚠️ Error reading {obj['Key']}: {e}")

    return records


# ==========================
# PROCESS RECORDS
# ==========================
def process_records(records):
    # Sort by timestamp
    records.sort(key=lambda x: x["timestamp"])

    processed = []
    previous_price = None

    for record in records:
        price = record["price_usd"]

        if previous_price is None:
            price_change = 0
            percent_change = 0
        else:
            price_change = price - previous_price
            percent_change = (price_change / previous_price) * 100

        processed_record = {
            "timestamp": record["timestamp"],
            "price_usd": round(price, 2),
            "price_change": round(price_change, 2),
            "percent_change": round(percent_change, 2)
        }

        processed.append(processed_record)
        previous_price = price

    return processed


# ==========================
# UPLOAD PROCESSED DATA
# ==========================
def upload_processed_data(processed_data, year, month, day):
    s3_key = (
        f"processed/{ASSET_NAME}/"
        f"year={year}/month={month:02d}/day={day:02d}/"
        f"processed_data.json"
    )

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(processed_data, indent=2),
        ContentType="application/json"
    )

    print(f"✅ Processed data uploaded to s3://{BUCKET_NAME}/{s3_key}")


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    today = datetime.now(timezone.utc)

    year = today.year
    month = today.month
    day = today.day

    print("📥 Fetching raw data from S3...")
    raw_records = get_raw_data_for_day(year, month, day)

    if not raw_records:
        print("⚠️ No raw data found for today.")
    else:
        print(f"📊 Processing {len(raw_records)} records...")
        processed_records = process_records(raw_records)
        upload_processed_data(processed_records, year, month, day)
