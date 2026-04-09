from __future__ import annotations

from _common import build_parser, request_json


def main() -> None:
    parser = build_parser("Call the /inference-stop-check endpoint.")
    parser.add_argument("--item-name", default="api_test")
    args = parser.parse_args()

    request_json("GET", f"{args.base_url}/inference-stop-check", params={"item_name": args.item_name})


if __name__ == "__main__":
    main()
