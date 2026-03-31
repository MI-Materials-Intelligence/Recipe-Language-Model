import os.path as osp
import os
from typing import List
import shutil
import yaml
from fastapi import UploadFile, File, Form, APIRouter

from app.models.schemas import (
    RunInferenceRequest,
    RunInferenceResponse,
    RunTrainingRequest,
    RunTrainingResponse,
    PrepareTrainingRequest,
    PrepareTrainingResponse,
    RunningItemCheckRequest,
    RunningItemCheckResponse,
)
from app.services.auto_running import (
    run_training,
    run_inference,
    check_and_cleanup_tmux_session,
)
from app.services.prepare_training import prepare_training
from app.config import get_config

router = APIRouter()


@router.post("/run-training", response_model=RunTrainingResponse)
def api_run_training(request: RunTrainingRequest) -> RunTrainingResponse:
    """
    Start a training session in a tmux session.
    Parameters:
        request (RunTrainingRequest): Request object containing GPU IDs and item name.
    Returns:
        RunTrainingResponse: Response object containing training ID and status.
    """

    training_item_name = "train_" + request.item_name
    config_path = f"examples/train_lora/{request.item_name}.yaml"

    log_file = osp.join(
        get_config().LORA_OUTPUT_ROOT, training_item_name, "training.log"
    )

    # Start training in a tmux session
    status = run_training(
        session_name=training_item_name,
        gpu_list=request.gpu_ids,
        config_path=config_path,
        log_file=log_file,
    )

    status_str = "started" if status else "failed"

    return RunTrainingResponse(status=status_str)


@router.post("/run-inference", response_model=RunInferenceResponse)
def api_run_inference(request: RunInferenceRequest) -> RunInferenceResponse:
    """
    Start an inference service session in a tmux session.
    Parameters:
        request (RunInferenceRequest): Request object containing item name, GPU ID, and API port.
    Returns:
        RunInferenceResponse: Response object containing inference ID and status.
    """
    # Start inference in a tmux session
    inference_item_name = "inference_" + request.item_name
    config_path = f"examples/inference/{request.item_name}.yaml"
    log_file = osp.join(
        get_config().LORA_OUTPUT_ROOT, inference_item_name, "inference.log"
    )

    status = run_inference(
        session_name = inference_item_name,
        gpu_ids=request.gpu_ids,
        api_port=request.api_port,
        config_path=config_path,
        log_file=log_file,
    )

    status_str = "started" if status else "failed"
    return RunInferenceResponse(status=status_str)

#  
@router.post("/prepare-training", response_model=PrepareTrainingResponse)
def api_prepare_training(
    item_name: str = Form(...), corpora_info: List[UploadFile] = File(...), base_model_path: str= Form(...), DPO_train_config_template: str = Form(...), inference_config_template: str = Form(...),
) -> PrepareTrainingResponse:
    """
    Prepare training data and configuration.
    Parameters:
        request (PrepareTrainingRequest): Request object containing corpora info and item name.
    Returns:
        PrepareTrainingResponse: Response object indicating preparation status.
    """
    corpora_save_root = osp.join(get_config().CORPORA_UPLOAD_ROOT, item_name)
    os.makedirs(corpora_save_root, exist_ok=True)

    files_data = []
    for file in corpora_info:
        save_path = os.path.join(corpora_save_root, file.filename)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_name = file.filename.split(".")[0]
        files_data.append({"name": file_name, "content": save_path})

    try:
        # Open the file with utf-8 encoding to support special characters
        with open(DPO_train_config_template, 'r', encoding='utf-8') as file:
            # yaml.safe_load() parses the file and returns a Python dictionary
            # Use safe_load to prevent arbitrary code execution from the YAML file
            DPO_train_config_template = yaml.safe_load(file)
        

    except FileNotFoundError:
        print(f"Error: The file '{DPO_train_config_template}' was not found.")
    except yaml.YAMLError as exc:
        print(f"Error while parsing YAML: {exc}")

    try:
       
        with open(inference_config_template, 'r', encoding='utf-8') as file:
            # yaml.safe_load() parses the file and returns a Python dictionary
            # Use safe_load to prevent arbitrary code execution from the YAML file
            inference_config_template = yaml.safe_load(file)
            
    except FileNotFoundError:
        print(f"Error: The file '{inference_config_template}' was not found.")
    except yaml.YAMLError as exc:
        print(f"Error while parsing YAML: {exc}")

    status = prepare_training(
        corpora_info=files_data,
        base_model_path=base_model_path,
        lora_output_dir=get_config().LORA_OUTPUT_ROOT,
        llama_factory_root=get_config().LLAMA_FACTORY_ROOT,
        train_meta_info_root=get_config().TRAIN_META_INFO_ROOT,
        output_name=item_name,
        DPO_train_config_template=DPO_train_config_template,
        inference_config_template=inference_config_template
    )

    status_str = "prepared" if status else "failed"
    return PrepareTrainingResponse(status=status_str)


@router.get("/train-finish-check", response_model=RunningItemCheckResponse)
def api_train_finish_check(
    request: RunningItemCheckRequest,
) -> RunningItemCheckResponse:
    """
    Check if a training session has finished.
    Parameters:
        request (RunningItemCheckRequest): Request object containing item name.
    Returns:
        RunningItemCheckResponse: Response object indicating if the training session has stopped.
    """
    finished = check_and_cleanup_tmux_session(f"train_{request.item_name}")
    return RunningItemCheckResponse(stopped=finished)


@router.get("/inference-stop-check", response_model=RunningItemCheckResponse)
def api_inference_stop_check(
    request: RunningItemCheckRequest,
) -> RunningItemCheckResponse:
    """
    Check if an inference session has stopped.
    Parameters:
        request (RunningItemCheckRequest): Request object containing item name.
    Returns:
        RunningItemCheckResponse: Response object indicating if the inference session has stopped.
    """
    stopped = check_and_cleanup_tmux_session(f"inference_{request.item_name}")
    return RunningItemCheckResponse(stopped=stopped)
