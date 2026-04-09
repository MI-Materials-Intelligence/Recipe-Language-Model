from __future__ import annotations

from pathlib import Path

import requests

from _common import DEMO_CONFIGS_DIR, build_parser, print_response


def _maybe_add_file(files: dict[str, tuple[str, object, str]], field_name: str, file_path: str | None) -> list[object]:
    handles: list[object] = []
    if not file_path:
        return handles
    path = Path(file_path).resolve()
    handle = path.open("rb")
    files[field_name] = (path.name, handle, "application/x-yaml")
    handles.append(handle)
    return handles


def main() -> None:
    parser = build_parser("Upload YAML config files with /upload-config-files.")
    parser.add_argument("--train-config", default=str(DEMO_CONFIGS_DIR / "qwen3_32b_lora_sft_COT_v8-4.yaml"))
    parser.add_argument("--merge-config", default=str(DEMO_CONFIGS_DIR / "qwen3_32b_lora_merge_COT_v8-4.yaml"))
    parser.add_argument("--inference-config", default=None)
    args = parser.parse_args()

    files: dict[str, tuple[str, object, str]] = {}
    opened_handles: list[object] = []
    try:
        opened_handles.extend(_maybe_add_file(files, "train_config", args.train_config))
        opened_handles.extend(_maybe_add_file(files, "merge_config", args.merge_config))
        opened_handles.extend(_maybe_add_file(files, "inference_config", args.inference_config))
        response = requests.post(f"{args.base_url}/upload-config-files", files=files, timeout=300)
        print_response(response)
    finally:
        for handle in opened_handles:
            handle.close()


if __name__ == "__main__":
    main()
