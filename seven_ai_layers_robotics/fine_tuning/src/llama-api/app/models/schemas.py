from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RunTrainingRequest(BaseModel):
    gpu_ids: List[int]
    item_name: str


class RunTrainingResponse(BaseModel):
    status: str


class RunTrainingByConfigRequest(BaseModel):
    config_path: str
    gpu_ids: List[int]
    session_name: Optional[str] = None
    log_file: Optional[str] = None
    env: Dict[str, str] = Field(default_factory=dict)


class RunInferenceRequest(BaseModel):
    item_name: str
    gpu_id: int
    api_port: int


class RunInferenceResponse(BaseModel):
    status: str


class MergeLoraRequest(BaseModel):
    item_name: str


class MergeLoraByConfigRequest(BaseModel):
    config_path: str
    session_name: Optional[str] = None
    log_file: Optional[str] = None
    env: Dict[str, str] = Field(default_factory=dict)
    run_async: bool = False


class MergeLoraResponse(BaseModel):
    status: str


class StopSessionRequest(BaseModel):
    item_name: str


class StopSessionByNameRequest(BaseModel):
    session_name: str


class StopSessionResponse(BaseModel):
    status: str


class PrepareTrainingRequest(BaseModel):
    corpora_info: list
    model_template: str
    item_name: str


class PrepareTrainingResponse(BaseModel):
    status: str


class RunningItemCheckRequest(BaseModel):
    item_name: str


class RunningSessionCheckRequest(BaseModel):
    session_name: str


class RunningItemCheckResponse(BaseModel):
    stopped: bool


class UploadConfigResponse(BaseModel):
    status: str
    saved_paths: List[str] = Field(default_factory=list)
