import requests


def check_training():
    url = ""
    payload = {
        "item_name": "",
    }

    response = requests.get(url, json=payload)

    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Failed:", response.status_code, response.text)


if __name__ == "__main__":
    check_training()
