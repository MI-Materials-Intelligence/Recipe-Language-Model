# LLAMA FACTORY API SERVICE

## Introduction

This service provides an API interface for the **RLM-Agent**, enabling:

1. **Corpus Preparation**: Merge corpora and generate training/inference configurations for use with [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory).
2. **Training Automation**: Automatically launch training sessions in a `tmux` session.
3. **Inference Automation**: Automatically launch inference services in a `tmux` session.

---

## Environment Setup

```bash
conda create -n llama_api python=3.12
conda activate llama_api
pip install -r requirements.txt
```

---

## Configuration

Before running the service, define the following environment variables in `config.yml` (you can refer `example_config.yml`):

```env
CONDA_ENV=llamafactory2
LLAMA_FACTORY_ROOT=/data/sunyao/Workspace/Projects/llama
BASE_MODEL_ROOT=/data/opt/LLM_Base_Model/DeepSeek-R1-Distill-Qwen-32B/
TRAIN_META_INFO_ROOT=/data/sunyao/Workspace/Projects/LLaMA-API/train_meta_info
LORA_OUTPUT_ROOT=/data/sunyao/Workspace/Models/LLM_lora_SFT/saves
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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
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
{
  "corpora_info": [
    {
      "name": "<corpora_name>",
      "content": "<corpora_content>"
    }
  ],
  "item_name": "<item_name>"
}
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
{
  "item_name": "<item_name>",
  "gpu_ids": [0, 1]
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
{
  "item_name": "<item_name>",
  "gpu_id": 0,
  "api_port": 9004
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

## Optional Enhancements

- ✅ **Swagger UI**: Access API docs at `/docs` when running with `uvicorn`.
- ✅ **ReDoc UI**: Access detailed schema at `/redoc`.

---

## Example: Run API on Port 9000

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

Then access the API at:  
[http://localhost:9000/docs](http://localhost:9000/docs)

