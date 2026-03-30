from typing import List

from pydantic import BaseModel


class RunTrainingRequest(BaseModel):
    gpu_ids: List[int]
    item_name: str


class RunTrainingResponse(BaseModel):
    status: str


class RunInferenceRequest(BaseModel):
    item_name: str
    gpu_id: int
    api_port: int


class RunInferenceResponse(BaseModel):
    status: str


class PrepareTrainingRequest(BaseModel):
    corpora_info: list
    item_name: str


class PrepareTrainingResponse(BaseModel):
    status: str


class RunningItemCheckRequest(BaseModel):
    item_name: str


class RunningItemCheckResponse(BaseModel):
    stopped: bool
