from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import requests

DEFAULT_BASE_URL = os.getenv("LLAMA_API_BASE_URL", "http://127.0.0.1:8000")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_CORPORA_DIR = PROJECT_ROOT / "demo_corpora"
DEMO_CONFIGS_DIR = PROJECT_ROOT / "demo_configs"
TEST_DIR = PROJECT_ROOT / "test"


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="API base URL, e.g. http://127.0.0.1:8000",
    )
    return parser


def comma_separated_ints(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def print_response(response: requests.Response) -> None:
    print(f"Status code: {response.status_code}")
    try:
        payload = response.json()
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    except ValueError:
        print(response.text)


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    *,
    params: dict[str, Any] | None = None,
) -> requests.Response:
    response = requests.request(
        method=method, url=url, json=payload, params=params, timeout=600
    )
    print_response(response)
    return response
