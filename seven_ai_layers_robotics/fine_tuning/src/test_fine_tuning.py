import random
import string
import time
from datetime import datetime
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).parent.resolve()
TODAY_DIR = (
    SCRIPT_DIR
    / "generate"
    / "characterization_function"
    / "daily_corpus"
    / datetime.now().strftime("%Y%m%d")
)
MERGED_JSON_PATH = TODAY_DIR / "merged_sft_pairs.json"

DATE_STR = datetime.now().strftime("%Y%m%d")
RANDOM_SUFFIX = "".join(random.choices(string.ascii_uppercase, k=3))
ITEM_NAME = f"{DATE_STR}_{RANDOM_SUFFIX}"
BASE_URL = ""


if not MERGED_JSON_PATH.exists():
    raise FileNotFoundError(f"Merged file does not exist: {MERGED_JSON_PATH}")

print(f"Will upload file: {MERGED_JSON_PATH}")


def call_prepare_training() -> bool:
    url = f"{BASE_URL}/prepare-training"
    with open(MERGED_JSON_PATH, "rb") as file_handle:
        files = [("corpora_info", ("merged_sft_pairs.json", file_handle, "application/json"))]
        data = {"item_name": ITEM_NAME}
        response = requests.post(url, files=files, data=data, timeout=300)

    if response.status_code == 200:
        print("Prepare training succeeded.")
        return True

    raise RuntimeError(
        f"Prepare training failed: {response.status_code} {response.text}"
    )


def run_training() -> bool:
    url = f"{BASE_URL}/run-training"
    payload = {"item_name": ITEM_NAME, "gpu_ids": [0, 1]}
    response = requests.post(url, json=payload, timeout=60)
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "started":
            print("Training started.")
            return True

    raise RuntimeError(f"Failed to start training: {response.status_code} {response.text}")


def run_inference() -> bool:
    url = f"{BASE_URL}/run-inference"
    payload = {"item_name": ITEM_NAME, "gpu_id": 0, "api_port": 9045}
    response = requests.post(url, json=payload, timeout=60)
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "started":
            print("Inference service started.")
            return True

    print(f"Inference start failed: {response.status_code} {response.text}")
    return False


def check_training_status() -> str:
    url = f"{BASE_URL}/train-finish-check"
    payload = {"item_name": ITEM_NAME}
    response = requests.get(url, json=payload, timeout=30)
    if response.status_code == 200:
        data = response.json()
        return data.get("status", "unknown").lower()
    return "unknown"


def start_and_wait_finetune(
    max_wait_minutes: int = 60,
    check_interval: int = 20,
    launch_training: bool = False,
) -> None:
    print("Step 1: Uploading merged corpus...")
    call_prepare_training()

    if not launch_training:
        return

    print("\nStep 2: Launching training...")
    run_training()

    print(f"\nStep 3: Waiting for training to complete (max: {max_wait_minutes} min)...")
    start_time = time.time()
    max_wait_sec = max_wait_minutes * 60

    while True:
        status = check_training_status()
        elapsed = (time.time() - start_time) / 60
        print(f"[{time.strftime('%H:%M:%S')}] Status: {status.upper()} | Elapsed: {elapsed:.1f} min")

        if status in ("finished", "failed", "error"):
            print(f"\nTraining ended with status: {status.upper()}")
            break

        if time.time() - start_time > max_wait_sec:
            raise TimeoutError(
                f"Training has run for more than {max_wait_minutes} minutes."
            )

        time.sleep(check_interval)

    print("\nStep 4: Launching inference service...")
    run_inference()


if __name__ == "__main__":
    try:
        start_and_wait_finetune(max_wait_minutes=60, launch_training=False)
    except Exception as exc:
        print(f"\nError: {exc}")
