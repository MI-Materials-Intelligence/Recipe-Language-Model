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

def load_model_data(task_type: str):
    # Get model configuration from app.config
    model_config = config.evaluation_predictor.get_model_config(config.root_path)[task_type]

    encoding = json.load(open(model_config["encoding"]))
    col = joblib.load(model_config["col"])
    scaler = joblib.load(model_config["scaler"])
    model = joblib.load(model_config["model"])

    return encoding, col, scaler, model

mappings, col_PCE, scaler_PCE, model_PCE = load_model_data("pce")

string_mappings = json.dumps(mappings)
string_mappings = string_mappings.lower()
mappings = json.loads(string_mappings)

merged = {}
for item in mappings:
    merged.update(item)
# print("merged dict", merged)

def get_valid_number(string):
    reg = re.compile(r'\d*\.\d+|\d+')
    matches = re.search(reg, string)
    if matches:
        return matches.group(0)
    return 0

def get_formula_pvk(string):
    reg = re.compile(r'[A-Za-z]+\d\.{0,1}\d*')
    matches = re.findall(reg, string)

    # Concatenate all matched results together
    formula_pvk = ''.join(matches)
    return formula_pvk

def get_PCE(FP_params_initial, task="None"):
    def PVK_encoding(FormulaPVK):
        FormulaPVK = FormulaPVK.replace("PbI", "Pb1I").replace("PbBr", "Pb1Br")
        # zqy
        FormulaPVK = get_formula_pvk(FormulaPVK)

        reg = re.compile(r'([a-zA-Z]+)(\d+\.{0,1}\d*)')
        matches = re.findall(reg, FormulaPVK)

        result = {k: float(v) for k, v in matches}

        return result

    # try:
    ## input parsing
    FP_params = {}
    Formula_PVK_encoding = PVK_encoding(FP_params_initial["Formula PVK"])
    FP_params['Fa1'] = Formula_PVK_encoding.get('Cs', 0)
    FP_params['Fa2'] = Formula_PVK_encoding.get('MA', 0)
    FP_params['Fa3'] = Formula_PVK_encoding.get('FA', 0)
    FP_params['Fa5'] = Formula_PVK_encoding.get('I', 0)
    FP_params['Fa6'] = Formula_PVK_encoding.get('Br', 0)

    FP_params['Fa7'] = FP_params_initial.get('Concentration PVK', 1.73)

    for key, value in FP_params_initial.items():
        value = str(value).replace("nan", "") if value is not None else ""

        if "Formula" in key:

            # if "PVK" in key:
            #     continue

            if "PVK" not in key:

                # list to dict

                items = merged.get(key.lower(), {})
                if value:
                    formula_encoding = items.get(value.lower(), "")
                    if not formula_encoding:
                        max_value = max(items.values())
                        formula_encoding = max_value + 1
                else:
                    formula_encoding = value

                FP_params[key] = formula_encoding


        elif "Formula" not in key:

            if key == "Concentration PVK":
                continue

            if isinstance(value, str):
                valid_number = get_valid_number(value)
                if valid_number:
                    FP_params[key] = float(valid_number)
                else:
                    FP_params[key] = FP_params_initial.get(key, 0)
            else:
                FP_params[key] = FP_params_initial.get(key, 0)

    # print(f"task {task}: \n\n FP_params: \n\n", FP_params)

    df_FP_params = pd.DataFrame([FP_params])

    X_new = df_FP_params[col_PCE].replace('', np.nan).fillna(0)
    # print(f"task {task}: \n\n FP_params: \n\n", X_new.to_dict(orient='records')[0])

    X_new_std = scaler_PCE.transform(X_new)
    y_new_pred_PCE = model_PCE.predict(X_new_std)[0]

    return float(y_new_pred_PCE)
