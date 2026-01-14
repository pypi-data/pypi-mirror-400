from signal_scope.metrics import (
    trend_strength, volatility, drift, turning_points, anomaly_score
)


def test_metrics():
    x = [1,2,3,2,4,3]

    assert isinstance(trend_strength(x), float)
    assert isinstance(volatility(x), float)
    assert isinstance(drift(x), float)
    assert isinstance(turning_points(x), int)
    assert isinstance(anomaly_score(x), float)
