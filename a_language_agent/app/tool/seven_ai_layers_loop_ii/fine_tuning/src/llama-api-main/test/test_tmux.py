import subprocess

tmux_command = 'tmux new-session -d -s train_api_test "cd /data/sunyao/Workspace/Projects/LLaMA-Factory && conda run -n llamafactory2 CUDA_VISIBLE_DEVICES=0,1 llamafactory-cli train examples/train_lora/api_test.yml"'

# run tmux command
subprocess.run(tmux_command, shell=True, executable="/bin/bash")
