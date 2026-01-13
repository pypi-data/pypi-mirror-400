import pandas as pd
import numpy as np

def detect_and_handle_outliers(df, config):
    """Detect outliers using IQR or Z-score, cap or remove based on config."""
    report = {}
    for col, method in config.get("outlier_methods", {}).items():
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            if method == "IQR":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers_before = ((df[col] < lower) | (df[col] > upper)).sum()
                df[col] = df[col].clip(lower=lower, upper=upper)  # Cap instead of drop
                report[f"{col}_outliers_capped"] = outliers_before
            elif method == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                threshold = config.get("threshold", 3.0)
                outliers_before = (z_scores > threshold).sum()
                df[col] = np.where(z_scores > threshold, df[col].median(), df[col])  # Replace with median
                report[f"{col}_outliers_replaced"] = outliers_before
    return df, {"outliers_handled": report}