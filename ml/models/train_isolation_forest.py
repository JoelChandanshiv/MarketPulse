import os
import json
import joblib
import pandas as pd
from datetime import datetime
from sklearn.ensemble import IsolationForest

# =====================
# PATH CONFIG
# =====================
FEATURE_PATH = "ml/data/btc_features.parquet"
REGISTRY_PATH = "ml/models/registry"

# =====================
# FEATURE LIST
# =====================
FEATURES = [
    "log_return",
    "volatility_10",
    "volatility_30",
    "z_score",
    "momentum_10"
]

# =====================
# VERSIONING UTILS
# =====================
def get_next_version():
    if not os.path.exists(REGISTRY_PATH):
        return "v1"

    versions = []
    for d in os.listdir(REGISTRY_PATH):
        if d.startswith("v") and d[1:].isdigit():
            versions.append(int(d[1:]))

    return f"v{max(versions) + 1}" if versions else "v1"


def update_latest_symlink(version):
    latest_path = os.path.join(REGISTRY_PATH, "latest")
    target_path = os.path.join(REGISTRY_PATH, version)

    if os.path.islink(latest_path) or os.path.exists(latest_path):
        os.remove(latest_path)

    os.symlink(version, latest_path)


# =====================
# TRAINING FUNCTION
# =====================
def train():
    print("📥 Loading features...")
    df = pd.read_parquet(FEATURE_PATH)

    X = df[FEATURES].dropna()

    print("🧠 Training Isolation Forest...")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.02,
        random_state=42
    )

    model.fit(X)

    # ---------------------
    # VERSIONING
    # ---------------------
    version = get_next_version()
    model_dir = os.path.join(REGISTRY_PATH, version)
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, "model.joblib")
    metadata_path = os.path.join(model_dir, "metadata.json")

    # Save model
    joblib.dump(model, model_path)

    # Save metadata
    metadata = {
        "version": version,
        "trained_at": datetime.utcnow().isoformat(),
        "algorithm": "IsolationForest",
        "features": FEATURES,
        "rows_used": len(X),
        "parameters": model.get_params()
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    # Update latest pointer
    update_latest_symlink(version)

    print("✅ Training completed")
    print(f"📦 Model saved at: {model_path}")
    print(f"🧾 Metadata saved at: {metadata_path}")
    print(f"🚀 Active model version: {version}")


# =====================
# ENTRY POINT
# =====================
if __name__ == "__main__":
    train()
