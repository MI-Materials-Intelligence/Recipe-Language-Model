# Learning Layer

## Overview

In the learning layer, the formulas and parameters are encoded and then tokenised into recipes as inputs. Through atomic skills of data extraction, cleaning, and matching, these data are organised into standardised datasets, providing the basis for RLM training and iterative recipe refinement.

Key Atomic Skills:
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
    │   ├── characterisation_image_pvk.py            
    │   ├── insert_characterization_pairs.py 
    │   ├── merge_results.py           
    │   ├── passivator_xrd.py          
    │   ├── perovskite_text_generator.py
    │   ├── characterisation_pl_sam.py                  
    │   └── single_var_matching_pipeline.py 
    ├── __init__.py
    ├── characterisation_reporting_match.py    # Characterization report matching
    ├── edge_reporting_match.py                # Edge report matching
    └── variable_reporting_match.py            # Variable report matching
```

## Input Demo

```json
{
  "No": 13873,
  "Formula PVK": "Cs0.05MA0.16FA0.79PbI2.9Br0.1",
  "Concentration PVK": 1.73,
  "Formula Additive 1": "MACl",
  "Concentration Additive 1": 0.30,
  "Formula Additive 2": null,
  "Concentration Additive 2": null,
  "Formula Additive 3": null,
  "Concentration Additive 3": null,
  "Formula SAM 1": "Me-4PACz",
  "Concentration SAM 1": 0.33,
  "Spin Coating Speed PVK 1": 1000,
  "Spin Coating Time PVK 1": 10,
  "Spin Coating Speed PVK 2": 5000,
  "Spin Coating Time PVK 2": 30,
  "Antisolvent Dropping Timing": 6,
  "Antisolvent Volume": 160,
  "Annealed Temperature PVK": 110,
  "Annealed Time PVK": 25,
  "PCE": 15.6,
  "FF": 74.3,
  "Voc": 1.01,
  "Jsc": 20.8
}

{
  "No": 14852,
  "Formula PVK": "Cs0.05MA0.16FA0.79PbI2.9Br0.1",
  "Concentration PVK": 1.73,
  "Formula Additive 1": "PEAI",
  "Concentration Additive 1": 0.50,
  "Formula SAM 1": "Me-4PACz",
  "Concentration SAM 1": 0.33,
  "Spin Coating Speed PVK 1": 1000,
  "Spin Coating Time PVK 1": 10,
  "Spin Coating Speed PVK 2": 5000,
  "Spin Coating Time PVK 2": 30,
  "Antisolvent Dropping Timing": 6,
  "Antisolvent Volume": 160,
  "Annealed Temperature PVK": 110,
  "Annealed Time PVK": 25,
  "PCE": 17.4,
  "FF": 74.3,
  "Voc": 1.09,
  "Jsc": 21.5
}

```

## Output Demo

```json
{
  "analysis_type": "Formula Additive 1",
  "reverse_diff_class": "MACl -> PEAI",
  "sample_id_1": "13873",
  "sample_id_2": "14852",
  "control_device_fabrication": "The hole transport layer (HTL) was fabricated by spin coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto a fluorine-doped tin oxide (FTO) substrate, followed by annealing at 100°C for 10 minutes. …… The control device achieved an average power conversion efficiency (PCE) of 15.6% with a short-circuit current density (JSC) of 20.8 mA/cm², an open-circuit voltage (VOC) of 1.01 V, and a fill factor (FF) of 74.3%.",
  "optimised_device_fabrication": "The hole transport layer (HTL) was fabricated by spin-coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto an FTO substrate, followed by annealing at 100°C for 10 minutes. …… The optimised device achieved an average power conversion efficiency (PCE) of 17.4% with a short-circuit current density (JSC) of 21.5 mA/cm², an open-circuit voltage (VOC) of 1.09 V, and a fill factor (FF) of 74.3%."
  }
```


## Basic Usage

1. **Initialize Database**  
   Run the SQL script to create tables:
   ```bash
   mysql -u <user> -p <database> < schema.sql
   ```

2. **Configure Settings**  
   Edit `config.toml` with your database and path details.

3. **Run Program**  
   ```bash
   conda activate rlm
   python main.py
   ```


### Key Modules for Executing Task

- **characterisation_reporting_match.py**: Data-pair matching for characterisation report generation
- **edge_reporting_match.py**: Data-pair matching for edge report generation
- **variable_reporting_match.py**: Data-pair matching for variable report

