from __future__ import annotations

from _common import build_parser, request_json


def main() -> None:
    parser = build_parser("Call the /run-inference-vllm endpoint.")
    parser.add_argument("--item-name", default="api_test2")
    parser.add_argument("--gpu-id", type=int, default=4)
    parser.add_argument("--api-port", type=int, default=19042)
    args = parser.parse_args()

    payload = {
        "gpu_id": args.gpu_id,
        "api_port": args.api_port,
        "item_name": args.item_name,
    }
    request_json("POST", f"{args.base_url}/run-inference-vllm", payload)


if __name__ == "__main__":
    main()
