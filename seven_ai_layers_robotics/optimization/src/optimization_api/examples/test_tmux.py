import subprocess

tmux_command = 'tmux new-session -d -s train_api_test "cd /home/maning/git/LLaMA-Factory && conda run -n llamafactory CUDA_VISIBLE_DEVICES=0,1 llamafactory-cli train examples/train_lora/qwena30_lora_dpo.yml"'

subprocess.run(tmux_command, shell=True, executable="/bin/bash")
