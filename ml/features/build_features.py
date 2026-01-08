import pandas as pd
import numpy as np

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input: DataFrame with column ['price']
    Output: DataFrame with ML features
    """

    df = df.copy()

    # Log return
    df["log_return"] = np.log(df["price"] / df["price"].shift(1))

    # Rolling volatility
    df["volatility_10"] = df["log_return"].rolling(10).std()
    df["volatility_30"] = df["log_return"].rolling(30).std()

    # Z-score
    rolling_mean = df["price"].rolling(30).mean()
    rolling_std = df["price"].rolling(30).std()
    df["z_score"] = (df["price"] - rolling_mean) / rolling_std

    # Momentum
    df["momentum_10"] = df["price"] - df["price"].shift(10)

    # Drop incomplete rows
    df.dropna(inplace=True)

    return df
