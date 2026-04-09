from __future__ import annotations

import argparse
import subprocess
import sys
import time


def main() -> None:
    parser = argparse.ArgumentParser(description="Basic local tmux availability test for this project.")
    parser.add_argument("--session-name", default="llama_api_tmux_smoke_test")
    args = parser.parse_args()

    start = subprocess.run(
        ["tmux", "new-session", "-d", "-s", args.session_name, "sleep 10"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if start.returncode != 0:
        print("Failed to create tmux session.")
        sys.exit(1)

    time.sleep(1)
    exists = subprocess.run(
        ["tmux", "has-session", "-t", args.session_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if exists.returncode != 0:
        print("tmux session was not found after creation.")
        sys.exit(1)

    subprocess.run(
        ["tmux", "kill-session", "-t", args.session_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("tmux smoke test passed.")


if __name__ == "__main__":
    main()
