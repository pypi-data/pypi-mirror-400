def check_consistency(df, config):
    """Check relationships between columns (e.g., end_date > start_date)."""
    report = {"inconsistencies_fixed": 0}
    for rule in config.get("business_rules", []):
        if "columns" in rule:  # Multi-col rule
            col1, col2 = rule["columns"][0], rule["columns"][1]
            if col1 in df and col2 in df:
                mask = df[col2] <= df[col1]  # e.g., end <= start
                df.loc[mask, col2] = df[col1] + pd.Timedelta(days=1)  # Fix by adding a day
                report["inconsistencies_fixed"] += mask.sum()
    return df, report

