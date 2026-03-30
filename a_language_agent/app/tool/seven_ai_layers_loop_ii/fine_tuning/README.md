# Fine-Tuning Layer

## Overview

The Fine-Tuning layer performs domain-adaptive fine-tuning of base language models using RecipeQA corpora.

Key Atomic Skills:
- **Training Data Preparation**: Merges multiple corpora and generates standardized training configurations
- **Training Automation**: One-click training launch based on LLaMA-Factory
- **Inference Service**: Automatic deployment of fine-tuned models as API services
- **Status Monitoring**: Real-time tracking of training and inference service status

## Layer Structure with Atomic Skills

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

## Database Requirements

Requires access to training corpora, training records, and inference service records.

Configuration Example:
```toml
[database]
host = "localhost"
port = 13330
user = "root"
password = "your_password"
database = "rlm_agent"

[fine_tuning]
llama_factory_root = "/path/to/LLaMA-Factory"
base_model_path = "/path/to/base/model"
default_gpus = [0, 1]
```

## Output Data

Outputs training configurations, training metadata, inference service configurations, and training status reports.

## Basic Usage

### Environment Setup

```bash
# Install LLaMA-Factory
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]"

# Install Fine-Tuning API dependencies
cd seven_layers/Fine_Tuning/src/llama-api-main
pip install -r requirements.txt
```

### Start API Service

```bash
cd seven_layers/Fine_Tuning/src/llama-api-main
uvicorn app.main:app --reload
```

### Using Training API

```python
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"
MERGED_JSON_PATH = Path("path/to/merged_sft_pairs.json")
ITEM_NAME = "test_20250101"

# 1. Prepare training data   
with open(MERGED_JSON_PATH, "rb") as f:
    files = [("corpora_info", ("merged_sft_pairs.json", f, "application/json"))]
    data = {"item_name": ITEM_NAME}
    response = requests.post(f"{BASE_URL}/prepare-training", files=files, data=data)

# 2. Start training
response = requests.post(
    f"{BASE_URL}/run-training",
    json={"item_name": ITEM_NAME, "gpu_ids": [0]}
)

# 3. Check training status
response = requests.get(
    f"{BASE_URL}/train-finish-check",
    json={"item_name": ITEM_NAME}
)

# 4. Start inference service
response = requests.post(
    f"{BASE_URL}/run-inference",
    json={"item_name": ITEM_NAME, "gpu_id": 0, "api_port": 9045}
)
```

### End-to-End Test

```python
# Run end-to-end test
python src/test_fine_tuning.py
```

### Key Modules for Executing Task

- **llama-api-main/app/api/endpoints.py**: API endpoint definitions
- **llama-api-main/app/services/**: Training preparation and automation services
- **test_fine_tuning.py**: End-to-end test script
