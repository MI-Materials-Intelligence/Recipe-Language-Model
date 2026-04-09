from functools import lru_cache

from pydantic import BaseModel

from app.utils import read_yml


class AppConfig(BaseModel):
    CONDA_ENV: str = ""
    LLAMA_FACTORY_ROOT: str = ""
    BASE_MODEL_ROOT: str = ""
    TRAIN_META_INFO_ROOT: str = ""
    LORA_OUTPUT_ROOT: str = ""
    CORPORA_UPLOAD_ROOT: str = "./corpora"


@lru_cache()
def get_config() -> AppConfig:
    config_data = read_yml("./example_config.yml")
    return AppConfig(**config_data)
