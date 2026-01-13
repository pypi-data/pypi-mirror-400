# detailed_cleaning/semantic_summary.py  ← ULTIMATE FIXED: FULL JSON HANDLER!
import json
import numpy as np
from datetime import datetime
import os

def generate_summary(df, l1_reports, output_path="../semantic_report_l1.json"):
    """Compile L1 reports into a JSON summary (numpy-safe, saves file)."""
    # Flatten metrics (convert np.int64 to int)
    key_metrics = {}
    for report in l1_reports:
        for k, v in report.items():
            if isinstance(v, dict):
                # Recurse for nested dicts (convert np ints)
                nested = {}
                for kk, vv in v.items():
                    if isinstance(vv, np.integer):
                        nested[kk] = int(vv)
                    elif isinstance(vv, dict):
                        nested[kk] = {kkk: int(vvv) if isinstance(vvv, np.integer) else vvv for kkk, vvv in vv.items()}
                    else:
                        nested[kk] = vv
                key_metrics[k] = nested
            elif isinstance(v, np.integer):
                key_metrics[k] = int(v)
            elif isinstance(v, (int, float, str, bool, type(None))):
                key_metrics[k] = v

    summary = {
        "layer": "L1_Semantic",
        "timestamp": datetime.now().isoformat(),
        "shape_after": [int(df.shape[0]), int(df.shape[1])],  # Ensure ints
        "key_metrics": key_metrics
    }
    
    # Custom encoder for any lingering numpy
    def json_serial(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Type {type(obj)} not serializable")

    # Make path absolute for safety
    abs_path = os.path.abspath(output_path)
    with open(abs_path, "w") as f:
        json.dump(summary, f, indent=2, default=json_serial)
    
    print(f"   → Summary saved: {abs_path}")
    return summary