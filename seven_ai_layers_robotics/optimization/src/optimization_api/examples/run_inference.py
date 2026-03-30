import requests


def run_inference():
    url = "http://localhost:13339/run-inference"

    payload = {
        "gpu_ids": [0, 1, 2, 3],
        "api_port": 9046,
        "item_name": "",
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Failed:", response.status_code, response.text)

if __name__ == "__main__":
    run_inference()
