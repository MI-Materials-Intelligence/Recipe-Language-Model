from __future__ import annotations

import json
import os
import os.path as osp
import shutil
from typing import List

from fastapi import APIRouter, File, Form, UploadFile

from app.config import get_config
from app.models.schemas import (
    MergeLoraByConfigRequest,
    MergeLoraRequest,
    MergeLoraResponse,
    PrepareTrainingResponse,
    RunInferenceRequest,
    RunInferenceResponse,
    RunTrainingByConfigRequest,
    RunTrainingRequest,
    RunTrainingResponse,
    RunningItemCheckRequest,
    RunningItemCheckResponse,
    RunningSessionCheckRequest,
    StopSessionByNameRequest,
    StopSessionRequest,
    StopSessionResponse,
    UploadConfigResponse,
)
from app.services.auto_running import (
    check_and_cleanup_tmux_session,
    merge_lora_weights,
    merge_lora_weights_async,
    run_inference,
    run_inference_vllm,
    run_training,
    run_training_by_config,
    stop_inference,
)
from app.services.config_template import AVAILABLE_TEMPLATES, clone_template
from app.services.prepare_training import prepare_training, read_train_meta_info

router = APIRouter()


def _status(ok: bool, success: str = "started", fail: str = "failed") -> str:
    return success if ok else fail


def _save_uploaded_yaml(dst_dir: str, uploaded_file: UploadFile) -> str:
    os.makedirs(dst_dir, exist_ok=True)
    filename = osp.basename(uploaded_file.filename)
    if not filename.endswith((".yaml", ".yml")):
        raise ValueError(f"Unsupported config file: {filename}")
    dst_path = osp.join(dst_dir, filename)
    with open(dst_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)
    return dst_path


@router.post("/run-training", response_model=RunTrainingResponse)
def api_run_training(request: RunTrainingRequest) -> RunTrainingResponse:
    training_item_name = "train_" + request.item_name
    config_path = f"examples/train_lora/{request.item_name}.yaml"
    log_file = osp.join(get_config().LORA_OUTPUT_ROOT, request.item_name, "training.log")
    status = run_training(
        session_name=training_item_name,
        gpu_list=request.gpu_ids,
        config_path=config_path,
        log_file=log_file,
    )
    return RunTrainingResponse(status=_status(status))


@router.post("/run-training-config", response_model=RunTrainingResponse)
def api_run_training_config(request: RunTrainingByConfigRequest) -> RunTrainingResponse:
    session_name = request.session_name or f"train_cfg_{osp.splitext(osp.basename(request.config_path))[0]}"
    log_file = request.log_file or f"{session_name}.log"
    status = run_training_by_config(
        session_name=session_name,
        config_path=request.config_path,
        gpu_list=request.gpu_ids,
        log_file=log_file,
        extra_env=request.env,
    )
    return RunTrainingResponse(status=_status(status))


@router.post("/stop-training", response_model=StopSessionResponse)
def api_stop_training(request: StopSessionRequest) -> StopSessionResponse:
    training_item_name = "train_" + request.item_name
    status = stop_inference(training_item_name)
    return StopSessionResponse(status=_status(status, success="stopped"))


@router.post("/stop-session", response_model=StopSessionResponse)
def api_stop_session(request: StopSessionByNameRequest) -> StopSessionResponse:
    status = stop_inference(request.session_name)
    return StopSessionResponse(status=_status(status, success="stopped"))


@router.post("/run-inference", response_model=RunInferenceResponse)
def api_run_inference(request: RunInferenceRequest) -> RunInferenceResponse:
    inference_item_name = "inference_" + request.item_name
    config_path = f"examples/inference/{request.item_name}.yaml"
    log_file = osp.join(get_config().LORA_OUTPUT_ROOT, request.item_name, "inference.log")
    status = run_inference(
        session_name=inference_item_name,
        gpu_id=request.gpu_id,
        api_port=request.api_port,
        config_path=config_path,
        log_file=log_file,
    )
    return RunInferenceResponse(status=_status(status))


@router.post("/run-inference-vllm", response_model=RunInferenceResponse)
def api_run_inference_vllm(request: RunInferenceRequest) -> RunInferenceResponse:
    inference_item_name = "inference_vllm_" + request.item_name
    model_path = f"{get_config().MERGED_OUTPUT_ROOT}/{request.item_name}"
    log_file = osp.join(get_config().LORA_OUTPUT_ROOT, request.item_name, "inference_vllm.log")
    status = run_inference_vllm(
        session_name=inference_item_name,
        gpu_id=request.gpu_id,
        api_port=request.api_port,
        model_path=model_path,
        log_file=log_file,
    )
    return RunInferenceResponse(status=_status(status))


@router.post("/stop-inference", response_model=StopSessionResponse)
def api_stop_inference(request: StopSessionRequest) -> StopSessionResponse:
    inference_item_name = "inference_" + request.item_name
    status = stop_inference(inference_item_name)
    return StopSessionResponse(status=_status(status, success="stopped"))


@router.post("/stop-inference-vllm", response_model=StopSessionResponse)
def api_stop_inference_vllm(request: StopSessionRequest) -> StopSessionResponse:
    inference_item_name = "inference_vllm_" + request.item_name
    status = stop_inference(inference_item_name)
    return StopSessionResponse(status=_status(status, success="stopped"))


@router.post("/merge-lora", response_model=MergeLoraResponse)
def api_merge_lora(request: MergeLoraRequest) -> MergeLoraResponse:
    try:
        meta = read_train_meta_info(get_config().TRAIN_META_INFO_ROOT, request.item_name)
        merge_config_path = meta.get("merge_config_path")
        if not merge_config_path:
            return MergeLoraResponse(status="failed, merge config not found")
        status = merge_lora_weights(merge_config_path)
        return MergeLoraResponse(status=_status(status, success="merged"))
    except Exception as e:
        return MergeLoraResponse(status=f"failed, {e}")


@router.post("/merge-lora-config", response_model=MergeLoraResponse)
def api_merge_lora_config(request: MergeLoraByConfigRequest) -> MergeLoraResponse:
    try:
        if request.run_async:
            session_name = request.session_name or f"export_{osp.splitext(osp.basename(request.config_path))[0]}"
            log_file = request.log_file or f"{session_name}.log"
            status = merge_lora_weights_async(
                session_name=session_name,
                config_path=request.config_path,
                log_file=log_file,
                extra_env=request.env,
            )
            return MergeLoraResponse(status=_status(status, success="started"))

        status = merge_lora_weights(request.config_path, extra_env=request.env)
        return MergeLoraResponse(status=_status(status, success="merged"))
    except Exception as e:
        return MergeLoraResponse(status=f"failed, {e}")


@router.post("/prepare-training", response_model=PrepareTrainingResponse)
def api_prepare_training(
    item_name: str = Form(...),
    model_template: str = Form(...),
    corpora_info: List[UploadFile] = File(...),
) -> PrepareTrainingResponse:
    if model_template not in AVAILABLE_TEMPLATES:
        return PrepareTrainingResponse(status="failed, invalid template")

    if model_template not in get_config().BASE_MODEL_DICT:
        return PrepareTrainingResponse(status="failed, template not configured in BASE_MODEL_DICT")

    base_model_path = get_config().BASE_MODEL_DICT[model_template].model_path
    sft_train_config_template = clone_template(model_template, "sft_train_template")
    pt_train_config_template = clone_template(model_template, "pt_train_template")
    merge_lora_config_template = clone_template(model_template, "merge_template")
    inference_config_template = clone_template(model_template, "inference_template")

    corpora_save_root = osp.join(get_config().CORPORA_UPLOAD_ROOT, item_name, "raw")
    os.makedirs(corpora_save_root, exist_ok=True)

    files_data = []
    for file in corpora_info:
        save_path = os.path.join(corpora_save_root, file.filename)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_name = os.path.splitext(file.filename)[0]
        files_data.append({"name": file_name, "content": save_path})

    status = prepare_training(
        corpora_info=files_data,
        base_model_path=base_model_path,
        lora_output_dir=get_config().LORA_OUTPUT_ROOT,
        merged_output_dir=get_config().MERGED_OUTPUT_ROOT,
        llama_factory_root=get_config().LLAMA_FACTORY_ROOT,
        train_meta_info_root=get_config().TRAIN_META_INFO_ROOT,
        dataset_workspace_root=osp.join(get_config().CORPORA_UPLOAD_ROOT, "prepared"),
        output_name=item_name,
        sft_train_config_template=sft_train_config_template,
        pt_train_config_template=pt_train_config_template,
        merge_lora_config_template=merge_lora_config_template,
        inference_config_template=inference_config_template,
    )
    return PrepareTrainingResponse(status=_status(status, success="prepared"))


@router.post("/upload-config-files", response_model=UploadConfigResponse)
def api_upload_config_files(
    train_config: UploadFile | None = File(None),
    merge_config: UploadFile | None = File(None),
    inference_config: UploadFile | None = File(None),
) -> UploadConfigResponse:
    saved_paths: List[str] = []
    try:
        if train_config is not None:
            saved_paths.append(_save_uploaded_yaml(osp.join(get_config().LLAMA_FACTORY_ROOT, "examples", "train_lora"), train_config))
        if merge_config is not None:
            saved_paths.append(_save_uploaded_yaml(osp.join(get_config().LLAMA_FACTORY_ROOT, "examples", "merge_lora"), merge_config))
        if inference_config is not None:
            saved_paths.append(_save_uploaded_yaml(osp.join(get_config().LLAMA_FACTORY_ROOT, "examples", "inference"), inference_config))
        return UploadConfigResponse(status="uploaded", saved_paths=saved_paths)
    except Exception as e:
        return UploadConfigResponse(status=f"failed, {e}", saved_paths=saved_paths)


@router.get("/train-finish-check", response_model=RunningItemCheckResponse)
def api_train_finish_check(request: RunningItemCheckRequest) -> RunningItemCheckResponse:
    finished = check_and_cleanup_tmux_session(f"train_{request.item_name}")
    return RunningItemCheckResponse(stopped=finished)


@router.get("/inference-stop-check", response_model=RunningItemCheckResponse)
def api_inference_stop_check(request: RunningItemCheckRequest) -> RunningItemCheckResponse:
    stopped = check_and_cleanup_tmux_session(f"inference_{request.item_name}")
    return RunningItemCheckResponse(stopped=stopped)


@router.get("/session-stop-check", response_model=RunningItemCheckResponse)
def api_session_stop_check(request: RunningSessionCheckRequest) -> RunningItemCheckResponse:
    stopped = check_and_cleanup_tmux_session(request.session_name)
    return RunningItemCheckResponse(stopped=stopped)
