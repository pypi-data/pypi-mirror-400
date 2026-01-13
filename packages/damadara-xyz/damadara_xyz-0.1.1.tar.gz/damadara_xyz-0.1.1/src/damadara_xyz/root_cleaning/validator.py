def validate(df, required_columns):
    """Basic schema & null validation."""
    missing_cols = [c for c in required_columns if c not in df.columns]
    null_counts = df.isnull().sum().to_dict()
    status = "PASS" if not missing_cols else "FAIL"
    return {"status": status, "missing_columns": missing_cols, "null_counts": null_counts}
