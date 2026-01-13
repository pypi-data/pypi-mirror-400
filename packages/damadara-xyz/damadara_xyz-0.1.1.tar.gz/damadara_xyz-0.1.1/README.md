# DaMadara_xyz

A 3-layer data cleaning library: L0 (basic hygiene), L1 (semantic logic), L2 (presentation polish).

## Quick Start

1. Install: `pip install -e .`

2. Run full pipeline: `damadara --layers all --input dirty.csv --output clean.csv`

3. Or via API:
   ```python
   from damadara_xyz import run_pipeline
   df_clean = run_pipeline('dirty.csv', layers='all')
   df_clean.to_csv('clean.csv') 

# DaMadara_xyz

A powerful 3-layer data cleaning library.

## Installation
```bash
pip install damadara_xyz
from damadara_xyz import run_pipeline

df_clean = run_pipeline("dirty.csv", layers="all", output_path="clean.csv")