from __future__ import annotations

from pathlib import Path

import requests

from _common import DEMO_CORPORA_DIR, build_parser, print_response


def main() -> None:
    parser = build_parser(
        "Call the /prepare-training endpoint with a local demo corpus."
    )
    parser.add_argument("--item-name", default="api_test2")
    parser.add_argument("--model-template", default="qwen3")
    parser.add_argument(
        "--corpus-file",
        default=str(DEMO_CORPORA_DIR / "exp_data_single_var_v7_6.json"),
        help="Path to a local corpus file to upload.",
    )
    args = parser.parse_args()

    url = f"{args.base_url}/prepare-training"
    corpus_path = Path(args.corpus_file).resolve()
    with corpus_path.open("rb") as file_handle:
        response = requests.post(
            url,
            data={"item_name": args.item_name, "model_template": args.model_template},
            files={"corpora_info": (corpus_path.name, file_handle, "application/json")},
            timeout=300,
        )
    print_response(response)


if __name__ == "__main__":
    main()
