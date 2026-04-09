from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Sequence

from app.config import get_config

CONDA_ENV = get_config().CONDA_ENV
VLLM_ENV = get_config().VLLM_ENV


def _normalize_log_file(log_file: str | None, default_name: str) -> str | None:
    if not log_file:
        return None

    if os.path.isabs(log_file):
        log_path = Path(log_file)
    else:
        base_dir = Path(get_config().LORA_OUTPUT_ROOT or ".")
        log_path = base_dir / log_file

    log_path.parent.mkdir(parents=True, exist_ok=True)
    return str(log_path)


def _tmux_session_exists(session_name: str) -> bool:
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def _quote_cmd(parts: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


def _env_prefix(env: Dict[str, str] | None = None) -> str:
    if not env:
        return ""
    items = [f"{key}={shlex.quote(str(value))}" for key, value in env.items()]
    return "env " + " ".join(items) + " "


def _resolve_conda_executable() -> str:
    cfg = get_config()

    candidates = [
        os.environ.get("CONDA_EXE", "").strip(),
        getattr(cfg, "CONDA_EXE", "").strip() if hasattr(cfg, "CONDA_EXE") else "",
        shutil.which("conda") or "",
        str(Path.home() / "miniconda3" / "bin" / "conda"),
        str(Path.home() / "anaconda3" / "bin" / "conda"),
        "/opt/conda/bin/conda",
        "/usr/local/miniconda3/bin/conda",
        "/usr/local/anaconda3/bin/conda",
    ]

    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    raise FileNotFoundError(
        "Cannot find executable 'conda'. "
        "Please export CONDA_EXE=/absolute/path/to/conda before starting the API service."
    )


def _build_tmux_shell_command(
    *,
    conda_env: str,
    command_args: Sequence[str],
    cwd: str,
    runtime_env: Dict[str, str] | None = None,
    log_file: str | None = None,
) -> str:
    conda_exe = _resolve_conda_executable()

    conda_run_cmd = [
        conda_exe,
        "run",
        "--no-capture-output",
        "-n",
        conda_env,
        *command_args,
    ]

    command_str = f"cd {shlex.quote(cwd)} && {_env_prefix(runtime_env)}{_quote_cmd(conda_run_cmd)}"

    if log_file:
        normalized = _normalize_log_file(log_file, "task.log")
        command_str = f"{command_str} >> {shlex.quote(normalized)} 2>&1"

    return command_str


def run_in_tmux(
    session_name: str,
    conda_env: str,
    command_args: Sequence[str],
    log_file: str | None = None,
    runtime_env: Dict[str, str] | None = None,
    cwd: str | None = None,
    check_existing: bool = True,
    startup_wait_seconds: float = 1.0,
) -> bool:
    if check_existing and _tmux_session_exists(session_name):
        print(f"[INFO] tmux session '{session_name}' already exists. Skipping.")
        return False

    workdir = cwd or get_config().LLAMA_FACTORY_ROOT
    full_command = _build_tmux_shell_command(
        conda_env=conda_env,
        command_args=command_args,
        cwd=workdir,
        runtime_env=runtime_env,
        log_file=log_file,
    )

    tmux_command = ["tmux", "new-session", "-d", "-s", session_name, full_command]
    print(f"[INFO] Starting tmux session '{session_name}' with command: {full_command}")

    result = subprocess.run(
        tmux_command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return False

    time.sleep(startup_wait_seconds)

    if not _tmux_session_exists(session_name):
        print(
            f"[ERROR] tmux session '{session_name}' exited immediately after startup."
        )
        return False

    return True


def run_training(
    session_name: str,
    gpu_list: List[int],
    config_path: str,
    log_file: str | None = None,
    conda_env: str = CONDA_ENV,
    extra_env: Dict[str, str] | None = None,
) -> bool:
    try:
        gpu_list_str = ",".join(str(gpu_id) for gpu_id in gpu_list)
        runtime_env = {
            "CUDA_VISIBLE_DEVICES": gpu_list_str,
            **(extra_env or {}),
        }
        command_args = ["llamafactory-cli", "train", config_path]
        return run_in_tmux(
            session_name=session_name,
            conda_env=conda_env,
            command_args=command_args,
            log_file=log_file,
            runtime_env=runtime_env,
        )
    except Exception as e:
        print(f"Error in run_training: {e}")
        return False


def run_training_by_config(
    session_name: str,
    config_path: str,
    gpu_list: List[int],
    log_file: str | None = None,
    conda_env: str = CONDA_ENV,
    extra_env: Dict[str, str] | None = None,
) -> bool:
    return run_training(
        session_name=session_name,
        gpu_list=gpu_list,
        config_path=config_path,
        log_file=log_file,
        conda_env=conda_env,
        extra_env=extra_env,
    )


def run_inference_vllm(
    session_name: str,
    model_path: str,
    gpu_id: int = 0,
    api_port: int = 8000,
    log_file: str | None = None,
    conda_env: str = VLLM_ENV,
    extra_env: Dict[str, str] | None = None,
    tensor_parallel_size: int = 1,
) -> bool:
    try:
        runtime_env = {
            "CUDA_VISIBLE_DEVICES": str(gpu_id),
            **(extra_env or {}),
        }
        command_args = [
            "python",
            "-m",
            "vllm.entrypoints.openai.api_server",
            "--model",
            model_path,
            "--distributed-executor-backend",
            "mp",
            "--tensor-parallel-size",
            str(tensor_parallel_size),
            "--dtype",
            "auto",
            "--kv-cache-dtype",
            "auto",
            "--max-model-len",
            "8192",
            "--max-num-batched-tokens",
            "16384",
            "--max-num-seqs",
            "32",
            "--enable-chunked-prefill",
            "--gpu-memory-utilization",
            "0.80",
            "--max-logprobs",
            "0",
            "--port",
            str(api_port),
        ]
        return run_in_tmux(
            session_name=session_name,
            conda_env=conda_env,
            command_args=command_args,
            log_file=log_file,
            runtime_env=runtime_env,
        )
    except Exception as e:
        print(f"Error in run_inference_vllm: {e}")
        return False


def run_inference(
    session_name: str,
    config_path: str,
    gpu_id: int = 0,
    api_port: int = 8000,
    log_file: str | None = None,
    conda_env: str = CONDA_ENV,
    extra_env: Dict[str, str] | None = None,
) -> bool:
    try:
        runtime_env = {
            "CUDA_VISIBLE_DEVICES": str(gpu_id),
            "API_PORT": str(api_port),
            **(extra_env or {}),
        }
        command_args = ["llamafactory-cli", "api", config_path]
        return run_in_tmux(
            session_name=session_name,
            conda_env=conda_env,
            command_args=command_args,
            log_file=log_file,
            runtime_env=runtime_env,
        )
    except Exception as e:
        print(f"Error in run_inference: {e}")
        return False


def stop_inference(session_name: str) -> bool:
    try:
        result = subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error in stop_inference: {e}")
        return False


def merge_lora_weights(
    config_path: str,
    conda_env: str = CONDA_ENV,
    extra_env: Dict[str, str] | None = None,
) -> bool:
    try:
        conda_exe = _resolve_conda_executable()
        runtime_env = os.environ.copy()
        if extra_env:
            runtime_env.update({k: str(v) for k, v in extra_env.items()})

        command = [
            conda_exe,
            "run",
            "--no-capture-output",
            "-n",
            conda_env,
            "llamafactory-cli",
            "export",
            config_path,
        ]
        print(f"[DEBUG] Full command to run merge lora weights: {_quote_cmd(command)}")

        result = subprocess.run(
            command,
            cwd=get_config().LLAMA_FACTORY_ROOT,
            env=runtime_env,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error in merge_lora_weights: {e}")
        return False


def merge_lora_weights_async(
    session_name: str,
    config_path: str,
    log_file: str | None = None,
    conda_env: str = CONDA_ENV,
    extra_env: Dict[str, str] | None = None,
) -> bool:
    command_args = ["llamafactory-cli", "export", config_path]
    return run_in_tmux(
        session_name=session_name,
        conda_env=conda_env,
        command_args=command_args,
        log_file=log_file,
        runtime_env=extra_env,
    )


def check_and_cleanup_tmux_session(session_name: str) -> bool:
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        return True

    try:
        output = subprocess.check_output(
            ["tmux", "list-panes", "-t", session_name, "-F", "#{pane_pid}"],
            text=True,
        ).strip()

        if not output:
            subprocess.run(
                ["tmux", "kill-session", "-t", session_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True

        pane_pids = [pid for pid in output.splitlines() if pid.strip()]
        if not pane_pids:
            subprocess.run(
                ["tmux", "kill-session", "-t", session_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True

        alive = False
        for pid in pane_pids:
            ps_result = subprocess.run(
                ["ps", "-p", pid],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if ps_result.returncode == 0:
                alive = True
                break

        if not alive:
            subprocess.run(
                ["tmux", "kill-session", "-t", session_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True

        return False
    except subprocess.CalledProcessError:
        subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
