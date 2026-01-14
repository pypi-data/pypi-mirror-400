from patternscope.metrics import monotonic_score, outlier_score, inflection_points


def test_monotonic():
    assert monotonic_score([1,2,3,4]) == 1.0
