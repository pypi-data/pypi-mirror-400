import pandas as pd

def format_dates(df, config):
    """Apply uniform date format."""
    report = {"dates_formatted": 0}
    fmt = config.get("date_format", "%Y-%m-%d")
    for col in df.select_dtypes(include=["datetime64"]).columns:
        before = df[col].dtype
        df[col] = df[col].dt.strftime(fmt)
        report["dates_formatted"] += 1 if df[col].dtype != before else 0
    return df, report