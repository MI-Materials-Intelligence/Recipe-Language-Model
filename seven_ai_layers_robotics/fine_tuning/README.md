# Fine-Tuning Layer

## Overview

In the fine-tuning layer, the base model (Qwen3-32B) together with the RecipeQA corpora are taken as the input of this layer. Through low-rank adaptation (LoRA), the model is efficiently adapted to domain-specific recipe knowledge and transformed into a domain-specific RLM as output.



## Layer Structure

```
Fine_Tuning/
└── src/
    ├── llama-api-main/                 # LLaMA-Factory API wrapper
    │   ├── app/
    │   │   ├── api/
    │   │   │   └── endpoints.py
    │   │   ├── models/
    │   │   │   └── schemas.py
    │   │   ├── services/
    │   │   │   ├── auto_running.py
    │   │   │   ├── config_template.py
    │   │   │   └── prepare_training.py
    │   │   ├── config.py
    │   │   ├── main.py
    │   │   └── utils.py
    │   ├── test/
    │   │   ├── check_inference.py
    │   │   ├── check_training.py
    │   │   ├── prepare_training.py
    │   │   ├── run_inference.py
    │   │   ├── run_training.py
    │   │   ├── test_corpora.json
    │   │   └── test_tmux.py
    │   ├── README.md
    │   ├── example_config.yml
    │   └── requirements.txt
    └── test_fine_tuning.py             # End-to-end test script
```

## Input Demo

```json
{
    "instruction": "Based on the perovskite formulation and process description, mechanistically analyze the device's Voc, FF, Jsc, and PCE.",
    "input": "Control Device Fabrication: The hole transport layer (HTL) was fabricated by spin coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto a fluorine-doped tin oxide (FTO) substrate, followed by annealing at 100°C for 10 minutes. …… The control device achieved an average power conversion efficiency (PCE) of 15.6% with a short-circuit current density (JSC) of 20.8 mA/cm², an open-circuit voltage (VOC) of 1.01 V, and a fill factor (FF) of 74.3%. Optimization Device Fabrication: The hole transport layer (HTL) was fabricated by spin-coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto an FTO substrate, followed by annealing at 100°C for 10 minutes. …… The optimised device achieved an average power conversion efficiency (PCE) of 17.4% with a short-circuit current density (JSC) of 21.5 mA/cm², an open-circuit voltage (VOC) of 1.09 V, and a fill factor (FF) of 74.3%.",
    "output": "<think>Alright, let's tackle this problem. I need to analyze why the optimized device with PEAI shows better performance compared to the control. ……</think><answer>Methylammonium chloride (MACl) is a small, volatile additive composed of a methylammonium cation (MA⁺) and a chloride anion (Cl⁻) that is commonly used to assist in perovskite film formation. …… As a result, replacing MACl with PEAI leads to clear improvements in performance: the PCE increases from 15.6% to 17.4%, the VOC increases from 1.01 V to 1.09 V due to the suppression of nonradiative recombination, and the JSC increases from 20.8 to 21.5 mA cm⁻² due to better crystallinity and a reduced defect density [DOI:10.1038/s41566-019-0398-2].</answer>"
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

- **llama-api-main/app/api/endpoints.py**: API endpoint definitions
- **llama-api-main/app/services/**: Training preparation and automation services
- **test_fine_tuning.py**: End-to-end test script
