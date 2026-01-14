# pattern-scope

A tiny (<200 lines) CSV pattern-analysis tool.

It computes:
- Monotonicity score
- Outlier count
- Inflection-point estimates
- Optional matplotlib plots

## Install

pip install pattern-scope

## Usage

from patternscope.core import analyze
summary = analyze("data.csv", plot=True)
print(summary)