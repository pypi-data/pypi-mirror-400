# detailed_cleaning/reference_validator.py  ← FIXED WITH import pandas!
import pandas as pd  # 👈 THIS WAS MISSING — NOW pd.to_numeric WORKS!

def validate_references(df, config):
    """Map invalid values to 'Unknown' or nearest valid."""
    report = {}
    for col, valid_list in config.get("valid_references", {}).items():
        if col in df.columns:
            mask = ~df[col].isin(valid_list)
            invalid_count = mask.sum()
            df.loc[mask, col] = "Unknown"  # Or use fuzzy matching later
            report[f"{col}_invalid_replaced"] = invalid_count
    
    # Range checks (safe for strings/NaNs)
    for col, ranges in config.get("domain_ranges", {}).items():
        if col in df.columns:
            # Coerce to numeric safely (strings/NaNs become NaN, then fill with median for checks)
            numeric_col = pd.to_numeric(df[col], errors='coerce')
            median_val = numeric_col.median()  # Use median for robust central tendency
            mask_low = numeric_col < ranges["min"]
            mask_high = numeric_col > ranges["max"]
            low_count = mask_low.sum()
            high_count = mask_high.sum()
            
            # Apply fixes only to original df (back to numeric)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(median_val)  # Fill NaNs first
            df.loc[mask_low, col] = ranges["min"]
            df.loc[mask_high, col] = ranges["max"]
            
            report[f"{col}_range_clipped"] = low_count + high_count
            if low_count > 0 or high_count > 0:
                report[f"{col}_clip_details"] = {"low": low_count, "high": high_count}
    
    return df, {"reference_validations": report}