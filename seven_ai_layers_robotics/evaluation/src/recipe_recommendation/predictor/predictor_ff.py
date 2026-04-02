import math
import re
import json
import warnings
from typing import Literal, Optional


try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except ImportError:
    pass

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", category=UserWarning, message=".*xgboost.*")
warnings.filterwarnings("ignore", message=".*XGBoost.*")

import pandas as pd
import numpy as np
import joblib
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[4]))
from seven_ai_layers_robotics.config import config


pd.set_option('future.no_silent_downcasting', True)


def load_model_data(task_type: str) -> tuple[dict, any, any, any]:
    """Load model configuration and artifacts."""
    # Get model configuration from app.config
    model_config = config.evaluation_predictor.get_model_config(config.root_path)[task_type]

    encoding = json.load(open(model_config["encoding"]))
    col = joblib.load(model_config["col"])
    scaler = joblib.load(model_config["scaler"])
    model = joblib.load(model_config["model"])

    return encoding, col, scaler, model


MAPPINGS, COL_FF, SCALER_FF, MODEL_FF = load_model_data("ff")

# Convert MAPPINGS to lowercase and merge into a single dictionary
STRING_MAPPINGS = json.dumps(MAPPINGS)
STRING_MAPPINGS = STRING_MAPPINGS.lower()
mappings_lower = json.loads(STRING_MAPPINGS)

# Merge list of dicts into a single dict
MERGED = {}
for item in mappings_lower:
    MERGED.update(item)

def get_valid_number(string: str) -> str:
    """Extract valid number from string using regex."""
    reg = re.compile(r'\d*\.\d+|\d+')
    matches = re.search(reg, string)
    if matches:
        return matches.group(0)
    return 0


def get_formula_pvk(string: str) -> str:
    """Extract perovskite formula from string."""
    reg = re.compile(r'[A-Za-z]+\d\.{0,1}\d*')
    matches = re.findall(reg, string)

    # Concatenate all matched results together
    formula_pvk = ''.join(matches)
    return formula_pvk

def get_ff(fp_params_initial: dict, task: str = "None") -> float:
    """
    Predict FF based on recipe parameters.
    
    Args:
        fp_params_initial: Recipe parameters dictionary.
        task: Task identifier (default: "None").
    
    Returns:
        Predicted FF value.
    """
    def pvk_encoding(formula_pvk: str) -> dict:
        formula_pvk = formula_pvk.replace("PbI", "Pb1I").replace("PbBr", "Pb1Br")
        # zqy
        formula_pvk = get_formula_pvk(formula_pvk)

        reg = re.compile(r'([a-zA-Z]+)(\d+\.{0,1}\d*)')
        matches = re.findall(reg, formula_pvk)

        result = {k: float(v) for k, v in matches}

        return result

    # try:
    ## input parsing
    fp_params = {}
    formula_pvk_encoding = pvk_encoding(fp_params_initial["Formula PVK"])
    fp_params['Fa1'] = formula_pvk_encoding.get('Cs', 0)
    fp_params['Fa2'] = formula_pvk_encoding.get('MA', 0)
    fp_params['Fa3'] = formula_pvk_encoding.get('FA', 0)
    fp_params['Fa5'] = formula_pvk_encoding.get('I', 0)
    fp_params['Fa6'] = formula_pvk_encoding.get('Br', 0)

    fp_params['Fa7'] = fp_params_initial.get('Concentration PVK', 1.73)

    for key, value in fp_params_initial.items():
        value = str(value).replace("nan", "") if value is not None else ""

        if "Formula" in key:

            # if "PVK" in key:
            #     continue

            if "PVK" not in key:

                # list to dict

                items = MERGED.get(key.lower(), {})
                if value:
                    formula_encoding = items.get(value.lower(), "")
                    if not formula_encoding:
                        max_value = max(items.values())
                        formula_encoding = max_value + 1
                else:
                    formula_encoding = value

                fp_params[key] = formula_encoding


        elif "Formula" not in key:

            if key == "Concentration PVK":
                continue

            if isinstance(value, str):
                valid_number = get_valid_number(value)
                if valid_number:
                    fp_params[key] = float(valid_number)
                else:
                    fp_params[key] = fp_params_initial.get(key, 0)
            else:
                fp_params[key] = fp_params_initial.get(key, 0)

    # print(f"task {task}: \n\n FP_params: \n\n", fp_params)

    df_fp_params = pd.DataFrame([fp_params])

    x_new = df_fp_params[COL_FF].replace('', np.nan).fillna(0)
    # print(f"task {task}: \n\n FP_params: \n\n", x_new.to_dict(orient='records')[0])

    x_new_std = SCALER_FF.transform(x_new)
    y_new_pred_ff = MODEL_FF.predict(x_new_std)[0]

    return float(y_new_pred_ff)
