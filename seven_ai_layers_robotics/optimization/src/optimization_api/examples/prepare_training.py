import requests


def call_prepare_training():
    url = ""

    corpora_files = [
        (
            "corpora_info",
            (
                "MIRecipe",
                open(
                    "D:\\pycharmpro\\1027manus\\OpenManus\\app\\tool\\RLM\\Optimization\\exports\\status1_export_20260324_174147.csv",
                    "rb",
                ),
            ),
        ),
    ]

    data = {
        "item_name": "",
        "base_model_path": "/data/opt/LLM_lora_SFT/models/qwen3_32b_v8-4/",
        "DPO_train_config_template": "/data/exp_maning/optimization_API/examples/train_config_example.yaml",
        "inference_config_template": "/data/exp_maning/optimization_API/examples/test_config_example.yaml",
    }

    response = requests.post(url, files=corpora_files, data=data)

    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Failed:", response.status_code, response.text)


if __name__ == "__main__":
    call_prepare_training()
