def format_columns(df, config):
    """Rename/reorder columns per style."""
    report = {"columns_renamed": 0}
    style = config.get("column_style", "snake_case")
    new_cols = []
    for col in df.columns:
        if style == "snake_case":
            new_col = col.lower().replace(" ", "_").replace("-", "_")
        elif style == "camelCase":
            new_col = col.lower().replace(" ", "").replace("_", "").title()
        else:
            new_col = col  # No change
        if new_col != col:
            report["columns_renamed"] += 1
        new_cols.append(new_col)
    df.columns = new_cols
    return df, report