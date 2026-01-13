import yaml  # Or json if preferred

def generate_metadata(df, config):
    """Create schema YAML/JSON with types, descriptions."""
    meta = config.get("metadata", {})
    include_desc = meta.get("include_descriptions", True)
    export_fmt = meta.get("export_format", "yaml")
    
    schema = {}
    for col in df.columns:
        dtypes = str(df[col].dtype)
        desc = f"Column: {col} ({dtypes})"  # Simple; extend with business dicts
        if include_desc:
            schema[col] = {"type": dtypes, "description": desc}
        else:
            schema[col] = dtypes
    
    path = "../schema_l2.yaml" if export_fmt == "yaml" else "../schema_l2.json"
    if export_fmt == "yaml":
        with open(path, "w") as f:
            yaml.dump(schema, f, default_flow_style=False)
    else:
        with open(path, "w") as f:
            json.dump(schema, f, indent=2)
    
    return df, {"metadata_generated": {"path": path, "columns": len(schema)}}