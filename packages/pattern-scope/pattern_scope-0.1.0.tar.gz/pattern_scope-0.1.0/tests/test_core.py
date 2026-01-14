from patternscope.core import analyze
import pandas as pd


def test_basic():
    df = pd.DataFrame({"x": [1,2,3,4,5]})
    df.to_csv("tmp.csv", index=False)
    result = analyze("tmp.csv")
    assert "x" in result
