# signal-scope

A tiny (<200 lines) Python tool for analyzing time-series data:

- Trend strength
- Volatility
- Drift detection
- Regime shifts
- Anomaly scoring
- Optional matplotlib visualizations

Perfect for finance, forecasting, sensor data, and fast exploratory analysis.

---

## Install

```bash
pip install signal-scope
```

---

## Usage

```python
from signal_scope.core import analyze_ts

result = analyze_ts("my_data.csv", col="price", plot=True)
print(result)
```

Expected output:

```json
{
  "trend": 0.87,
  "volatility": 0.032,
  "drift": -0.12,
  "turning_points": 5,
  "anomaly_score": 0.014
}
```

---

## Input format

CSV must contain a numeric column, e.g.:

```csv
timestamp,price
2024-01-01,120.3
2024-01-02,121.0
...
```

---

## Programmatic usage

```python
import pandas as pd
from signal_scope.metrics import volatility

df = pd.read_csv("my_data.csv")
print(volatility(df["price"]))
```

---

## Plotting

Enable visual output:

```python
analyze_ts("my_data.csv", col="price", plot=True)
```

---

MIT License.