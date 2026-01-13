def remove_duplicates(df, keys):
    """Drop duplicate rows based on given key columns."""
    before = len(df)
    df = df.drop_duplicates(subset=keys)
    removed = before - len(df)
    return df, {"duplicates_removed": removed}
