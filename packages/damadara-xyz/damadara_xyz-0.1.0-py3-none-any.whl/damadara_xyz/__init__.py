# DaMadara_xyz/__init__.py  ← PUBLIC API: EXPOSES MAIN FUNCTIONS
from .main import run_pipeline  # Your CLI orchestrator, renamed for lib use

__version__ = "0.1.0"
__all__ = ["run_pipeline"]

# Optional: Quick usage example in docstring
"""
DaMadara_xyz: 3-Layer Data Cleaning Library

Quick start:
>>> from damadara_xyz import run_pipeline
>>> df_clean = run_pipeline('dirty.csv', layers='all')
>>> df_clean.to_csv('clean.csv', index=False)
"""