import pandas as pd
import numpy as np

def analyze_csv(path):
    df = pd.read_csv(path)

    report = {}

    # 1. Shape
    report["rows"] = len(df)
    report["columns"] = df.columns.tolist()

    # 2. Missing values
    report["missing_pct"] = (df.isna().mean() * 100).round(2).to_dict()

    # 3. Duplicate rows
    report["duplicate_rows"] = int(df.duplicated().sum())

    # 4. Cardinality per column
    report["cardinality"] = {col: df[col].nunique() for col in df.columns}

    # 5. Basic anomaly score (per column z-score > 3)
    anomaly_counts = {}
    numeric_df = df.select_dtypes(include=[np.number])
    for col in numeric_df.columns:
        z = (numeric_df[col] - numeric_df[col].mean()) / (numeric_df[col].std() + 1e-9)
        anomaly_counts[col] = int((np.abs(z) > 3).sum())

    report["anomalies"] = anomaly_counts

    return report
