# Test Scripts

This folder contains small request-based test scripts for the FastAPI service.

## Default base URL

All scripts use `http://127.0.0.1:8000` by default.
You can override it with either:

```bash
export LLAMA_API_BASE_URL=http://127.0.0.1:9047
```

or:

```bash
python test/run_training.py --base-url http://127.0.0.1:9047
```

## Existing item-based workflow

```bash
python test/prepare_training.py
python test/run_training.py
python test/check_training.py
python test/stop_training.py
python test/run_inference.py
python test/check_inference.py
python test/stop_inference.py
python test/run_inference_vllm.py
python test/stop_inference_vllm.py
python test/merge_lora.py
```

## New config-file workflow

Upload demo YAML files first:

```bash
python test/upload_config_files.py
```

Then run training by config:

```bash
python test/run_training_config.py
python test/session_stop_check.py --session-name train_qwen3_32b_lora_sft_COT_v8-4
python test/stop_session.py --session-name train_qwen3_32b_lora_sft_COT_v8-4
```

Run export by config:

```bash
python test/merge_lora_config.py
python test/merge_lora_config.py --run-async
python test/session_stop_check.py --session-name export_qwen3_32b_lora_merge_COT_v8-4
python test/stop_session.py --session-name export_qwen3_32b_lora_merge_COT_v8-4
```

## Local tmux smoke test

```bash
python test/test_tmux.py
```
