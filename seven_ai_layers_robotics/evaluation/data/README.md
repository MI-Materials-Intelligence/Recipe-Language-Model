# Data Overview

This directory contains the data files required by the evaluation layer.

## Data Files

### 1. Predictor Model Files (`predictor_inputs/`)

**Predictor types:**
- `ff/` - Files required by the fill factor (FF) predictor.
- `jsc/` - Files required by the short-circuit current density (Jsc) predictor.
- `pce/` - Files required by the power conversion efficiency (PCE) predictor.
- `voc/` - Files required by the open-circuit voltage (Voc) predictor.

**Each predictor directory contains the following files:**

| File | Format | Description |
|------|--------|-------------|
| `xgb_col_*.pkl` | Pickle | Feature columns used by the XGBoost model. |
| `xgb_scaler_*.pkl` | Pickle | Data scaler. |
| `xgb_model_*.pkl` | Pickle | Trained XGBoost model. |
| `encoding_mappings_*.json` | JSON | Encoding mappings for categorical features. |

### 2. Configuration Files

#### `compound_mapping.json`
- **Format**: JSON
- **Description**: Compound-name mapping table used to normalize compound names from different sources.
- **Example**:
```json
{
  "2-AEP": "2-AEP (2-aminoethylphosphonic acid)",
  "2PACz": "2PACz (2-(9H-carbazol-9-yl)ethylphosphonic acid)"
}
```

#### `five_dimension_rubrics_new_zhao.json`
- **Format**: JSON
- **Description**: Evaluation rubrics for the five dimensions used in mechanistic reasoning.
- **Example**:
```json
{
  "score_range": "9-10",
  "label": "",
  "description": "All chemical names, structures, and ionic compositions are fully correct; no contradictions. Complex species, such as PEA and PACz derivatives, are accurately described; abbreviations and full names match."
}
```

#### `materials_dict_2025_11_11.pickle`
- **Format**: Pickle
- **Description**: Material dictionary used to supplement alternative forms of the same compound.

## Source

1. `predictor_inputs/`: Model training outputs, including trained models and related configuration files.
2. Other files: Provided by the experimental team.

## Notes

### Usage Limits
- The model files are intended only for predictions related to perovskite solar cells.
- The material dictionary mainly covers common perovskite materials. New materials need to be added manually.

### Updates and Maintenance
- Model files are updated when new data is added.
- The material dictionary is expanded periodically.
- If errors or missing entries are found, contact the team for updates.
