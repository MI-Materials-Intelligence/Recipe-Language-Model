import json
import os
import os.path as osp
import shutil

import yaml


def copy_file(src_file: str, dst_file: str) -> None:
    dst_dir = osp.dirname(dst_file)
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(src_file, dst_file)


def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_yml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yml(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
