import pandas as pd
import numpy as np
from .metrics import monotonic_score, outlier_score, inflection_points
from .visualize import plot_patterns


def analyze(csv_path, plot=False):
    """
    Analyze numerical columns in a CSV file.
    Returns a dict of monotonicity, outlier count, and inflection points.
    """

    df = pd.read_csv(csv_path)
    summary = {}

    for col in df.columns:
        # Only analyze numeric columns
        if not np.issubdtype(df[col].dtype, np.number):
            continue

        series = df[col].dropna().values

        summary[col] = {
            "monotonicity": monotonic_score(series),
            "outliers": outlier_score(series),
            "inflections": inflection_points(series),
        }

        if plot:
            plot_patterns(series, title=col)

    return summary
