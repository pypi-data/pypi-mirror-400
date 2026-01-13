def handle_missing(df, config):
    na_thresh = config.get("na_threshold", 0.6)
    fill_values = config.get("fill_values", {})
    
    # Drop columns with too many NaNs
    df = df.dropna(axis=1, thresh=int((1 - na_thresh) * len(df)))
    
    # Fill numeric & categorical
    df = df.fillna({
        col: fill_values.get("numeric", 0) if df[col].dtype != 'O'
        else fill_values.get("categorical", "Unknown")
        for col in df.columns
    })
    return df, {"missing_handled": True}
