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
    ├── cleaning/                       
    │   ├── __init__.py
    │   ├── preprocess.py               
    │   ├── remove_abnormal.py         
    │   └── utils.py                   
    ├── extraction/                     
    │   ├── __init__.py
    │   ├── data_extractor.py          
    │   └── edge_report_extractor.py    
    ├── matching/                       
    │   ├── __init__.py
    │   ├── templates_lib
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
    ├── characterisation_reporting_match.py    
    ├── edge_reporting_match.py                
    └── variable_reporting_match.py            
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

> **Note**: If the database has been initialized or the environment configured by other layers, skip the corresponding steps.

1. **Environment Setup**  
   Create and activate virtual environment:
   ```bash
   conda create -n rlm python=3.9 -y
   conda activate rlm
   pip install -r requirements.txt
   ```

2. **Initialize Database**  
   Run SQL script to create tables (skip if already executed by other layers). Database already contains required initial data.
   ```bash
   cd seven_ai_layers_robotics && mysql -u <user> -p <database> < schema.sql
   ```

3. **Configure Settings**  
   Copy `config.example.toml` to `config.toml` and edit with your database connection and API keys.

4. **Run Program**  
   ```bash
   python main.py learning --pipeline variable      # Variable data pipeline
   python main.py learning --pipeline edge         # Edge report pipeline
   python main.py learning --pipeline characterization  # Characterization pipeline
   ```

### Key Modules for Executing Task

- **characterisation_reporting_match.py**: Data-pair matching for characterisation report generation
- **edge_reporting_match.py**: Data-pair matching for edge report generation
- **variable_reporting_match.py**: Data-pair matching for variable report

