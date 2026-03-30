import requests


def run_training():
    url = "http://localhost:8000/run-training"
    payload = {
        "gpu_ids": [0, 1],
        "item_name": "api_test",
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Failed:", response.status_code, response.text)


if __name__ == "__main__":
    run_training()
