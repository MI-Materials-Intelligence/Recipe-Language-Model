
import time
from typing import ClassVar

import requests

from app.tool.base import BaseTool
# A100 test service
def start_and_wait_finetune():
    """
    Start finetune → Check status every 20 seconds → Return when status is not PENDING
    No input parameters
    """
    BASE_URL = ""
    # 1. Start finetune
    start_url = f"{BASE_URL}/finetune"
    headers = {"Content-Type": "application/json"}

    print("Starting finetune task...")
    r = requests.post(start_url, headers=headers, json={})
    resp = r.json()

    task_id = resp.get("task_id")
    if not task_id:
        raise ValueError(f"Failed to start finetune: {resp}")

    print(f"Finetune started, task_id = {task_id}")

    # 2. Loop check status
    status_url = f"{BASE_URL}/task/{task_id}"

    while True:
        print("Checking status...")

        r = requests.get(status_url, headers=headers)
        data = r.json()

        status = data.get("status", "").upper()
        print(f"Current status: {status}")

        # End if status is not PENDING
        if status != "PENDING":
            return f"Finetune completed: final status = {status}"

        # Wait 20 seconds before checking again
        time.sleep(20)




class Fine_tuning(BaseTool):
    name: str = "fine_tuning"
    description: str = """fine_tuning"""
    has_run: ClassVar[int] = 0
    parameters: dict = {
        "type": "object",
        "properties": {
            "fine_tuning_type": {
                "type": "string",
                "description": " (required) Types of fine_tuning_type",
                "enum": ["1", "2"],
                "default": "1",
            }
        },
        "required": ["fine_tuning_type"],
    }

    async def execute(self, fine_tuning_type: str) -> str:
        # ⭐⭐ Return directly on second and subsequent executions
        if Fine_tuning.has_run == 1:
            return "Finetune task has been executed, skipping this time"

        # First execution
        if fine_tuning_type == "1":
            result = start_and_wait_finetune()
            Fine_tuning.has_run = 1  # ⭐ Mark as executed
            return result

        elif fine_tuning_type == "2":
            return "fine_tuning finished incorrectly"


