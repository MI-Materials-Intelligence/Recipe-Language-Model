from __future__ import annotations

from _common import build_parser, request_json


def main() -> None:
    parser = build_parser("Call the /session-stop-check endpoint.")
    parser.add_argument("--session-name", default="train_qwen3_32b_lora_sft_COT_v8-4")
    args = parser.parse_args()

    request_json("GET", f"{args.base_url}/session-stop-check", params={"session_name": args.session_name})


if __name__ == "__main__":
    main()
