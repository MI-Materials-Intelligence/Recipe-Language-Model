# Learning Layer

## Overview

The Learning layer performs extraction, cleaning, and matching on robotic experimental data to establish a reliable data foundation for subsequent recipe learning and model.  
Key Atomic Skill:
- **Cleaning**: Preprocessing and outlier cleaning
- **Matching**: Matching data pairs based on variables
- **Extraction**: Data extraction from robotic boxes

## Layer Structure with Atomic Skills

```
Learning/
├── data/
│   
└── src/
    ├── cleaning/                       # Data cleaning module
    │   ├── __init__.py
    │   ├── preprocess.py               
    │   ├── remove_abnormal.py         
    │   └── utils.py                   
    ├── extraction/                     # Data extraction module
    │   ├── __init__.py
    │   ├── data_extractor.py          
    │   └── edge_report_extractor.py    
    ├── matching/                       # Data matching module
    │   ├── __init__.py
    │   ├── additive_xrd.py             
    │   ├── generating_single_var.py    
    │   ├── get_single_var_diff_class.py 
    │   ├── image_process.py            
    │   ├── insert_characterization_pairs.py 
    │   ├── merge_results.py           
    │   ├── passivator_xrd.py          
    │   ├── perovskite_text_generator.py
    │   ├── pl_sam.py                  
    │   └── single_var_matching_pipeline.py 
    ├── __init__.py
    ├── characterisation_reporting_match.py    # Characterization report matching
    ├── edge_reporting_match.py                # Edge report matching
    └── variable_reporting_match.py            # Variable report matching
```

## Database Requirements

Requires access to experimental record database containing experimental parameters, characterization data, and other fields.

## Output Data

Outputs structured experimental data, matching results, and feature extraction results.

## Basic Usage

### Environment Setup

```bash
conda activate rlm_agent
cd seven_layers/Learning
```

### Usage Example

```python
from src.cleaning import preprocess, remove_abnormal
from src.matching import run, run_cleaning, run_matching
from src.extraction.data_extractor import DataExtractor

# Data cleaning
preprocessed_data = preprocess(raw_data_path)
clean_data = remove_abnormal(preprocessed_data)

# Run matching process
results = run(data_source="database")

# Feature extraction
extractor = DataExtractor()
extracted_features = extractor.extract(report_text)
```

### Key Modules for Executing Task

- **characterisation_reporting_match.py**: Data-pair matching for characterisation report generation
- **edge_reporting_match.py**: Data-pair matching for edge report generation
- **variable_reporting_match.py**: Data-pair matching for variable report

