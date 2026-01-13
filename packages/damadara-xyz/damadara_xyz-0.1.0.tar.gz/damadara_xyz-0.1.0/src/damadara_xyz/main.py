# main.py  ← FIXED: DUAL API + CLI (run_pipeline FOR IMPORTS, main FOR CLI)
import argparse
import pandas as pd
import yaml
import json
import os
import sys
from datetime import datetime
import numpy as np  # For safe serialization if needed

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def run_l0(df, l0_config_path):
    """Inline L0 chain."""
    from .root_cleaning import (
        remove_duplicates, handle_missing, coerce_types, clean_text, validate
    )
    config = yaml.safe_load(open(l0_config_path))
    df, rep1 = remove_duplicates(df, config.get("dedup_keys", []))
    df, rep2 = handle_missing(df, config)
    df, rep3 = coerce_types(df, config.get("type_map", {}))
    df, rep4 = clean_text(df)
    val = validate(df, config.get("required_columns", []))
    report = {"duplicates": rep1, "missing": rep2, "types": rep3, "text": rep4, "validation": val}
    return df, report

def run_l1(df, l1_config_path):
    """Inline L1 chain."""
    from .detailed_cleaning import (
        detect_and_handle_outliers, check_consistency, validate_references, enforce_logic, generate_summary
    )
    config = yaml.safe_load(open(l1_config_path))
    df, rep1 = detect_and_handle_outliers(df, config)
    df, rep2 = check_consistency(df, config)
    df, rep3 = validate_references(df, config)
    df, rep4 = enforce_logic(df, config)
    summary = generate_summary(df, [rep1, rep2, rep3, rep4], "temp_l1_summary.json")
    os.remove("temp_l1_summary.json")  # Clean up
    return df

def run_l2(df, l2_config_path):
    """Inline L2 chain."""
    from .superficial_cleaning import (
        format_columns, standardize_labels, format_dates, format_numerics, generate_metadata, beautify_df
    )
    config = yaml.safe_load(open(l2_config_path))
    df, rep1 = format_columns(df, config)
    df, rep2 = standardize_labels(df, config)
    df, rep3 = format_dates(df, config)
    df, rep4 = format_numerics(df, config)
    df, rep5 = generate_metadata(df, config)
    df, rep6 = beautify_df(df, config)
    return df

def run_pipeline(input_path, layers="all", output_path=None):
    """
    API Entry: Run the pipeline on a CSV file.
    
    Args:
        input_path (str): Path to input CSV.
        layers (str): Layers to run: 'l0', 'l1', 'l2', or 'all'.
        output_path (str, optional): Path to save output CSV.
    
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    # Paths
    l0_config = os.path.join(PROJECT_ROOT, "configs", "cleaning_config.yaml")
    l1_config = os.path.join(PROJECT_ROOT, "configs", "semantic_config.yaml")
    l2_config = os.path.join(PROJECT_ROOT, "configs", "presentation_config.yaml")

    # Load input
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input '{input_path}' not found!")
    df = pd.read_csv(input_path)
    print(f"Loaded input: {df.shape}")

    # Parse layers
    if layers == "all":
        layers_list = ["l0", "l1", "l2"]
    else:
        layers_list = layers.split(",")

    overall_report = {"timestamp": datetime.now().isoformat(), "input_shape": df.shape, "layers_run": layers_list}

    for layer in layers_list:
        if layer == "l0":
            df, l0_rep = run_l0(df, l0_config)
            overall_report["l0"] = l0_rep
            print(f"✅ L0 complete: {df.shape}")
        elif layer == "l1":
            df = run_l1(df, l1_config)
            print(f"✅ L1 complete: {df.shape}")
        elif layer == "l2":
            df = run_l2(df, l2_config)
            print(f"✅ L2 complete: {df.shape}")
        else:
            raise ValueError(f"Unknown layer: {layer}")

    # Save if path given
    if output_path:
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")

    overall_report["output_shape"] = df.shape
    with open("pipeline_report.json", "w") as f:
        json.dump(overall_report, f, indent=2)

    print(f"\n🏆 PIPELINE COMPLETE! Input: {overall_report['input_shape']} → Output: {overall_report['output_shape']}")
    print("Report: pipeline_report.json")
    return df

def main():
    parser = argparse.ArgumentParser(description="DaMadara_xyz Multi-Layer Data Cleaning Pipeline")
    parser.add_argument("--layers", type=str, default="all", help="Layers to run: 'l0', 'l1', 'l2', or 'all'")
    parser.add_argument("--input", type=str, default="dirty_customer_data.csv", help="Input CSV")
    parser.add_argument("--output", type=str, default=None, help="Output CSV")
    args = parser.parse_args()

    run_pipeline(args.input, args.layers, args.output)

if __name__ == "__main__":
    main()