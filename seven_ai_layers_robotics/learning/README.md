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

## Input Demo

```json
{
  "No": 50009,
  "date": "20250727",
  "rank": 168,
  "Formula PVK": "Cs0.05MA0.1FA0.85PbI3.0",
  "Concentration PVK": 1.65,
  "Formula Additive 1": "MACl",
  "Concentration Additive 1": 15.0,
  "Formula Additive 2": "m-F-PEACl",
  "Concentration Additive 2": 2.0,
  "Formula Additive 3": null,
  "Concentration Additive 3": null,
  "Formula SAM 1": "4,4,4-NA",
  "Concentration SAM 1": 0.5,
  "Formula SAM 2": null,
  "Concentration SAM 2": null,
  "Formula SAM 3": null,
  "Concentration SAM 3": null,
  "Spin Coating Speed SAM": 3000,
  "Spin Coating Time SAM": 30,
  "Annealed Temperature SAM": 100,
  "Annealed Time SAM": 10,
  "Spin Coating Speed PVK 1": 1000,
  "Spin Coating Time PVK 1": 5,
  "Spin Coating Speed PVK 2": 5500,
  "Spin Coating Time PVK 2": 30,
  "Antisolvent Dropping Timing": 15,
  "Antisolvent Volume": 150,
  "Annealed Temperature PVK": 110,
  "Annealed Time PVK": 15,
  "Formula Passivator 1": "PDADI",
  "Concentration Passivator 1": 0.5,
  "Formula Passivator 2": null,
  "Concentration Passivator 2": null,
  "Formula Passivator 3": null,
  "Concentration Passivator 3": null,
  "Formula Passivator 4": null,
  "Concentration Passivator 4": null,
  "Spin Coating Speed Passivator": 5000,
  "Spin Coating Time Passivator": 30,
  "Passivator Dropping Timing": 6,
  "Passivator Volume": 70,
  "Annealed Temperature Passivator": 100,
  "Annealed Time Passivator": 5,
  "PCE": 26.2531,
  "FF": 82.9223,
  "Voc": 1.19423,
  "Jsc": 26.5107,
  "Product": 1898,
  "Channel": "CH1",
  "From": "20250626.csv",
  "upload_time": null
}

{
  "No": 50425,
  "date": "20250731",
  "rank": 172,
  "Formula PVK": "Cs0.05MA0.1FA0.85PbI3.0",
  "Concentration PVK": 1.65,
  "Formula Additive 1": "MACl",
  "Concentration Additive 1": 15.0,
  "Formula Additive 2": "m-Br-PEACl",
  "Concentration Additive 2": 2.0,
  "Formula Additive 3": null,
  "Concentration Additive 3": null,
  "Formula SAM 1": "4,4,4-NA",
  "Concentration SAM 1": 0.5,
  "Formula SAM 2": null,
  "Concentration SAM 2": null,
  "Formula SAM 3": null,
  "Concentration SAM 3": null,
  "Spin Coating Speed SAM": 3000,
  "Spin Coating Time SAM": 30,
  "Annealed Temperature SAM": 100,
  "Annealed Time SAM": 10,
  "Spin Coating Speed PVK 1": 1000,
  "Spin Coating Time PVK 1": 5,
  "Spin Coating Speed PVK 2": 5500,
  "Spin Coating Time PVK 2": 30,
  "Antisolvent Dropping Timing": 15,
  "Antisolvent Volume": 150,
  "Annealed Temperature PVK": 110,
  "Annealed Time PVK": 15,
  "Formula Passivator 1": "PDADI",
  "Concentration Passivator 1": 0.5,
  "Formula Passivator 2": null,
  "Concentration Passivator 2": null,
  "Formula Passivator 3": null,
  "Concentration Passivator 3": null,
  "Formula Passivator 4": null,
  "Concentration Passivator 4": null,
  "Spin Coating Speed Passivator": 5000,
  "Spin Coating Time Passivator": 30,
  "Passivator Dropping Timing": 6,
  "Passivator Volume": 70,
  "Annealed Temperature Passivator": 100,
  "Annealed Time Passivator": 5,
  "PCE": 25.147,
  "FF": 81.2593,
  "Voc": 1.17917,
  "Jsc": 26.2444,
  "Product": 2002,
  "Channel": "CH1",
  "From": "20250702.csv",
  "upload_time": null
}


```

## Output Demo

```json
{
  "id": 2024,
  "analysis_type": "Formula Additive 2",
  "reverse_diff_class": "m-F-PEACl -> m-Br-PEACl",
  "sample_id_1": "50425",
  "sample_id_2": "50009",
  "control_device_fabrication": "The cells showed an increase in VOC to 1.17917 V, accompanied by a slight increase in FF to 81.2593% and JSC to 26.2444 mA/cm², resulting in a peak PCE of 25.147%. The 1.65 mol/L perovskite precursor solution with a chemical formula of Cs0.05MA0.1FA0.85I3 was prepared. The sample of 4,4,4-NA was fabricated by spin coating the 4,4,4-NA solution with a concentration of 0.5 mg/mL. MACl (15.0 mg/mL) and m-Br-PEACl (2.0 mg/mL) were incorporated as additives. For perovskite films fabrication, the perovskite precursor was spin-coated on the as prepared substrates at 1000 rpm for 5 s and at 5500 rpm for 30 s. 150 µL CB was dripped onto the center of film at 15 s before the end of spin-coating. The samples were subsequently annealed on a hotplate at 110 °C for 15 min. The PDADI (0.5 mg/mL) was coated onto the perovskite surface. For the passivation treatment, the passivation solution was spin-coated on the perovskite surface at 5000 rpm for 30 s. The passivator volume of 70 µL was dropped at 6 s during spin-coating. The passivation layer underwent annealing at 100 °C for 5 min to optimize its properties. In details, SAM solution was spin-coated on the substrate at 3000 rpm for 30 s, and annealed at 100 °C for 10 min.",
  "target_device_fabrication": "The champion device achieves an outstanding PCE of 26.2531%, with a VOC of 1.19423 V, JSC of 26.5107 mA/cm², and FF of 82.9223%, marking a significant improvement over the control device. The perovskite precursor solution (1.65 mol/L) was prepared in a solvent mixture of DMF and DMSO according to the formula of Cs0.05MA0.1FA0.85I3. The optimal SAM was prepared by using 4,4,4-NA (0.5 mg/mL).The sample of 4,4,4-NA was fabricated with a concentration of 0.5 mg/mL. For the additives treated cells, the MACl (15.0 mg/mL) or m-F-PEACl (2.0 mg/mL) were added into the perovskite precursor solution. For the fabrication of perovskite films, the perovskite solutions were spin-coated onto the substrates at 1000 rpm for 5 s and 5500 rpm for 30 s. 150 µL of CB as antisolvent was dripped onto the substrate quickly at last 15 s during the second spinning step. The substrates were immediately transferred to the hotplate and annealed at 110 °C for 15 min. To enhance device performance, PDADI (0.5 mg/mL) was deposited as a passivation layer on the sample surface using spin-coating. For the surface passivation, passivators were spin-coated on perovskite film at 5000 rpm for 30 s. Subsequently, 70 µL of passivator was dropped at 6 s during spin-coating. The passivation layer was thermally treated at 100 °C for 5 min to improve its properties. In details, SAM solution was spin-coated on the substrate at 3000 rpm for 30 s, and annealed at 100 °C for 10 min.",
  "json_file_path": "D:\\pycharmpro\\0330\\Recipe-Language-Model\\seven_ai_layers_robotics\\learning\\data\\fp\\tasks\\Formula Additive 2\\m-Br-PEACl -_ m-F-PEACl.json",
  "created_at": "2026-03-30 17:28:07",
  "meta_info": {
    "Expert": "",
    "Sample_ID_1": "50425,control device",
    "Sample_ID_2": "50009,target device",
    "Analysis_Type": "Formula Additive 2",
    "Sample_ID_1_date": "2025-07-31",
    "Sample_ID_2_date": "2025-07-27",
    "Sample_ID_1_Group_ID": 4,
    "Sample_ID_2_Group_ID": 6
  },
  "status": 1,
  "task_name": "Formula Additive 2"
}
```


## Basic Usage

### Environment Setup
Activate the conda environment and navigate to the agent framework directory.

```bash
conda activate MIAgent
python main.py
```


### Key Modules for Executing Task

- **characterisation_reporting_match.py**: Data-pair matching for characterisation report generation
- **edge_reporting_match.py**: Data-pair matching for edge report generation
- **variable_reporting_match.py**: Data-pair matching for variable report

