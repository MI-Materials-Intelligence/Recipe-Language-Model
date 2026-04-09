# API Usage Examples

## 1. Upload train / merge / inference YAML files

```bash
curl -X POST "http://127.0.0.1:8000/upload-config-files" \
  -F "train_config=@demo_configs/qwen3_32b_lora_sft_COT_v8-4.yaml" \
  -F "merge_config=@demo_configs/qwen3_32b_lora_merge_COT_v8-4.yaml"
```

Example response:

```json
{
  "status": "uploaded",
  "saved_paths": [
    "/path/to/LLaMA-Factory/examples/train_lora/qwen3_32b_lora_sft_COT_v8-4.yaml",
    "/path/to/LLaMA-Factory/examples/merge_lora/qwen3_32b_lora_merge_COT_v8-4.yaml"
  ]
}
```

## 2. Start training from a YAML file

Equivalent shell command:

```bash
nohup bash -c 'DISABLE_VERSION_CHECK=1 CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 llamafactory-cli train examples/train_lora/qwen3_32b_lora_sft_COT_v8-2.yaml' > qwen3_32b_lora_sft_COT_v8-2.log 2>&1 &
```

API request:

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

Example response:

```json
{
  "status": "started"
}
```

## 3. Check whether the training session has stopped

```bash
curl "http://127.0.0.1:8000/session-stop-check?session_name=train_qwen3_32b_lora_sft_COT_v8-4"
```

Example response:

```json
{
  "stopped": false
}
```

## 4. Stop a training or export session by session name

```bash
curl -X POST "http://127.0.0.1:8000/stop-session" \
  -H "Content-Type: application/json" \
  -d '{
    "session_name": "train_qwen3_32b_lora_sft_COT_v8-4"
  }'
```

Example response:

```json
{
  "status": "stopped"
}
```

## 5. Run LoRA export synchronously

Equivalent shell command:

```bash
DISABLE_VERSION_CHECK=1 llamafactory-cli export examples/merge_lora/qwen3_32b_lora_merge_COT_v8-4.yaml
```

API request:

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

Example response:

```json
{
  "status": "merged"
}
```

## 6. Run LoRA export asynchronously in tmux

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

Example response:

```json
{
  "status": "started"
}
```

## 7. Upload corpora and auto-generate configs

```bash
curl -X POST "http://127.0.0.1:8000/prepare-training" \
  -F "item_name=my_job" \
  -F "model_template=qwen3" \
  -F "corpora_info=@demo_corpora/sft_alpaca.json"
```

## 8. Start template-based training

```bash
curl -X POST "http://127.0.0.1:8000/run-training" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "my_job",
    "gpu_ids": [0, 1]
  }'
```

## 9. Run Hugging Face backend inference

```bash
curl -X POST "http://127.0.0.1:8000/run-inference" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "my_job",
    "gpu_id": 0,
    "api_port": 8001
  }'
```

## 10. Run merged-model vLLM inference

```bash
curl -X POST "http://127.0.0.1:8000/run-inference-vllm" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "qwen3_32b_v8-4",
    "gpu_id": 4,
    "api_port": 9042
  }'
```

## 11. Stop item-based jobs

Stop training:

```bash
curl -X POST "http://127.0.0.1:8000/stop-training" \
  -H "Content-Type: application/json" \
  -d '{"item_name": "my_job"}'
```

Stop inference:

```bash
curl -X POST "http://127.0.0.1:8000/stop-inference" \
  -H "Content-Type: application/json" \
  -d '{"item_name": "my_job"}'
```

Stop vLLM inference:

```bash
curl -X POST "http://127.0.0.1:8000/stop-inference-vllm" \
  -H "Content-Type: application/json" \
  -d '{"item_name": "qwen3_32b_v8-4"}'
```
