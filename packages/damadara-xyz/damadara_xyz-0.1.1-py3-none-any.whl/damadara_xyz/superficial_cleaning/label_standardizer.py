def standardize_labels(df, config):
    """Title/lower/upper case categoricals."""
    report = {"labels_standardized": 0}
    casing = config.get("label_casing", "title")
    for col in df.select_dtypes(include="object").columns:
        if config.get("text_beautify", {}).get(col, False):
            before = df[col].nunique()
            if casing == "title":
                df[col] = df[col].str.title()
            elif casing == "lower":
                df[col] = df[col].str.lower()
            elif casing == "upper":
                df[col] = df[col].str.upper()
            after = df[col].nunique()
            report["labels_standardized"] += abs(after - before)  # Approx changes
    return df, report