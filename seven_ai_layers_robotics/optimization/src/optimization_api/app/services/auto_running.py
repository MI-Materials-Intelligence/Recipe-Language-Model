import subprocess
import shlex
from typing import List

from app.config import get_config

TRAINING_COMMAND = (
    "CUDA_VISIBLE_DEVICES={gpu_list} llamafactory-cli train {config_path}"
)

INFERENCE_COMMAND = "CUDA_VISIBLE_DEVICES={gpu_ids} API_PORT={api_port} llamafactory-cli api {config_path}"
CONDA_ENV = get_config().CONDA_ENV

def run_in_tmux(
    session_name: str,
    conda_env: str,
    command: str,
    log_file: str = None,
    check_existing: bool = True,
):
    """
    Launch a background command in a new tmux session using a specific Conda environment.

    Parameters:
        session_name (str): Name of the tmux session to create.
        conda_env (str): Name of the Conda environment to activate.
        command (str): The command to run inside the tmux session (e.g., 'python script.py').
        log_file (str, optional): Path to a log file to redirect output. Default is None.
        check_existing (bool): If True, will skip starting if the tmux session already exists.
    """

    # Check if the tmux session already exists
    if check_existing:
        check_cmd = ["tmux", "has-session", "-t", session_name]
        result = subprocess.run(
            check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            print(f"[INFO] tmux session '{session_name}' already exists. Skipping.")
            return

    # Build the full command with conda run
    full_command = f"cd {get_config().LLAMA_FACTORY_ROOT} && conda run -n {shlex.quote(conda_env)} {command}"

    print(f"[DEBUG] Full command to run in tmux: {full_command}")

    # Optionally redirect output to a log file
    # if log_file:
    #     full_command += f" > {shlex.quote(log_file)} 2>&1"

    # Build the tmux command to start a new detached session
    tmux_command = (
        f'tmux new-session -d -s {shlex.quote(session_name)} "{full_command}"'
    )

    print(f"[INFO] Starting tmux session '{session_name}' with command: {tmux_command}")

    # Execute the tmux command
    subprocess.run(tmux_command, shell=True, executable="/bin/bash")

    print(f"[OK] Started tmux session '{session_name}' running: {command}")


def run_training(
    session_name: str,
    gpu_list: List[int],
    config_path: str,
    log_file: str = None,
    conda_env: str = CONDA_ENV,
) -> bool:
    """
    Run a training script in a tmux session with the specified Conda environment and configuration.

    Parameters:
        session_name (str): Name of the tmux session to create.
        gpu_list (List[int]): List of GPU IDs to use for training.
        config_path (str): Path to the configuration file for the training script.
        log_file (str, optional): Path to a log file to redirect output. Default is None.
        conda_env (str): Name of the Conda environment to activate.
    """
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
    """
    Run an inference script in a tmux session with the specified Conda environment and configuration.

    Parameters:
        session_name (str): Name of the tmux session to create.
        config_path (str): Path to the configuration file for the inference script.
        gpu_ids (list): GPU IDs to use for inference.
        api_port (int): API port for the inference server.
        log_file (str, optional): Path to a log file to redirect output. Default is None.
        conda_env (str): Name of the Conda environment to activate.
    """
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
    """
    Check if a tmux session is still running a process.
    If the process has finished, kill the tmux session and return True.
    Otherwise, return False.

    Parameters:
        session_name (str): Name of the tmux session to check.

    Returns:
        bool: True if session was terminated because the process finished, False otherwise.
    """

    # Step 1: Check if the tmux session exists
    check_cmd = ["tmux", "has-session", "-t", session_name]
    result = subprocess.run(
        check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if result.returncode != 0:
        # Session doesn't exist
        return True

    # Step 2: Get the PID of the process running in the pane
    try:
        pane_pid_cmd = ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_pid}"]
        output = subprocess.check_output(pane_pid_cmd, text=True).strip()
        if not output:
            # No process found
            subprocess.run(["tmux", "kill-session", "-t", session_name])
            return True

        # Check if the process is still running
        pid = output.strip()
        ps_cmd = ["ps", "-p", pid]
        ps_result = subprocess.run(
            ps_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        if ps_result.returncode != 0:
            # Process not running -> kill session
            subprocess.run(["tmux", "kill-session", "-t", session_name])
            return True
        else:
            # Process is still running
            return False
    except subprocess.CalledProcessError:
        # Something went wrong, assume session is inactive and kill it
        subprocess.run(["tmux", "kill-session", "-t", session_name])
        return True
