from __future__ import annotations

from _common import build_parser, comma_separated_ints, request_json


def main() -> None:
    parser = build_parser("Call the /run-training-config endpoint.")
    parser.add_argument("--config-path", default="examples/train_lora/qwen3_32b_lora_sft_COT_v8-4.yaml")
    parser.add_argument("--gpu-ids", default="0,1,2,3,4,5,6,7", help="Comma-separated GPU ids.")
    parser.add_argument("--session-name", default="train_qwen3_32b_lora_sft_COT_v8-4")
    parser.add_argument("--log-file", default="qwen3_32b_lora_sft_COT_v8-4.log")
    parser.add_argument("--disable-version-check", dest="disable_version_check", action="store_true", default=True)
    parser.add_argument("--skip-disable-version-check", dest="disable_version_check", action="store_false")
    args = parser.parse_args()

    env = {}
    if args.disable_version_check:
        env["DISABLE_VERSION_CHECK"] = "1"

    payload = {
        "config_path": args.config_path,
        "gpu_ids": comma_separated_ints(args.gpu_ids),
        "session_name": args.session_name,
        "log_file": args.log_file,
        "env": env,
    }
    request_json("POST", f"{args.base_url}/run-training-config", payload)


if __name__ == "__main__":
    main()
