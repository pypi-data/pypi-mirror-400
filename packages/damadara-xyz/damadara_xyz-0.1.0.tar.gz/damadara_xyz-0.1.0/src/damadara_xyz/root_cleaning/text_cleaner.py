def clean_text(df):
    """Trim spaces, fix capitalization, remove weird chars."""
    for col in df.select_dtypes(include="object").columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.replace(r"[^\w\s@.,'-]", "", regex=True)
        )
    return df, {"text_cleaned": True}
