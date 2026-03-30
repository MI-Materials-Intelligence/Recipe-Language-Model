import requests


def call_prepare_training():
    url = "http://localhost:8000/prepare-training"

    corpora_files = [
        (
            "corpora_info",
            (
                "test_corpora.json",
                open(
                    "/data/sunyao/Workspace/Projects/LLaMA-API/test/test_corpora.json",
                    "rb",
                ),
            ),
        ),
    ]

    data = {
        "item_name": "api_test",
    }

    response = requests.post(url, files=corpora_files, data=data)

    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Failed:", response.status_code, response.text)


if __name__ == "__main__":
    call_prepare_training()
