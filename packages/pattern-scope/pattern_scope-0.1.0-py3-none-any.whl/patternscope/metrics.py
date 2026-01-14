import numpy as np
from scipy.signal import find_peaks


def monotonic_score(x):
    """Returns score in [0,1] measuring monotonic consistency."""
    diffs = np.diff(x)
    sign = np.sign(np.sum(diffs))
    return float(np.mean(np.sign(diffs) == sign))


def outlier_score(x):
    """Counts |z| > 3 outliers."""
    z = (x - np.mean(x)) / (np.std(x) + 1e-8)
    return int(np.sum(np.abs(z) > 3))


def inflection_points(x):
    """Counts curvature shifts via 2nd derivative peaks."""
    second = np.diff(x, n=2)
    peaks, _ = find_peaks(np.abs(second), height=np.std(second))
    return int(len(peaks))
