# Optimization Layer

## Overview

Direct Preference Optimisation is used to align the RLM towards preference-consistent, high-performance recipe recommendations. 

Key Atomic Skills:
- **DPO Training Data Preparation**: Constructs preference ranking training data from evaluation results
- **Automated Training**: Implements automated DPO fine-tuning based on LLaMA-Factory
- **Inference Deployment**: Deploys optimized models and provides API services
- **Status Monitoring**: Real-time tracking of training and service status

## Layer Structure with Atomic Skills

```
Optimization/
└── src/optimization_api/
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
    │   ├── inference.yaml
    │   └── qwena30_lora_dpo.yaml
    ├── README.md
    ├── example_config.yml
    └── requirements.txt
```

## Database Requirements

Requires access to evaluation scoring data, DPO training records, and optimized model records.

Configuration Example:
```toml
[database]
host = "localhost"
port = 13330
user = "root"
password = "your_password"
database = "rlm_agent"

[optimization]
llama_factory_root = "/path/to/LLaMA-Factory"
base_model_path = "/path/to/base/model"
default_beta = 0.1
default_gpus = [0, 1]
```

## Output Data

Outputs DPO training configurations, DPO training corpora, training metadata, and optimization effectiveness evaluation reports.

## Basic Usage

### Environment Setup

```bash

cd /path/to/LLaMA-Factory
pip install -e ".[torch,metrics]"


cd seven_layers/Optimization/src/optimization_api
pip install -r requirements.txt
```

### Start API Service

```bash
cd seven_layers/Optimization/src/optimization_api
uvicorn app.main:app --reload
```

### Using Optimization API

```python
import requests
import pandas as pd
from pathlib import Path

BASE_URL = "http://localhost:8000"
CSV_FILE = Path("evaluation_results/MIRecipe.csv")
ITEM_NAME = "dpo_20250101_ABC"


with open(CSV_FILE, "rb") as f:
    files = [("corpora_info", ("MIRecipe.csv", f, "text/csv"))]
    data = {
        "item_name": ITEM_NAME,
        "base_model_path": "/path/to/base/model",
        "SFT_adapter_path": "/path/to/sft/adapter"
    }
    response = requests.post(f"{BASE_URL}/prepare-training", files=files, data=data)


response = requests.post(
    f"{BASE_URL}/run-training",
    json={"item_name": ITEM_NAME, "gpu_ids": [0, 1]}
)


while True:
    response = requests.get(
        f"{BASE_URL}/check-training-finish",
        json={"item_name": ITEM_NAME}
    )
    if response.json().get("stopped"):
        print("✅ Training completed!")
        break
    time.sleep(60)


response = requests.post(
    f"{BASE_URL}/run-inference",
    json={"item_name": ITEM_NAME, "gpu_id": 0, "api_port": 9047}
)
```

### Complete Workflow Example

```python

python examples/run_training.py
```

### Key Modules for Executing Task

- **app/api/endpoints.py**: API endpoint definitions
- **app/services/prepare_training.py**: DPO training data preparation
- **app/services/auto_running.py**: Automated running services
- **examples/**: Usage examples and test scripts
