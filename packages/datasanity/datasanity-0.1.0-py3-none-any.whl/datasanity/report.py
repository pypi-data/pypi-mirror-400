def pretty_report(report):
    lines = []
    lines.append("=== DataSanity Report ===")
    lines.append(f"Rows: {report['rows']}")
    lines.append("Columns: " + ", ".join(report["columns"]))
    lines.append("")

    lines.append("Missing %:")
    for col, pct in report["missing_pct"].items():
        lines.append(f"  {col}: {pct}%")

    lines.append("\nDuplicate rows: " + str(report["duplicate_rows"]))

    lines.append("\nCardinality:")
    for col, card in report["cardinality"].items():
        lines.append(f"  {col}: {card}")

    lines.append("\nAnomalies (>3σ):")
    for col, count in report["anomalies"].items():
        lines.append(f"  {col}: {count}")

    return "\n".join(lines)
