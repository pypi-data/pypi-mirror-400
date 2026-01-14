from signal_scope.core import analyze_ts
import pandas as pd


def test_core_runs(tmp_path):
    df = pd.DataFrame({"value": [1,2,3,2,5,4]})
    p = tmp_path / "x.csv"
    df.to_csv(p, index=False)

    result = analyze_ts(p, col="value", plot=False)

    assert "trend" in result
    assert "volatility" in result
    assert "drift" in result
    assert "turning_points" in result
    assert "anomaly_score" in result
