# root_cleaning/__init__.py  ← ADD import yaml HERE
import yaml  # 👈 THIS FIXES THE "yaml not defined" ERROR
import pandas as pd
from .duplicates_handler import remove_duplicates
from .missing_value_handler import handle_missing
from .type_standardizer import coerce_types
from .text_cleaner import clean_text
from .validator import validate

def run_pipeline(df, config_path):
    """Orchestrator for L0 - chains all modules."""
    config = yaml.safe_load(open(config_path))  # Now yaml works!
    
    df, rep1 = remove_duplicates(df, config.get("dedup_keys", []))
    df, rep2 = missing_value_handler.handle_missing(df, config)  # Note: Use full module name if needed
    df, rep3 = coerce_types(df, config.get("type_map", {}))
    df, rep4 = clean_text(df)
    validation_report = validate(df, config.get("required_columns", []))
    
    report = {
        "duplicates": rep1,
        "missing": rep2,
        "types": rep3,
        "text": rep4,
        "validation": validation_report,
    }
    
    return df, report