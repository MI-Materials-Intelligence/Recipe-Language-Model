# LLaMA-Factory API Service

A FastAPI service for preparing datasets, generating LLaMA-Factory configuration files, launching training and inference jobs in `tmux`, exporting merged LoRA weights, and operating existing YAML-based workflows through HTTP APIs.

This project is designed for two common production patterns:

1. **Template-based workflow**: upload corpora, let the service infer the dataset type, generate YAML files, and run training / inference / export by `item_name`.
2. **Config-file workflow**: upload your own LLaMA-Factory YAML files and execute them directly with API requests.

---

## 1. What this service does

This service wraps several repetitive LLaMA-Factory operations behind HTTP endpoints so that another system, script, scheduler, or agent can trigger them programmatically.

It currently supports:

- Preparing local corpora for training jobs
- Auto-generating `dataset_info.json`
- Generating training / inference / merge YAML files under the LLaMA-Factory `examples/` directory
- Running `llamafactory-cli train` in a detached `tmux` session
- Running `llamafactory-cli api` for Hugging Face backend inference in a detached `tmux` session
- Running a vLLM OpenAI-compatible inference server in a detached `tmux` session
- Running `llamafactory-cli export` either synchronously or in a detached `tmux` session
- Uploading external YAML files into the correct LLaMA-Factory `examples/` subdirectories
- Stopping jobs and checking whether sessions have already exited

---

## 2. Supported workflows

### Workflow A: Template-based workflow

Use this when you want the service to prepare everything for you.

Typical flow:

1. Upload one or more corpus files with `/prepare-training`
2. The service:
   - copies files into the corpus workspace
   - infers dataset type
   - generates `dataset_info.json`
   - generates train / inference / merge YAML files
   - writes training metadata under `TRAIN_META_INFO_ROOT`
3. Start training with `/run-training`
4. Check training completion with `/train-finish-check`
5. Start Hugging Face inference with `/run-inference`
6. Export merged LoRA weights with `/merge-lora`
7. Start vLLM inference on the merged model with `/run-inference-vllm`

### Workflow B: Config-file workflow

Use this when you already maintain your own LLaMA-Factory YAML files.

Typical flow:

1. Upload train / merge / inference YAML files with `/upload-config-files`
2. Launch training directly from a YAML file with `/run-training-config`
3. Run export directly from a merge YAML file with `/merge-lora-config`
4. Stop or check the underlying `tmux` session with `/stop-session` and `/session-stop-check`

This workflow maps naturally to shell commands such as:

```bash
nohup bash -c 'DISABLE_VERSION_CHECK=1 CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 llamafactory-cli train examples/train_lora/your_job.yaml' > your_job.log 2>&1 &
```

and:

```bash
DISABLE_VERSION_CHECK=1 llamafactory-cli export examples/merge_lora/your_merge.yaml
```

The API service does not use `nohup` internally. It uses detached `tmux` sessions for long-running jobs.

---

## 3. Project layout

```text
LLaMA-API/
├── app/
│   ├── api/                  # FastAPI routes
│   ├── models/               # Pydantic schemas
│   ├── services/             # Training preparation and job runners
│   ├── config.py             # Config loader
│   └── main.py               # FastAPI app entrypoint
├── demo_configs/             # Example train / merge / serve files
├── demo_corpora/             # Example corpus files
├── docs/
│   └── API_USAGE_EXAMPLES.md # Copy-paste API examples
├── test/                     # API test scripts
├── train_meta_info/          # Generated metadata for prepared jobs
├── config.yml                # Local runtime config
├── example_config.yml        # Example runtime config
├── requirements.txt
└── README.md
```

---

## 4. Prerequisites

Make sure the target machine has the following installed and usable:

- Python 3.12
- Conda
- `tmux`
- A working LLaMA-Factory installation
- GPU drivers and CUDA runtime required by your training / inference stack
- Optional: vLLM, if you plan to use `/run-inference-vllm`

The service assumes LLaMA-Factory is already present at `LLAMA_FACTORY_ROOT` and can be executed inside the configured Conda environment.

---

## 5. Environment setup

Create and activate the API service environment:

```bash
conda create -n llama_api python=3.12
conda activate llama_api
pip install -r requirements.txt
```

Start from the example configuration:

```bash
cp example_config.yml config.yml
```

Then edit `config.yml` to match your environment.

---

## 6. Runtime configuration

The service reads runtime settings from `config.yml`.

### Example

```yaml
CONDA_ENV: "llama_f"
LLAMA_FACTORY_ROOT: "/data/sunyao/Workspace/Projects/LLaMA-Factory"
BASE_MODEL_DICT:
  "deepseek3":
    "model_path": "/data/opt/LLM_Base_Model/DeepSeek-V3-0324/"
    "template": "deepseek3"
  "qwen3":
    "model_path": "/data/opt/LLM_Base_Model/Qwen-3-14B/"
    "template": "qwen3"
TRAIN_META_INFO_ROOT: "/data/sunyao/Workspace/Projects/LLaMA-API/train_meta_info"
LORA_OUTPUT_ROOT: "/data/sunyao/Workspace/Models/LLM_lora_SFT/saves"
MERGED_OUTPUT_ROOT: "/data/sunyao/Workspace/Models/LLM_lora_SFT/merged"
CORPORA_UPLOAD_ROOT: "/data/sunyao/Workspace/Projects/LLaMA-API/uploaded_corpora"
```

### Configuration fields

| Field | Description |
|---|---|
| `CONDA_ENV` | Conda environment used to run LLaMA-Factory and vLLM commands. |
| `LLAMA_FACTORY_ROOT` | Root directory of your LLaMA-Factory checkout. |
| `BASE_MODEL_DICT` | Model template registry used by `/prepare-training`. Each entry maps a template name to a base model path and template identifier. |
| `TRAIN_META_INFO_ROOT` | Directory used to store generated metadata for prepared jobs. |
| `LORA_OUTPUT_ROOT` | Root directory for training outputs and relative log files. |
| `MERGED_OUTPUT_ROOT` | Root directory for merged model exports used by vLLM item-based inference. |
| `CORPORA_UPLOAD_ROOT` | Workspace for uploaded corpus files and prepared dataset directories. |

### Notes about `BASE_MODEL_DICT`

- The key must match the `model_template` submitted to `/prepare-training`.
- The key must also exist in the built-in template registry.
- In the current codebase, built-in template names are:
  - `qwen3`
  - `deepseek3`

If a template is missing from `BASE_MODEL_DICT`, `/prepare-training` will fail even if the template exists in code.

---

## 7. How the service maps shell commands to APIs

### Template-based training

API:

```text
POST /run-training
```

Equivalent command pattern:

```bash
llamafactory-cli train examples/train_lora/<item_name>.yaml
```

### Config-file training

API:

```text
POST /run-training-config
```

Equivalent command pattern:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 llamafactory-cli train examples/train_lora/<config>.yaml
```

Additional environment variables, such as `DISABLE_VERSION_CHECK=1`, are passed via the `env` field.

### Hugging Face backend inference

API:

```text
POST /run-inference
```

Equivalent command pattern:

```bash
API_PORT=9004 CUDA_VISIBLE_DEVICES=0 llamafactory-cli api examples/inference/<item_name>.yaml
```

### LoRA export / merge

API:

```text
POST /merge-lora
POST /merge-lora-config
```

Equivalent command pattern:

```bash
llamafactory-cli export examples/merge_lora/<config>.yaml
```

### vLLM inference

API:

```text
POST /run-inference-vllm
```

Current implementation pattern:

```bash
python -m vllm.entrypoints.openai.api_server --model <merged_model_path> ... --port <api_port>
```

The current code launches vLLM from Python and stores the merged model under:

```text
<MERGED_OUTPUT_ROOT>/<item_name>
```

---

## 8. Running the service

Start the API server locally:

```bash
uvicorn app.main:app --reload
```

Expose it on a specific host and port:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Useful built-in docs:

- Swagger UI: `http://<host>:<port>/docs`
- ReDoc: `http://<host>:<port>/redoc`

Example:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

Then open:

```text
http://localhost:9000/docs
```

---

## 9. API endpoint summary

Base URL:

```text
http://<host>:<port>/
```

### Item-based endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/prepare-training` | Upload corpora and auto-generate dataset metadata and YAML files. |
| `POST` | `/run-training` | Start training for a prepared `item_name`. |
| `POST` | `/stop-training` | Stop the training session for a prepared `item_name`. |
| `GET` | `/train-finish-check` | Check whether the training session has exited. |
| `POST` | `/run-inference` | Start Hugging Face backend inference for a prepared `item_name`. |
| `POST` | `/stop-inference` | Stop the Hugging Face inference session for a prepared `item_name`. |
| `GET` | `/inference-stop-check` | Check whether the Hugging Face inference session has exited. |
| `POST` | `/merge-lora` | Export merged LoRA weights for a prepared `item_name`. |
| `POST` | `/run-inference-vllm` | Start vLLM inference for a merged model under `MERGED_OUTPUT_ROOT/<item_name>`. |
| `POST` | `/stop-inference-vllm` | Stop the vLLM session for a merged model. |

### Config-file endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/upload-config-files` | Upload train / merge / inference YAML files into the LLaMA-Factory `examples/` folders. |
| `POST` | `/run-training-config` | Run training directly from a YAML file. |
| `POST` | `/merge-lora-config` | Run `llamafactory-cli export` directly from a merge YAML file. |
| `POST` | `/stop-session` | Stop any managed `tmux` session by its name. |
| `GET` | `/session-stop-check` | Check whether a named `tmux` session has already exited. |

---

## 10. Detailed endpoint reference

## 10.1 `POST /prepare-training`

Prepare local corpora and generate all required metadata and YAML files for a training job.

### Request type

`multipart/form-data`

### Form fields

| Field | Type | Required | Description |
|---|---|---|---|
| `item_name` | string | Yes | Logical job name used for generated files and output directories. |
| `model_template` | string | Yes | Built-in template name such as `qwen3` or `deepseek3`. |
| `corpora_info` | file | Yes | One or more uploaded corpus files. Repeat the same field name for multiple files. |

### Example

```bash
curl -X POST "http://127.0.0.1:8000/prepare-training" \
  -F "item_name=qwen3_demo_job" \
  -F "model_template=qwen3" \
  -F "corpora_info=@demo_corpora/sft_alpaca.json"
```

### Response

```json
{
  "status": "prepared"
}
```

### What it generates

For a successful request, the service will typically generate:

- raw uploaded corpora under `CORPORA_UPLOAD_ROOT/<item_name>/raw/`
- prepared local dataset workspace under `CORPORA_UPLOAD_ROOT/prepared/<item_name>/`
- `dataset_info.json` in the prepared dataset directory
- training YAML under `LLAMA_FACTORY_ROOT/examples/train_lora/<item_name>.yaml`
- inference YAML under `LLAMA_FACTORY_ROOT/examples/inference/<item_name>.yaml` for SFT jobs
- merge YAML under `LLAMA_FACTORY_ROOT/examples/merge_lora/<item_name>.yaml` for SFT jobs
- metadata JSON under `TRAIN_META_INFO_ROOT/<item_name>.json`

### Supported local corpus patterns

The current auto-inference logic is intended for local JSON / JSONL corpora in one of these shapes:

- Alpaca-style SFT (`instruction`, `input`, `output`)
- ShareGPT-style chat (`conversations`)
- OpenAI-style chat (`messages`)
- Plain-text pretraining (`text`)

The service will select `sft` or `pt` automatically based on the uploaded data.

---

## 10.2 `POST /run-training`

Start training for a prepared `item_name`.

### Request body

```json
{
  "item_name": "qwen3_demo_job",
  "gpu_ids": [0, 1]
}
```

### Response

```json
{
  "status": "started"
}
```

### Session and log conventions

- `tmux` session: `train_<item_name>`
- config path: `examples/train_lora/<item_name>.yaml`
- log file: `<LORA_OUTPUT_ROOT>/<item_name>/training.log`

---

## 10.3 `POST /stop-training`

Stop the training session for a prepared `item_name`.

### Request body

```json
{
  "item_name": "qwen3_demo_job"
}
```

### Response

```json
{
  "status": "stopped"
}
```

---

## 10.4 `GET /train-finish-check`

Check whether the training session has already exited.

### Example

```bash
curl "http://127.0.0.1:8000/train-finish-check?item_name=qwen3_demo_job"
```

### Response

```json
{
  "stopped": false
}
```

---

## 10.5 `POST /run-inference`

Start Hugging Face backend inference for a prepared `item_name`.

### Request body

```json
{
  "item_name": "qwen3_demo_job",
  "gpu_id": 0,
  "api_port": 9004
}
```

### Response

```json
{
  "status": "started"
}
```

### Session and log conventions

- `tmux` session: `inference_<item_name>`
- config path: `examples/inference/<item_name>.yaml`
- log file: `<LORA_OUTPUT_ROOT>/<item_name>/inference.log`

---

## 10.6 `POST /stop-inference`

Stop the Hugging Face backend inference session for a prepared `item_name`.

### Request body

```json
{
  "item_name": "qwen3_demo_job"
}
```

### Response

```json
{
  "status": "stopped"
}
```

---

## 10.7 `GET /inference-stop-check`

Check whether the Hugging Face backend inference session has already exited.

### Example

```bash
curl "http://127.0.0.1:8000/inference-stop-check?item_name=qwen3_demo_job"
```

### Response

```json
{
  "stopped": false
}
```

---

## 10.8 `POST /merge-lora`

Run LoRA export for a prepared `item_name` using the generated merge YAML.

### Request body

```json
{
  "item_name": "qwen3_demo_job"
}
```

### Response

```json
{
  "status": "merged"
}
```

### Notes

- This endpoint runs export synchronously.
- The merge config path is loaded from `TRAIN_META_INFO_ROOT/<item_name>.json`.

---

## 10.9 `POST /run-inference-vllm`

Start vLLM inference for a merged model.

### Request body

```json
{
  "item_name": "qwen3_32b_v8-4",
  "gpu_id": 4,
  "api_port": 9042
}
```

### Response

```json
{
  "status": "started"
}
```

### Session and log conventions

- `tmux` session: `inference_vllm_<item_name>`
- model path: `<MERGED_OUTPUT_ROOT>/<item_name>`
- log file: `<LORA_OUTPUT_ROOT>/<item_name>/inference_vllm.log`

### Current implementation notes

The current vLLM launcher uses a fixed server command pattern with parameters such as:

- `--distributed-executor-backend mp`
- `--tensor-parallel-size 1`
- `--dtype auto`
- `--kv-cache-dtype auto`
- `--max-model-len 8192`
- `--max-num-batched-tokens 16384`
- `--max-num-seqs 32`
- `--enable-chunked-prefill`
- `--gpu-memory-utilization 0.80`
- `--max-logprobs 0`

If you need fully custom vLLM arguments, the current code should be extended further.

---

## 10.10 `POST /stop-inference-vllm`

Stop the vLLM inference session for a merged model.

### Request body

```json
{
  "item_name": "qwen3_32b_v8-4"
}
```

### Response

```json
{
  "status": "stopped"
}
```

---

## 10.11 `POST /upload-config-files`

Upload YAML files directly into the LLaMA-Factory `examples/` folders.

### Request type

`multipart/form-data`

### Supported form fields

| Field | Destination |
|---|---|
| `train_config` | `LLAMA_FACTORY_ROOT/examples/train_lora/` |
| `merge_config` | `LLAMA_FACTORY_ROOT/examples/merge_lora/` |
| `inference_config` | `LLAMA_FACTORY_ROOT/examples/inference/` |

You may upload any combination of these fields in one request.

### Example

```bash
curl -X POST "http://127.0.0.1:8000/upload-config-files" \
  -F "train_config=@demo_configs/qwen3_32b_lora_sft_COT_v8-4.yaml" \
  -F "merge_config=@demo_configs/qwen3_32b_lora_merge_COT_v8-4.yaml"
```

### Response

```json
{
  "status": "uploaded",
  "saved_paths": [
    "/path/to/LLaMA-Factory/examples/train_lora/qwen3_32b_lora_sft_COT_v8-4.yaml",
    "/path/to/LLaMA-Factory/examples/merge_lora/qwen3_32b_lora_merge_COT_v8-4.yaml"
  ]
}
```

---

## 10.12 `POST /run-training-config`

Start training directly from a YAML file.

### Request body

```json
{
  "config_path": "examples/train_lora/qwen3_32b_lora_sft_COT_v8-4.yaml",
  "gpu_ids": [0, 1, 2, 3, 4, 5, 6, 7],
  "session_name": "train_qwen3_32b_lora_sft_COT_v8-4",
  "log_file": "qwen3_32b_lora_sft_COT_v8-4.log",
  "env": {
    "DISABLE_VERSION_CHECK": "1"
  }
}
```

### Response

```json
{
  "status": "started"
}
```

### Notes

- `CUDA_VISIBLE_DEVICES` is generated automatically from `gpu_ids`.
- If `session_name` is omitted, the service derives one from `config_path`.
- If `log_file` is relative, it is placed under `LORA_OUTPUT_ROOT`.

---

## 10.13 `POST /merge-lora-config`

Run `llamafactory-cli export` directly from a merge YAML file.

### Synchronous request body

```json
{
  "config_path": "examples/merge_lora/qwen3_32b_lora_merge_COT_v8-4.yaml",
  "env": {
    "DISABLE_VERSION_CHECK": "1"
  },
  "run_async": false
}
```

### Synchronous response

```json
{
  "status": "merged"
}
```

### Asynchronous request body

```json
{
  "config_path": "examples/merge_lora/qwen3_32b_lora_merge_COT_v8-4.yaml",
  "session_name": "export_qwen3_32b_lora_merge_COT_v8-4",
  "log_file": "qwen3_32b_lora_merge_COT_v8-4.log",
  "env": {
    "DISABLE_VERSION_CHECK": "1"
  },
  "run_async": true
}
```

### Asynchronous response

```json
{
  "status": "started"
}
```

---

## 10.14 `POST /stop-session`

Stop any managed `tmux` session by name.

### Request body

```json
{
  "session_name": "train_qwen3_32b_lora_sft_COT_v8-4"
}
```

### Response

```json
{
  "status": "stopped"
}
```

---

## 10.15 `GET /session-stop-check`

Check whether a named `tmux` session has already exited.

### Example

```bash
curl "http://127.0.0.1:8000/session-stop-check?session_name=train_qwen3_32b_lora_sft_COT_v8-4"
```

### Response

```json
{
  "stopped": false
}
```

---

## 11. End-to-end examples

### Example A: Template-based SFT flow

#### Step 1: Prepare training files

```bash
curl -X POST "http://127.0.0.1:8000/prepare-training" \
  -F "item_name=my_job" \
  -F "model_template=qwen3" \
  -F "corpora_info=@demo_corpora/sft_alpaca.json"
```

#### Step 2: Start training

```bash
curl -X POST "http://127.0.0.1:8000/run-training" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "my_job",
    "gpu_ids": [0, 1]
  }'
```

#### Step 3: Check training

```bash
curl "http://127.0.0.1:8000/train-finish-check?item_name=my_job"
```

#### Step 4: Export merged weights

```bash
curl -X POST "http://127.0.0.1:8000/merge-lora" \
  -H "Content-Type: application/json" \
  -d '{"item_name": "my_job"}'
```

#### Step 5: Start Hugging Face inference

```bash
curl -X POST "http://127.0.0.1:8000/run-inference" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "my_job",
    "gpu_id": 0,
    "api_port": 9004
  }'
```

#### Step 6: Start vLLM inference on the merged model

```bash
curl -X POST "http://127.0.0.1:8000/run-inference-vllm" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "my_job",
    "gpu_id": 0,
    "api_port": 9042
  }'
```

### Example B: Config-file training flow

#### Step 1: Upload YAML files

```bash
curl -X POST "http://127.0.0.1:8000/upload-config-files" \
  -F "train_config=@demo_configs/qwen3_32b_lora_sft_COT_v8-4.yaml" \
  -F "merge_config=@demo_configs/qwen3_32b_lora_merge_COT_v8-4.yaml"
```

#### Step 2: Start training from YAML

```bash
curl -X POST "http://127.0.0.1:8000/run-training-config" \
  -H "Content-Type: application/json" \
  -d '{
    "config_path": "examples/train_lora/qwen3_32b_lora_sft_COT_v8-4.yaml",
    "gpu_ids": [0, 1, 2, 3, 4, 5, 6, 7],
    "session_name": "train_qwen3_32b_lora_sft_COT_v8-4",
    "log_file": "qwen3_32b_lora_sft_COT_v8-4.log",
    "env": {
      "DISABLE_VERSION_CHECK": "1"
    }
  }'
```

#### Step 3: Check the session

```bash
curl "http://127.0.0.1:8000/session-stop-check?session_name=train_qwen3_32b_lora_sft_COT_v8-4"
```

#### Step 4: Run export synchronously

```bash
curl -X POST "http://127.0.0.1:8000/merge-lora-config" \
  -H "Content-Type: application/json" \
  -d '{
    "config_path": "examples/merge_lora/qwen3_32b_lora_merge_COT_v8-4.yaml",
    "env": {
      "DISABLE_VERSION_CHECK": "1"
    },
    "run_async": false
  }'
```

#### Step 5: Or run export asynchronously

```bash
curl -X POST "http://127.0.0.1:8000/merge-lora-config" \
  -H "Content-Type: application/json" \
  -d '{
    "config_path": "examples/merge_lora/qwen3_32b_lora_merge_COT_v8-4.yaml",
    "session_name": "export_qwen3_32b_lora_merge_COT_v8-4",
    "log_file": "qwen3_32b_lora_merge_COT_v8-4.log",
    "env": {
      "DISABLE_VERSION_CHECK": "1"
    },
    "run_async": true
  }'
```

---

## 12. Testing

The `test/` directory contains helper scripts for most endpoints.

### Typical usage

```bash
python test/upload_config_files.py
python test/run_training_config.py
python test/session_stop_check.py --session-name train_qwen3_32b_lora_sft_COT_v8-4
python test/stop_session.py --session-name train_qwen3_32b_lora_sft_COT_v8-4
```

If your API server is not running on port `8000`, pass `--base-url`:

```bash
python test/run_training.py --base-url http://127.0.0.1:9000
```

See `test/README.md` for endpoint-specific examples.

---

## 13. Logs, sessions, and outputs

### `tmux` session naming

| Workflow | Session name pattern |
|---|---|
| Template training | `train_<item_name>` |
| Template inference | `inference_<item_name>` |
| Template vLLM inference | `inference_vllm_<item_name>` |
| Config training | provided `session_name`, or auto-generated from the YAML filename |
| Async export | provided `session_name`, or auto-generated from the YAML filename |

### Log file behavior

- Template-based training logs go to `<LORA_OUTPUT_ROOT>/<item_name>/training.log`
- Template-based inference logs go to `<LORA_OUTPUT_ROOT>/<item_name>/inference.log`
- Template-based vLLM logs go to `<LORA_OUTPUT_ROOT>/<item_name>/inference_vllm.log`
- Config-based relative log file names are stored under `LORA_OUTPUT_ROOT`
- Config-based absolute log file paths are used as-is

### Output directories

- LoRA training outputs: under `LORA_OUTPUT_ROOT/<item_name>/`
- Merged exports: under `MERGED_OUTPUT_ROOT/<item_name>/`
- Prepared dataset workspace: under `CORPORA_UPLOAD_ROOT/prepared/<item_name>/`

---

## 14. Operational notes and current limitations

- Long-running tasks are managed with `tmux`, not a task queue.
- `/merge-lora` runs synchronously; `/merge-lora-config` supports both synchronous and asynchronous execution.
- `/run-inference-vllm` currently targets merged models under `MERGED_OUTPUT_ROOT/<item_name>` rather than arbitrary absolute model paths.
- `/run-inference-vllm` currently uses a fixed internal command template instead of fully user-controlled vLLM arguments.
- The current auto corpus inference path is best suited for JSON / JSONL datasets whose schema matches the built-in detection logic.
- Template-based requests depend on both the built-in code templates and matching entries in `config.yml`.

---

## 15. Troubleshooting

### `prepare-training` fails with `invalid template`

Make sure `model_template` matches a built-in template name such as `qwen3` or `deepseek3`.

### `prepare-training` fails with `template not configured in BASE_MODEL_DICT`

Add the template to `BASE_MODEL_DICT` in `config.yml`.

### Training or inference returns `failed`

Check:

- whether `tmux` is installed
- whether the configured Conda environment exists
- whether `LLAMA_FACTORY_ROOT` is correct
- whether the referenced YAML file exists under the correct `examples/` directory
- whether the selected GPUs are visible and available

### Export fails

Check the merge YAML file first:

- `model_name_or_path`
- `adapter_name_or_path`
- `export_dir`
- `template`

### vLLM fails to start

Check:

- whether vLLM is installed in the configured Conda environment
- whether the merged model exists under `MERGED_OUTPUT_ROOT/<item_name>`
- whether the requested port is free
- whether the selected GPU is available

---

## 16. Additional documentation

- API examples: `docs/API_USAGE_EXAMPLES.md`
- Test script usage: `test/README.md`
- Demo train / merge configs: `demo_configs/`
- Demo corpora: `demo_corpora/`

---

## 17. References

- LLaMA-Factory: https://github.com/hiyouga/LLaMA-Factory
- LLaMA-Factory docs: https://llamafactory.readthedocs.io/
- vLLM docs: https://docs.vllm.ai/
