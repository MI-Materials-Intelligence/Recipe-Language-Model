import requests
import json
import os
from pathlib import Path
from datetime import datetime
import time
import random
import string

# ========== Configuration ==========
script_dir = Path(__file__).parent.resolve()

# 1. Use today's directory (auto-get)
TODAY_DIR = script_dir/ "generate" / "characterization_function" / "daily_corpus" / datetime.now().strftime("%Y%m%d")
MERGED_JSON_PATH = TODAY_DIR / "merged_sft_pairs.json"

# 2. Training configuration
date_str = datetime.now().strftime("%Y%m%d")
random_suffix = ''.join(random.choices(string.ascii_uppercase, k=3))
ITEM_NAME = f"{date_str}_{random_suffix}"
BASE_URL = ""

# ========== Check if file exists ==========
if not MERGED_JSON_PATH.exists():
    raise FileNotFoundError(f"❌ Merged file does not exist: {MERGED_JSON_PATH}")

print(f"✅ Will upload file: {MERGED_JSON_PATH}")

# ========== 1. Call prepare-training ==========
def call_prepare_training():
    url = f"{BASE_URL}/prepare-training"
    with open(MERGED_JSON_PATH, "rb") as f:
        files = [("corpora_info", ("merged_sft_pairs.json", f, "application/json"))]
        data = {"item_name": ITEM_NAME}
        response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        print("✅ Prepare training succeeded.")
        return True
    else:
        raise RuntimeError(f"❌ Prepare training failed: {response.status_code} {response.text}")

# ========== 2. Start training ==========
def run_training():
    url = f"{BASE_URL}/run-training"
    payload = {"item_name": ITEM_NAME, "gpu_ids": [0, 1]}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "started":
            print("✅ Training started.")
            return True
    raise RuntimeError(f"❌ Failed to start training: {response.status_code} {response.text}")

# ========== 3. Start inference ==========
def run_inference():
    url = f"{BASE_URL}/run-inference"
    payload = {"item_name": ITEM_NAME, "gpu_id": 0, "api_port": 9045}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "started":
            print("✅ Inference service started at ")
            return True
    print(f"⚠️ Inference start failed: {response.status_code} {response.text}")
    return False

# ========== 4. Check training status ==========
def check_training_status():
    url = f"{BASE_URL}/train-finish-check"
    payload = {"item_name": ITEM_NAME}
    response = requests.get(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        # Assume return {"status": "pending" | "finished" | "failed"}
        return data.get("status", "unknown").lower()
    return "unknown"

# ========== 5. Main flow: Upload → Train → Wait → Inference ==========
def start_and_wait_finetune(max_wait_minutes=60, check_interval=20):
    print("🚀 Step 1: Uploading merged corpus...")
    call_prepare_training()

    print("\n🚀 Step 2: Launching training...")
    # run_training()

    print(f"\n⏳ Step 3: Waiting for training to complete (max: {max_wait_minutes} min)...")
    # start_time = time.time()
    # max_wait_sec = max_wait_minutes * 60

    # while True:
    #     status = check_training_status()
    #     elapsed = (time.time() - start_time) / 60
    #     print(f"[{time.strftime('%H:%M:%S')}] Status: {status.upper()} | Elapsed: {elapsed:.1f} min")

    #     if status in ("finished", "failed", "error"):
    #         print(f"\n✅ Training ended with status: {status.upper()}")
    #         break

    #     if time.time() - start_time > max_wait_sec:
    #         print(f"\n⚠️ Timeout: Training has run for more than {max_wait_minutes} minutes.")
    #         try:
    #             if input("Do you want to continue waiting? (y/n): ").strip().lower() in ("n", "no"):
    #                 print("🛑 User cancelled.")
    #                 return
    #         except KeyboardInterrupt:
    #             print("\n🛑 User interrupted.")
    #             return
    #         start_time = time.time() 

    #     time.sleep(check_interval)

    # # Start inference after training ends
    # print("\n🚀 Step 4: Launching inference service...")
    # run_inference()

# ========== Main program ==========
if __name__ == "__main__":
    try:
        start_and_wait_finetune(max_wait_minutes=60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
