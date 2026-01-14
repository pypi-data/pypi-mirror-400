# datasanity

A tiny (<200 lines) CSV health-check + anomaly-detection tool.

It reports:

- Missing value percentages  
- Duplicate row count  
- Cardinality per column  
- Basic anomaly score (z-score > 3)  
- Row + column summary  

## Install

```bash
pip install datasanity
```

## Usage

```python
from datasanity import analyze_csv, pretty_report

r = analyze_csv("data.csv")
print(pretty_report(r))
```

## CLI Demo

```bash
python run_demo.py
```

## Local Development

To install the package locally for development:

```bash
cd datasanity
pip install -e .
```

## Building for Distribution

To create a distributable package:

```bash
pip install build
python -m build
```

This creates `.whl` and `.tar.gz` files in the `dist/` directory that you can share or upload to PyPI.
