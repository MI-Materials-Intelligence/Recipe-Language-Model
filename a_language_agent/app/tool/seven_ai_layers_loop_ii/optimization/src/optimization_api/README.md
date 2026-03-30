

## Introduction

This service provides an API interface for the **Optimization Layer**, enabling:

1. **Corpus Preparation**: Merge the QA pairs and socres from evaluation layer and build DPO training corpora, generate training configurations for use with [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory).
2. **Training Automation**: Automatically launch training and inference sessions in a `tmux` session.

We recommend to test all the functions in ./examples folder with ready examples. Make aure you can training your model with LLaMA-Factory before deploying the API service.
---

## Environment Setup

```bash
conda activate llamafactory
pip install -r requirements.txt
```

---

## Configuration

Before running the service, define the following environment variables in `config.yml` (you can refer `example_config.yml`):

```env
CONDA_ENV: "llamafactory_new"
LLAMA_FACTORY_ROOT: "/home/maning/git/LLaMA-Factory_20251215/LlamaFactory/"
BASE_MODEL_ROOT: "/data/opt/LLM_Base_Model/Qwen2.5-0.5B-Instruct/"
TRAIN_META_INFO_ROOT: "/data/exp_maning/optimization_API/train_meta_info"
LORA_OUTPUT_ROOT: "/data/opt/LLM_lora_SFT/saves/DPO_LORA/"

```

---

## Running the Service

To start the API server (default port is `8000`):

```bash
uvicorn app.main:app --reload
```

### Run on a Specific Port

To run the API server on a **custom port**, use the `--port` argument:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 9047
```

- `--host 0.0.0.0`: Makes the API accessible externally (not just localhost).
- `--port 8080`: Replace `8080` with your desired port.

---

## API Endpoints

Base URL: `http://<host>:<port>/` (e.g., `http://localhost:8000/`)

---

### 📦 `/prepare-training` — Prepare Training

**Method**: `POST`  
**Description**: Merge corpora and generate training configuration files.

#### Request Body

```json
    corpora_files = [
        (
            "corpora_info",
            (
                "MIRecipe",
                open(
                    "/data/exp_maning/optimization_API/test/MIRecipe.csv",
                    "rb",
                ),
            ),
        ),
    ]


    data = {
        "item_name": "<item_name>",
        "base_model_path": "/data/opt/LLM_Base_Model/Qwen3-32B/",
        "DPO_train_config_template": "/data/exp_maning/optimization_API/test/train_config_example.yaml",
        "inference_config_template": "/data/exp_maning/optimization_API/test/test_config_example.yaml"
    }

    response = requests.post(url, files=corpora_files, data=data)

```

#### Response

```json
{
  "status": "prepared" // or "failed"
}
```

---

### 🚀 `/run-training` — Start Training

**Method**: `POST`  
**Description**: Launch a training session in a tmux window.

#### Request Body

```json
 payload = {
        "gpu_ids": [0, 1,2,3],
        "item_name": "<item_name>",
    }
```

#### Response

```json
{
  "status": "started" // or "failed"
}
```

---

### 🤖 `/run-inference` — Start Inference

**Method**: `POST`  
**Description**: Launch an inference service on a specified port.

#### Request Body

```json
payload = {
        "gpu_id": [0,1,2,3],
        "api_port": 9081, 
        "item_name": "<item_name>",
    }
```

#### Response

```json
{
  "status": "started" // or "failed"
}
```

---

### 📈 `/check-training-finish` — Check Training Status

**Method**: `GET`  
**Description**: Check if a training session has completed.

#### Request Parameters (query or JSON body)

```json
{
  "item_name": "<item_name>"
}
```

#### Response

```json
{
  "stopped": true // or false
}
```

---

### 🛑 `/check-inference-stop` — Check Inference Service Status

**Method**: `GET`  
**Description**: Check if the inference service has stopped.

#### Request Parameters (query or JSON body)

```json
{
  "item_name": "<item_name>"
}
```

#### Response

```json
{
  "stopped": true // or false
}
```

---


---

## Example: Run API on Port 9000

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

We recommend to test all the functions in ./test folder with ready exampls.
