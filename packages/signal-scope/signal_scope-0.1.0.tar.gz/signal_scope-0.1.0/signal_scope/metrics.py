import numpy as np
from scipy.signal import find_peaks


def trend_strength(x):
    """Returns normalized linear correlation with index."""
    idx = np.arange(len(x))
    corr = np.corrcoef(idx, x)[0, 1]
    return float(corr)


def volatility(x):
    """Standard deviation normalized by mean magnitude."""
    return float(np.std(x) / (np.abs(np.mean(x)) + 1e-8))


def drift(x):
    """Difference between last and first value."""
    return float(x[-1] - x[0])


def turning_points(x):
    """Count local maxima + minima."""
    x = np.asarray(x)
    peaks, _ = find_peaks(x)
    troughs, _ = find_peaks(-x)
    return int(len(peaks) + len(troughs))


def anomaly_score(x):
    """Z-score based anomaly measure."""
    z = np.abs((x - np.mean(x)) / (np.std(x) + 1e-8))
    return float(np.mean(z))
