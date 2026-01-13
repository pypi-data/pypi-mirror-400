# detailed_cleaning/logic_enforcer.py  ← FIXED WITH import pandas!
import pandas as pd  # 👈 THIS WAS MISSING — NOW pd.api.types WORKS!

def enforce_logic(df, config):
    """Apply simple column-level business rules."""
    report = {"rules_enforced": {}}
    for rule in config.get("business_rules", []):
        if "column" in rule:
            col = rule["column"]
            if col in df.columns:
                before = df[col].sum() if pd.api.types.is_numeric_dtype(df[col]) else len(df)
                if rule["condition"] == "> 0" and pd.api.types.is_numeric_dtype(df[col]):
                    negatives_before = (df[col] < 0).sum()
                    df.loc[df[col] < 0, col] = 0
                    report["rules_enforced"][col] = f"Fixed {negatives_before} negatives"
                # Add more conditions here as needed
    return df, report