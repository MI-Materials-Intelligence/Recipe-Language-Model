from __future__ import annotations

from functools import lru_cache

from pydantic import BaseModel

try:
    from pydantic import field_validator

    def _strip_validator(*fields):
        return field_validator(*fields, mode="before")

except ImportError:  # pydantic v1
    from pydantic import validator

    def _strip_validator(*fields):
        return validator(*fields, pre=True)


from app.utils import read_yml


class BaseModelConfig(BaseModel):
    model_path: str
    template: str

    @_strip_validator("model_path", "template")
    def _strip_strings(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class AppConfig(BaseModel):
    CONDA_ENV: str = ""
    VLLM_ENV: str = ""
    LLAMA_FACTORY_ROOT: str = ""
    BASE_MODEL_DICT: dict[str, BaseModelConfig] = {}
    TRAIN_META_INFO_ROOT: str = ""
    LORA_OUTPUT_ROOT: str = ""
    MERGED_OUTPUT_ROOT: str = ""
    CORPORA_UPLOAD_ROOT: str = ""

    @_strip_validator(
        "CONDA_ENV",
        "VLLM_ENV",
        "LLAMA_FACTORY_ROOT",
        "TRAIN_META_INFO_ROOT",
        "LORA_OUTPUT_ROOT",
        "MERGED_OUTPUT_ROOT",
        "CORPORA_UPLOAD_ROOT",
    )
    def _strip_top_level_strings(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


@lru_cache()
def get_config() -> AppConfig:
    config_data = read_yml("config.yml")
    return AppConfig(**config_data)
