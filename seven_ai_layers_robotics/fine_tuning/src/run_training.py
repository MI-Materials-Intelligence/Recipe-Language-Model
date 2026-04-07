from __future__ import annotations

from _common import build_parser, comma_separated_ints, request_json


def main() -> None:
    parser = build_parser("Call the /run-training endpoint.")
    parser.add_argument("--item-name", default="api_test2")
    parser.add_argument("--gpu-ids", default="4,5", help="Comma-separated GPU ids.")
    args = parser.parse_args()

    payload = {
        "gpu_ids": comma_separated_ints(args.gpu_ids),
        "item_name": args.item_name,
    }
    request_json("POST", f"{args.base_url}/run-training", payload)


if __name__ == "__main__":
    main()
