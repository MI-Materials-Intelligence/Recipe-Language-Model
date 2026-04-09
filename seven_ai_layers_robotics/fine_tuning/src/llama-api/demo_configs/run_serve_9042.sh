export CUDA_VISIBLE_DEVICES=4,5
#export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
#  --enable-lora \
#  --lora-modules mytask=/data/opt/LLM_lora_SFT/saves/qwen2.5_32b_R1_v5-8/lora/sft/ \

python -m vllm.entrypoints.openai.api_server \
  --model /data/opt/LLM_lora_SFT/models/qwen3_32b_v8-4 \
  --distributed-executor-backend mp \
  --tensor-parallel-size 2 \
  --dtype auto \
  --kv-cache-dtype auto \
  --max-model-len 8192 \
  --max-num-batched-tokens 16384 \
  --max-num-seqs 32 \
  --enable-chunked-prefill \
  --gpu-memory-utilization 0.80 \
  --max-logprobs 0 \
  --port 9042 \
  > vllm_9042.log 2>&1 