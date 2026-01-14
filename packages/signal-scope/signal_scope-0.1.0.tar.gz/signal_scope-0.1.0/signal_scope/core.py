import pandas as pd
from .metrics import (
    trend_strength,
    volatility,
    drift,
    turning_points,
    anomaly_score
)
from .visualize import plot_series


def analyze_ts(path, col="value", plot=False):
    """Load CSV, compute signal metrics, optionally plot."""
    df = pd.read_csv(path)

    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in CSV.")

    x = df[col].astype(float).values

    result = {
        "trend": trend_strength(x),
        "volatility": volatility(x),
        "drift": drift(x),
        "turning_points": turning_points(x),
        "anomaly_score": anomaly_score(x),
    }

    if plot:
        plot_series(df[col])

    return result
