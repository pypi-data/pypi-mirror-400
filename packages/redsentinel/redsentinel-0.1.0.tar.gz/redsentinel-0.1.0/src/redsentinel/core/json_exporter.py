import json
import os

def export_json_report(target: str, normalized_findings: list, output_dir="reports"):
    os.makedirs(output_dir, exist_ok=True)

    path = os.path.join(output_dir, f"{target}_report.json")

    payload = {
        "target": target,
        "findings": normalized_findings,
        "format": "SOC-compatible",
        "version": "1.0"
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return path
