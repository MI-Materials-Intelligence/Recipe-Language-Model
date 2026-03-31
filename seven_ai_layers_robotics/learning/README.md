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

## Input Demo

```json
{
  "No": 13873,
  "date": "20241203",
  "rank": 27,
  "Formula PVK": "Cs0.05MA0.16FA0.79PbI2.9Br0.1",
  "Concentration PVK": 1.73,
  "Formula Additive 1": "MACl",
  "Concentration Additive 1": 0.30,
  "Formula Additive 2": null,
  "Concentration Additive 2": null,
  "Formula Additive 3": null,
  "Concentration Additive 3": null,
  "Formula SAM 1": "Me-4PACz",
  "Concentration SAM 1": 0.3300000000,
  "Formula SAM 2": null,
  "Concentration SAM 2": null,
  "Formula SAM 3": null,
  "Concentration SAM 3": null,
  "Spin Coating Speed SAM": null,
  "Spin Coating Time SAM": null,
  "Annealed Temperature SAM": null,
  "Annealed Time SAM": null,
  "Spin Coating Speed PVK 1": 1000,
  "Spin Coating Time PVK 1": 10,
  "Spin Coating Speed PVK 2": 5000,
  "Spin Coating Time PVK 2": 30,
  "Antisolvent Dropping Timing": 6,
  "Antisolvent Volume": 160,
  "Annealed Temperature PVK": 110,
  "Annealed Time PVK": 25,
  "Formula Passivator 1": null,
  "Concentration Passivator 1": null,
  "Formula Passivator 2": null,
  "Concentration Passivator 2": null,
  "Formula Passivator 3": null,
  "Concentration Passivator 3": null,
  "Formula Passivator 4": null,
  "Concentration Passivator 4": null,
  "Spin Coating Speed Passivator": null,
  "Spin Coating Time Passivator": null,
  "Passivator Dropping Timing": null,
  "Passivator Volume": null,
  "Annealed Temperature Passivator": null,
  "Annealed Time Passivator": null,
  "PCE": 15.6140000000,
  "FF": 74.2830000000,
  "Voc": 1.0118000000,
  "Jsc": 20.7740000000,
  "Product": 3469,
  "Channel": "CH1",
  "From": "v1",
  "upload_time": null
}

{
  "No": 14852,
  "date": "20241204",
  "rank": 28,
  "Formula PVK": "Cs0.05MA0.16FA0.79PbI2.9Br0.1",
  "Concentration PVK": 1.73,
  "Formula Additive 1": "PEAI",
  "Concentration Additive 1": 0.50,
  "Formula Additive 2": null,
  "Concentration Additive 2": null,
  "Formula Additive 3": null,
  "Concentration Additive 3": null,
  "Formula SAM 1": "Me-4PACz",
  "Concentration SAM 1": 0.3300000000,
  "Formula SAM 2": null,
  "Concentration SAM 2": null,
  "Formula SAM 3": null,
  "Concentration SAM 3": null,
  "Spin Coating Speed SAM": null,
  "Spin Coating Time SAM": null,
  "Annealed Temperature SAM": null,
  "Annealed Time SAM": null,
  "Spin Coating Speed PVK 1": 1000,
  "Spin Coating Time PVK 1": 10,
  "Spin Coating Speed PVK 2": 5000,
  "Spin Coating Time PVK 2": 30,
  "Antisolvent Dropping Timing": 6,
  "Antisolvent Volume": 160,
  "Annealed Temperature PVK": 110,
  "Annealed Time PVK": 25,
  "Formula Passivator 1": null,
  "Concentration Passivator 1": null,
  "Formula Passivator 2": null,
  "Concentration Passivator 2": null,
  "Formula Passivator 3": null,
  "Concentration Passivator 3": null,
  "Formula Passivator 4": null,
  "Concentration Passivator 4": null,
  "Spin Coating Speed Passivator": null,
  "Spin Coating Time Passivator": null,
  "Passivator Dropping Timing": null,
  "Passivator Volume": null,
  "Annealed Temperature Passivator": null,
  "Annealed Time Passivator": null,
  "PCE": 17.3550000000,
  "FF": 74.3480000000,
  "Voc": 1.0870000000,
  "Jsc": 21.4740000000,
  "Product": 3713,
  "Channel": "CH4",
  "From": "v1",
  "upload_time": null
}

```

## Output Demo

```json
{
  "id": 2024,
  "analysis_type": "Formula Additive 1",
  "reverse_diff_class": "MACl -> PEAI",
  "sample_id_1": "13873",
  "sample_id_2": "14852",
  "control_device_fabrication": "The hole transport layer (HTL) was fabricated by spin coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto a fluorine-doped tin oxide (FTO) substrate, followed by annealing at 100°C for 10 minutes. …… The control device achieved an average power conversion efficiency (PCE) of 15.61% with a short-circuit current density (JSC) of 20.77 mA/cm², an open-circuit voltage (VOC) of 1.01 V, and a fill factor (FF) of 74.28%.",
  "target_device_fabrication": "The hole transport layer (HTL) was fabricated by spin-coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto an FTO substrate, followed by annealing at 100°C for 10 minutes. …… The optimised device achieved an average power conversion efficiency (PCE) of 17.36% with a short-circuit current density (JSC) of 21.47 mA/cm², an open-circuit voltage (VOC) of 1.09 V, and a fill factor (FF) of 74.35%.",
  "json_file_path": "D:\\pycharmpro\\0330\\Recipe-Language-Model\\seven_ai_layers_robotics\\learning\\data\\fp\\tasks\\Formula Additive 2\\m-Br-PEACl -_ m-F-PEACl.json",
  "created_at": "2026-03-30 17:28:07",
  "meta_info": {
    "Expert": "",
    "Sample_ID_1": "13873,control device",
    "Sample_ID_2": "14852,target device",
    "Analysis_Type": "Formula Additive 1",
    "Sample_ID_1_date": "2024-12-03",
    "Sample_ID_2_date": "2024-12-04",
    "Sample_ID_1_Group_ID": 4,
    "Sample_ID_2_Group_ID": 6
  },
  "status": 1,
  "task_name": "Formula Additive 1"
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

