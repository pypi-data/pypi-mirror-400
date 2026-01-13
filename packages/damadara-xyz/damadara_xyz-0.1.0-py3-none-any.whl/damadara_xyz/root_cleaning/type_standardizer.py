import pandas as pd

def coerce_types(df, type_map):
    """Attempt to convert columns to specified types."""
    report = {}
    for col, dtype in type_map.items():
        try:
            if dtype == "datetime":
                df[col] = pd.to_datetime(df[col], errors="coerce")
            elif dtype == "numeric":
                df[col] = pd.to_numeric(df[col], errors="coerce")
            else:
                df[col] = df[col].astype(dtype)
            report[col] = "converted"
        except Exception as e:
            report[col] = f"failed: {e}"
    return df, report
