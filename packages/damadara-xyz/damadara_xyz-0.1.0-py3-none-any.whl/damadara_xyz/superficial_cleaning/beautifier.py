def beautify_df(df, config):
    """Sort, reset index, etc."""
    report = {"beautified": True}
    # Sort by customer_id for determinism
    if "customer_id" in df.columns:
        df = df.sort_values("customer_id").reset_index(drop=True)
    # Extra: Remove trailing spaces globally
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    return df, report