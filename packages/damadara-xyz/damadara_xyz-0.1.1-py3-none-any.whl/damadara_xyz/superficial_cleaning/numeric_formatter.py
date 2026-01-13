# superficial_cleaning/numeric_formatter.py  ← FIXED WITH import pandas!
import pandas as pd  # 👈 THIS UNLOCKS pd.api.types

def format_numerics(df, config):
    """Round numerics per precision."""
    report = {"numerics_rounded": 0}
    prec = config.get("numeric_precision", {})
    for col, digits in prec.items():
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            before = df[col].round(digits).equals(df[col])
            df[col] = df[col].round(digits)
            report["numerics_rounded"] += 1 if not before else 0
    return df, {"numerics_formatted": report}