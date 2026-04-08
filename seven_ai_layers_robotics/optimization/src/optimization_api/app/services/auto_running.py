import shlex
import subprocess
from typing import List

from app.config import get_config

TRAINING_COMMAND = (
    "CUDA_VISIBLE_DEVICES={gpu_list} llamafactory-cli train {config_path}"
)

INFERENCE_COMMAND = (
    "CUDA_VISIBLE_DEVICES={gpu_ids} API_PORT={api_port} "
    "llamafactory-cli api {config_path}"
)
CONDA_ENV = get_config().CONDA_ENV


def run_in_tmux(
    session_name: str,
    conda_env: str,
    command: str,
    log_file: str = None,
    check_existing: bool = True,
):
    if check_existing:
        check_cmd = ["tmux", "has-session", "-t", session_name]
        result = subprocess.run(
            check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            print(f"[INFO] tmux session '{session_name}' already exists. Skipping.")
            return

    full_command = (
        f"cd {get_config().LLAMA_FACTORY_ROOT} "
        f"&& conda run -n {shlex.quote(conda_env)} {command}"
    )

    if log_file:
        full_command += f" > {shlex.quote(log_file)} 2>&1"

    tmux_command = (
        f'tmux new-session -d -s {shlex.quote(session_name)} "{full_command}"'
    )

    print(f"[INFO] Starting tmux session '{session_name}' with command: {tmux_command}")

    subprocess.run(tmux_command, shell=True, executable="/bin/bash")

    print(f"[OK] Started tmux session '{session_name}' running: {command}")


def run_training(
    session_name: str,
    gpu_list: List[int],
    config_path: str,
    log_file: str = None,
    conda_env: str = CONDA_ENV,
) -> bool:
    try:
        gpu_list_str = ",".join(str(gpu_id) for gpu_id in gpu_list)
        command = TRAINING_COMMAND.format(
            gpu_list=shlex.quote(gpu_list_str),
            config_path=shlex.quote(config_path),
        )
        run_in_tmux(session_name, conda_env, command, log_file)
        return True
    except Exception as e:
        print(f"Error in run_training: {e}")
        return False


def run_inference(
    session_name: str,
    config_path: str,
    gpu_ids: List[int],
    api_port: int = 8000,
    log_file: str = None,
    conda_env: str = CONDA_ENV,
) -> bool:
    try:
        gpu_list_str = ",".join(str(gpu_id) for gpu_id in gpu_ids)
        command = INFERENCE_COMMAND.format(
            gpu_ids=shlex.quote(gpu_list_str),
            api_port=shlex.quote(str(api_port)),
            config_path=shlex.quote(config_path),
        )
        run_in_tmux(session_name, conda_env, command, log_file)
        return True
    except Exception as e:
        print(f"Error in run_inference: {e}")
        return False


def check_and_cleanup_tmux_session(session_name: str) -> bool:
    check_cmd = ["tmux", "has-session", "-t", session_name]
    result = subprocess.run(
        check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if result.returncode != 0:
        return True

    try:
        pane_pid_cmd = ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_pid}"]
        output = subprocess.check_output(pane_pid_cmd, text=True).strip()
        if not output:
            subprocess.run(["tmux", "kill-session", "-t", session_name])
            return True

        pid = output.strip()
        ps_cmd = ["ps", "-p", pid]
        ps_result = subprocess.run(
            ps_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        if ps_result.returncode != 0:
            subprocess.run(["tmux", "kill-session", "-t", session_name])
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        subprocess.run(["tmux", "kill-session", "-t", session_name])
        return True
