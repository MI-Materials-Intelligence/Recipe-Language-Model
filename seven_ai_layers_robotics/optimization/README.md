# Optimization Layer

## Overview

In the optimization layer, the RLM to be optimised and preference pairs of positive and negative samples are taken as the input of this layer. Through atomic skill of Direct Preference Optimisation (DPO), an optimised RLM is obtained as output. This layer further aligns the model towards preference-consistent and high-performance recipe recommendation.


## Layer Structure with Atomic Skills

```
Optimization/
├── data/                              
└── src/
    ├── DPOTrainDataExporter.py       
    └── optimization_api/            
        ├── app/
        │   ├── api/
        │   │   └── endpoints.py
        │   ├── models/
        │   │   └── schemas.py
        │   ├── services/
        │   │   ├── auto_running.py
        │   │   ├── config_template.py
        │   │   └── prepare_training.py
        │   ├── config.py
        │   ├── main.py
        │   └── utils.py
        ├── examples/
        │   ├── check_inference.py
        │   ├── check_training.py
        │   ├── prepare_training.py
        │   ├── run_inference.py
        │   ├── run_training.py
        │   ├── test_config_example.yaml
        │   ├── test_tmux.py
        │   └── train_config_example.yaml
        ├── train_meta_info/
        │   ├── api_test.json
        │   ├── api_test_new.json
        │   ├── api_test_new_1.json
        │   ├── api_test_new_2.json
        │   ├── inference.yaml
        │   └── qwena30_lora_dpo.yaml
        ├── README.md
        ├── example_config.yml
        └── requirements.txt
```

## Input Demo

```json
{"1_Abstract": " Inverted (p–i–n) perovskite solar cells are highly promising for efficient and stable photovoltaics, but their performance remains constrained by non-radiative recombination at buried interfaces and insufficient control over perovskite crystallization. …… This rational, multi-parameter optimization provides a scalable and effective pathway toward high-performance, industrially viable inverted perovskite solar cells.", 
"2_Introduction": "The device displayed a champion PCE of 15.9%, with a VOC of 0.98 V, a JSC of 20.8 mA/cm², and an FF of 77.7%. 1.73 mol/L perovskite precursor solution with the composition of Cs0.05MA0.1FA0.85PbI3.0 was prepared. ……  Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"3_Result_Discussion": "The device lacks an interfacial layer designed to mitigate interfacial recombination and improve perovskite crystallization. …… Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"4_Conclusion": {"4_1_Table": "| F/P Optimization | Performance | Mechanism |\n| Introduction of 4,4,4-NA SAM (0.33 mg/mL in ethanol) and reduction of perovskite precursor concentration to 1.65 mol/L with optimized antisolvent (150 µL ethyl acetate at 15 s). …… "},
"5_Supporting_Information": "4,4,4-NA acts as a multifunctional interfacial modifier. …… These effects collectively prolong photoluminescence lifetime and improve charge transport and extraction, thereby contributing to enhanced device performance"}

{"score": {"overall": 0.76, "Mechanistic_Reasoning": 0.36, "Recipe_Recommendation": 0.40}}
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
   Run SQL script to create tables (skip if already executed by other layers).
   ```bash
   cd seven_ai_layers_robotics && mysql -u <user> -p <database> < schema.sql
   ```

3. **Configure Settings**  
   Copy `config.example.toml` to `config.toml` and edit with your database connection and API keys.

4. **Deploy Service**  
   Deploy the optimization_api service on the server first (refer to `src/optimization_api/README.md` for details).

5. **Run Optimization Pipeline**  
   Execute the complete optimization pipeline from project root:
   ```bash
   python main.py optimization --item-name test1
   ```
   
   This will automatically execute three workflows:
   - Export training data from database
   - Call training preparation API
   - Optimize questions and write back to database

### Key Modules

- **DPOTrainDataExporter**: Complete optimization pipeline including:
  - Export MIRecipe records to CSV
  - Call training preparation API
  - Optimize questions using LLM and write results back to database
- **optimization_api**: DPO training API service for model training
