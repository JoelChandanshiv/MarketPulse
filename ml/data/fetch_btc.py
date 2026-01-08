import requests
from ml.features.build_features import build_features
from ml.features.build_features import build_features, save_features

API_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"

PARAMS = {
    "vs_currency": "usd",
    "days": 30        # last 30 days (5-min resolution)
}

def fetch_prices():
    response = requests.get(API_URL, params=PARAMS)
    data = response.json()

    if "prices" not in data:
        raise RuntimeError(f"API failed: {data}")

    # ✅ Extract ONLY price (index 1), ensure float
    prices = [float(p[1]) for p in data["prices"]]

    print(f"✅ Fetched {len(prices)} BTC prices")
    print("📈 Sample:", prices[:5])

    return prices

if __name__ == "__main__":
    prices = fetch_prices()

    price_series = prices

    print(f"✅ Fetched {len(price_series)} BTC prices")
    print("📈 Sample:", price_series[:5])
    from ml.features.build_features import build_features

    features = build_features(price_series)
    print(features.head())

    prices = fetch_prices()
    df = build_features(prices)
    save_features(df)

    print(df.head())

