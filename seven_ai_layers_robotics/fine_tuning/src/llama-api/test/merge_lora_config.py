from __future__ import annotations

from _common import build_parser, request_json


def main() -> None:
    parser = build_parser("Call the /merge-lora-config endpoint.")
    parser.add_argument("--config-path", default="examples/merge_lora/qwen3_32b_lora_merge_COT_v8-4.yaml")
    parser.add_argument("--session-name", default="export_qwen3_32b_lora_merge_COT_v8-4")
    parser.add_argument("--log-file", default="qwen3_32b_lora_merge_COT_v8-4.log")
    parser.add_argument("--run-async", action="store_true")
    parser.add_argument("--disable-version-check", dest="disable_version_check", action="store_true", default=True)
    parser.add_argument("--skip-disable-version-check", dest="disable_version_check", action="store_false")
    args = parser.parse_args()

    env = {}
    if args.disable_version_check:
        env["DISABLE_VERSION_CHECK"] = "1"

    payload = {
        "config_path": args.config_path,
        "session_name": args.session_name,
        "log_file": args.log_file,
        "env": env,
        "run_async": args.run_async,
    }
    request_json("POST", f"{args.base_url}/merge-lora-config", payload)


if __name__ == "__main__":
    main()
