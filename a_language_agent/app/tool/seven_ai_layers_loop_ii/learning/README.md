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

## Input Requirements

Provides raw experimental data via SQL dump files. The system imports these files into the MySQL database to initialize the experimental records table.

### Configuration Details

| # | Database | Target Table | File Format | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `seven_ai_layers_robotics` | `experimental_records` | `.sql` | Raw experimental records (3000+ entries) |
| 2 | `seven_ai_layers_robotics` | `sam` | `.sql` | Extended experimental records (5000+ entries) |
| 3 | `seven_ai_layers_robotics` | `add` | `.sql` | Robotics-integrated experimental data |
| 4 | `seven_ai_layers_robotics` | `process` | `.sql` | Control-target matching pairs for analysis |
| 5 | `seven_ai_layers_robotics` | `passive` | `.sql` | Control-target matching pairs for analysis |

### experimental_records Table Structure (JSON Format)
```json
{
  "No": 2965,
  "date": "20240925",
  "rank": 8,
  "Formula PVK": "Cs0.04MA0.16FA0.8PbI2.8Br0.2",
  "Concentration PVK": 1.35,
  "Formula Additive 1": null,
  "Concentration Additive 1": null,
  "Formula Additive 2": null,
  "Concentration Additive 2": null,
  "Formula Additive 3": null,
  "Concentration Additive 3": null,
  "Formula SAM 1": null,
  "Concentration SAM 1": null,
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
  "Spin Coating Time PVK 2": 25,
  "Antisolvent Dropping Timing": 15,
  "Antisolvent Volume": 120,
  "Annealed Temperature PVK": 105,
  "Annealed Time PVK": 30,
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
  "PCE": 2.4463000000,
  "FF": 54.8060000000,
  "Voc": 0.3541800000,
  "Jsc": 12.6030000000,
  "Product": "742",
  "Channel": "CH1",
  "From": "v0",
  "upload_time": null
}
```

## Output Data
| # | Database | Target Table | File Format | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `seven_ai_layers_robotics` | `match_pair` | `.sql` | Raw experimental records (3000+ entries) |
| 2 | `seven_ai_layers_robotics` | `experiments_characterization_pairs` | `.sql` | Extended experimental records (5000+ entries) |
| 3 | `seven_ai_layers_robotics` | `single_report` | `.sql` | Robotics-integrated experimental data |

### match_pair Table Structure (JSON Format)
```json
{
  "id": 10882,
  "analysis_type": "Formula SAM 1",
  "reverse_diff_class": "4PADCB -> 4PACz",
  "sample_id_1": "10348",
  "sample_id_2": "12422",
  "control_device_fabrication": "The resulting hybrid SAMs-modified PSC achieve a champion PCE of 16.25%, with VOC of 1.0227 V, FF of 78.104%, and JSC of 20.345 mA/cm². The perovskite precursor solutions were prepared by dissolving 1.5 mol/L Cs0.1FA0.9I2.8Br0.2. Controlled addition of 4PACz (0.33 mg/mL) as a SAM was performed to stabilize the perovskite layer and engineer a more robust interface.  Perovskite solution was deposited in two steps, first at 1000 rpm for 10 s and then at 5000 rpm for 40 s. Antisolvent (240 µL) was dripped onto the center of film at 12 s before the end of spin-coating. Subsequent thermal treatment was carried out at 110 °C for 30 min to finalize the perovskite crystal structure.",
  "target_device_fabrication": "Within a framework of controlled experimental inputs, a perovskite cell configuration was put together, ultimately manifesting a PCE of 16.903%, FF of 81.157%, Voc of 1.0763 V, and Jsc of 19.351 mA/cm². For the Cs0.1FA0.9I2.8Br0.2, 1.5 mol/L perovskite precursor solution was prepared. The addition of 4PADCB (0.33 mg/mL) as a SAM was performed to optimize surface passivation and ensure improved interface quality.  The perovskite precursor solutions were spin-coated on the substrates at 1000 rpm for 10 s and 5000 rpm for 40 s. At the last 12 s of spinning, 240 µL of antisolvent was dripped onto the substrate centre. After spin-coating, the films were annealed on the hot plate at 110 °C for 30 min.",
  "created_at": "2026-01-16 11:32:43",
  "meta_info": {
    "Expert": "",
    "Sample_ID_1": "10348,control device",
    "Sample_ID_2": "12422,target device",
    "Analysis_Type": "Formula SAM 1",
    "Sample_ID_1_date": "2024-11-25",
    "Sample_ID_2_date": "2024-11-28",
    "Sample_ID_1_Group_ID": 143,
    "Sample_ID_2_Group_ID": 151
  },
  "status": 0,
  "version": 0,
  "task_name": "Formula SAM 1"
}
```


## Basic Usage

### Environment Setup
Activate the conda environment and navigate to the agent framework directory.

```bash
conda activate MIAgent
cd agent_framework
```

### Run Agent
Start the main agent process.

```bash
python main.py
```

###  Interactive Command
Once the agent is running, input the learning command to trigger the data pipeline.

```text
> do learning
```

### Key Modules for Executing Task

- **characterisation_reporting_match.py**: Data-pair matching for characterisation report generation
- **edge_reporting_match.py**: Data-pair matching for edge report generation
- **variable_reporting_match.py**: Data-pair matching for variable report

