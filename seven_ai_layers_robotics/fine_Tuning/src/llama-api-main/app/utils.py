import os
import shutil
import os.path as osp
import json

import yaml


def copy_file(src_file: str, dst_file: str) -> None:
    """
    Copies a file from src_file to dst_file, creating any necessary directories.
    Parameters:
        src_file (str): Path to the source file.
        dst_file (str): Path to the destination file.
    """
    dst_dir = osp.dirname(dst_file)
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy2(src_file, dst_file)


def save_json(data, file_path):
    """Saves a dictionary as a JSON file.

    Args:
        data (dict): The data to save.
        file_path (str): The path to the file where the data should be saved.
    """

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def load_json(file_path):
    """Loads a dictionary from a JSON file.

    Args:
        file_path (str): The path to the JSON file to load.

    Returns:
        dict: The loaded data.
    """
    with open(file_path, "r") as f:
        return json.load(f)


def read_yml(file_path):
    """Reads a YAML file and returns its contents as a dictionary.

    Args:
        file_path (str): The path to the YAML file to read.
    Returns:
        dict: The contents of the YAML file.
    """

    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def save_yml(data, file_path):
    """Saves a dictionary as a YAML file.

    Args:
        data (dict): The data to save.
        file_path (str): The path to the file where the data should be saved.
    """
    with open(file_path, "w") as f:
        yaml.safe_dump(data, f)
