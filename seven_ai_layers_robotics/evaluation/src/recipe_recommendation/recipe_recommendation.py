import os
# print(os.path.dirname(__file__))

from pathlib import Path
path = Path(__file__).resolve().parents[2]
os.chdir(path)
# print(os.getcwd())


from flask import request, jsonify, Blueprint

import re
import json
import pandas as pd
import numpy as np

from recipe_recommendation.predictor.main_predictor import get_prediction
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from seven_ai_layers_robotics.config import config



recipe_integrity_bp = Blueprint('recipe_integrity', __name__)
formula_rationality_bp = Blueprint('formula_rationality', __name__)
parameter_rationality_bp = Blueprint('parameter_rationality', __name__)
performance_rationality_bp = Blueprint('performance_rationality', __name__)
recipe_recommendation_bp = Blueprint('recipe_recommendation', __name__)
experimental_validation_bp = Blueprint('experimental_validation', __name__)
recipe_bp = Blueprint('recipe', __name__)

# ignore the warning in X_new = df_FP_params[col_PCE].replace('', np.nan).fillna(0)
pd.set_option("future.no_silent_downcasting", True)

COMPOUND_MAPPING = json.load(open(config.get_evaluation_data_path('data/compound_mapping.json'), 'r', encoding='utf-8'))

def get_compound_mapping_invert(compound_mapping: dict) -> dict:
    compound_mapping_invert = {}
    for k, v in compound_mapping.items():
        v_ = v.split(" (")[1][:-1].lower()
        compound_mapping_invert[f"{v_}"] = k.lower()

    return compound_mapping_invert


COMPOUND_MAPPING_INVERT = get_compound_mapping_invert(COMPOUND_MAPPING)


def get_valid_number(string: str) -> str:
    reg = re.compile(r'\d*\.\d+|\d+')
    matches = re.search(reg, string)
    if matches:
        return matches.group(0)
    return 0


# zqy
def get_formula_pvk(string: str) -> str:
    reg = re.compile(r'[A-Za-z]+\d\.{0,1}\d*')
    matches = re.findall(reg, string)

    formula_pvk = ''.join(matches)
    return formula_pvk

def clean_formula(formula: str) -> str:
    if not isinstance(formula, str):
        return formula

    # Use regular expression to match the first pair of parentheses and the content before them
    match = re.match(r'^([^(]+?)\s*\([^)]*\)', formula)
    if match:
        formula_cleaned = match.group(1).strip()
    else:
        formula_cleaned = formula

    # formula_cleaned.replace("BSP", "PSP").replace("bsp", "psp")

    # print(f"Original formula: {formula} -> After cleaning: {formula_cleaned}")
    return formula_cleaned


def deal_response_formula(response: str) -> str:
    json_start = response.rfind("{")
    json_end = response.rfind("}")
    json_content = response[json_start:json_end + 1]

    json_content = json_content.replace("\n", " ")
    # if json_start == -1 or json_end == -1:
    #     # print("\n\n\n ⚠ Warning: Missing JSON content")
    #     format_match=0

    json_response = json.loads(json_content)

    for key, value in json_response.items():
        if "formula" in key.lower():
            json_response[key] = clean_formula(value)

    return json.dumps(json_response)

REQUIRED_FIELDS = ["Formula PVK", "Concentration PVK", "Formula Additive 1", "Concentration Additive 1",
                   "Formula Additive 2", "Concentration Additive 2", "Formula Additive 3",
                   "Concentration Additive 3", "Formula SAM 1", "Concentration SAM 1", "Formula SAM 2",
                   "Concentration SAM 2", "Formula SAM 3", "Concentration SAM 3", "Spin Coating Speed SAM",
                   "Spin Coating Time SAM", "Annealed Temperature SAM", "Annealed Time SAM",
                   "Spin Coating Speed PVK 1", "Spin Coating Time PVK 1", "Spin Coating Speed PVK 2",
                   "Spin Coating Time PVK 2", "Antisolvent Dropping Timing", "Antisolvent Volume",
                   "Annealed Temperature PVK", "Annealed Time PVK", "Formula Passivator 1",
                   "Concentration Passivator 1", "Formula Passivator 2", "Concentration Passivator 2",
                   "Formula Passivator 3", "Concentration Passivator 3", "Formula Passivator 4",
                   "Concentration Passivator 4", "Spin Coating Speed Passivator",
                   "Spin Coating Time Passivator",
                   "Passivator Dropping Timing", "Passivator Volume", "Annealed Temperature Passivator",
                   "Annealed Time Passivator"]

PVK_FIELDS = ["Formula PVK", "Concentration PVK",
              "Spin Coating Speed PVK 1", "Spin Coating Time PVK 1",
              "Spin Coating Speed PVK 2", "Spin Coating Time PVK 2",
              "Antisolvent Dropping Timing", "Antisolvent Volume",
              "Annealed Temperature PVK", "Annealed Time PVK"]

PVK_P_FIELDS = ["Spin Coating Speed PVK 1", "Spin Coating Time PVK 1",
              "Spin Coating Speed PVK 2", "Spin Coating Time PVK 2",
              "Antisolvent Dropping Timing", "Antisolvent Volume",
              "Annealed Temperature PVK", "Annealed Time PVK"]

SAM_P_FIELDS = ["Spin Coating Speed SAM", "Spin Coating Time SAM",
                "Annealed Temperature SAM", "Annealed Time SAM"]

PASSIVATOR_P_FIELDS = ["Spin Coating Speed Passivator", "Spin Coating Time Passivator",
                        "Passivator Dropping Timing", "Passivator Volume",
                        "Annealed Temperature Passivator", "Annealed Time Passivator"]

INVALID_STRINGS = ["none", "nan", "null", "n/a", "na", "0", "", "0.0"]
INORGANIC = ["NiOx", "C60", "Ag", "BCP"]

def get_fp_str(response: dict, control: dict) -> tuple[dict, dict]:

    """
    Convert all values in JSON format to uniform strings
    """

    try:
        if isinstance(response, str):
            response = json.loads(response)
        if isinstance(control, str):
            control = json.loads(control)

        response = json.loads(deal_response_formula(json.dumps(response)))

        for key, value in response.items():
            response[key] = str(value)

        for key, value in control.items():
            control[key] = str(value)

        return response, control

    except Exception as e:
        print(f"The input may be neither JSON nor a JSON string ({e})")
        return {}, {}

def get_valid_number_str(string: str) -> str:
    """Extract valid digits"""
    if not isinstance(string, str):
        return ""

    string = string.strip()
    # Check if it is empty or an invalid value
    if not string or string.lower() in INVALID_STRINGS:
        return ""

    # Extract digits
    numbers = re.findall(r'[-+]?\d*\.?\d+', string)
    if numbers:
        try:
            return numbers[0]
        except (ValueError, IndexError):
            return ""
    return ""


def get_param(data):

    optimize = data.get("optimized_FP", {}).copy()
    control = data.get("control_FP", {}).copy()

    if optimize != {}:
        # Unify key name modification
        keys_to_update = {}
        for key in list(optimize.keys()):
            if " (μL)" in key:
                new_key = key.replace(" (μL)", "")
                keys_to_update[new_key] = optimize[key]
        # Execute key name update
        optimize.update(keys_to_update)

        for key in keys_to_update:
            old_key = key + " (μL)"
            optimize.pop(old_key, None)


        for field in REQUIRED_FIELDS:
            if field not in optimize:
                optimize[field] = ""

    if control != {}:
        # Unify key name modification
        keys_to_update = {}
        for key in list(control.keys()):
            if " (μL)" in key:
                new_key = key.replace(" (μL)", "")
                keys_to_update[new_key] = control[key]
        # Execute key name update
        control.update(keys_to_update)

        for key in keys_to_update:
            old_key = key + " (μL)"
            control.pop(old_key, None)


        for field in REQUIRED_FIELDS:
            if field not in control:
                control[field] = ""

    return optimize, control

def get_difficulty(control: dict) -> float:
    """Used to calculate the difficulty coefficient for different experimental stages"""

    ctrl = control.copy()
    for field in ["PCE", "Voc", "Jsc", "FF"]:
        ctrl.pop(field, None)

    SAM_field = [field for field in REQUIRED_FIELDS if "SAM" in field]
    Additive_field = [field for field in REQUIRED_FIELDS if "Additive" in field]
    Passivator_field = [field for field in REQUIRED_FIELDS if "Passivator" in field]

    difficulty = 0.5
    for field in SAM_field+Additive_field:
        if str(ctrl[field]) not in INVALID_STRINGS:
            difficulty = 0.7
            break

    for field in Passivator_field:
        if str(ctrl[field]) not in INVALID_STRINGS:
            difficulty = 1
            break

    return difficulty

def has_performance(optimized: dict) -> bool:
    """Used to determine whether experimental values are passed into the optimization formula"""

    PCE = optimized.get("PCE", "")
    if PCE in INVALID_STRINGS:
        return False

    return True


# 1
@recipe_integrity_bp.route('/RECIPE/recipe_integrity', methods=['POST'])
def recipe_integrity():
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_recipe_integrity(response, control)

    return jsonify(result)

def calculate_recipe_integrity(response: dict, control: dict) -> dict:
    '''
        Calculate indicator 'recipe integrity' score in evaluation layer.

        Args:
            response: Optimized recipe.
            control: Control recipe.

        Returns:
            Indicator 'recipe integrity' score.
    '''


    """
        Completeness Evaluation: Map the 0-5 score standard to a decimal between 0-1

        Rules:
        - All PVK_FIELDS fields are checked, and count each missing field
        - PASSIVATOR_P_FIELDS are only checked when Formula Passivator 1 exists
        - Fuzzy judgment: If a number can be extracted, it is not considered fuzzy; only when there is content but no number can be extracted is it considered fuzzy
    """

    def has_structural_contradictions(response: dict) -> bool:
        """
        Check for structural contradictions
        Example: Concentration value exists but formula field is empty
        """

        formula_conc_pairs = [
            ("Formula PVK", "Concentration PVK"),
            ("Formula Additive 1", "Concentration Additive 1"),
            ("Formula Additive 2", "Concentration Additive 2"),
            ("Formula Additive 3", "Concentration Additive 3"),
            ("Formula SAM 1", "Concentration SAM 1"),
            ("Formula SAM 2", "Concentration SAM 2"),
            ("Formula SAM 3", "Concentration SAM 3"),
            ("Formula Passivator 1", "Concentration Passivator 1"),
            ("Formula Passivator 2", "Concentration Passivator 2"),
            ("Formula Passivator 3", "Concentration Passivator 3"),
            ("Formula Passivator 4", "Concentration Passivator 4"),
        ]

        for formula_field, conc_field in formula_conc_pairs:
            formula = str(response.get(formula_field, "")).strip()
            concentration = str(response.get(conc_field, "")).strip()

            # Concentration value exists but formula is empty
            if concentration and concentration.lower() not in INVALID_STRINGS:
                if not formula or formula.lower() in INVALID_STRINGS:
                    return True

        return False

    reason = "initial score"
    score = None
    result = {
        "score": score,
        "reason": reason
    }

    try:

        response, control = get_param({
            "control_FP": control,
            "optimized_FP": response
        })

        response, control = get_fp_str(response, control)

        if not (response and control):
            reason = "No valid optimized_FP and control_FP were found."
            print(reason)
            result["reason"] = reason
            return result

        indicator = "recipe_integrity"

        # 1. Check for structural contradictions
        if has_structural_contradictions(response):
            score = 0
            reason = f"{indicator}({score} 分): A concentration value exists, but the corresponding formulation field is empty."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # Count missing and fuzzy parameters
        missing_count = 0
        ambiguous_count = 0

        # 2. Check PVK_FIELDS (all)
        for field in PVK_FIELDS:
            value = str(response.get(field, "")).strip()

            # Check if missing
            if not value or value.lower() in INVALID_STRINGS:
                missing_count += 1
            else:
                # Check numeric fields (excluding formula fields)
                if field != "Formula PVK":
                    if not any(char.isdigit() for char in value) and value.lower() not in INVALID_STRINGS:
                        ambiguous_count += 1

        # 3. Check PASSIVATOR_P_FIELDS (only when Formula Passivator 1 exists)
        formula_passivator_1 = str(response.get("Formula Passivator 1", "")).strip()

        if formula_passivator_1 and formula_passivator_1.lower() not in INVALID_STRINGS:
            for field in PASSIVATOR_P_FIELDS:
                value = str(response.get(field, "")).strip()

                if not value or value.lower() in INVALID_STRINGS:
                    missing_count += 1
                else:
                    if not any(char.isdigit() for char in value) and value.lower() not in INVALID_STRINGS:
                        ambiguous_count += 1

        # 4. Score based on the number of missing and fuzzy items
        # 0
        if missing_count >= 8:
            score = 0
            reason = f"{indicator}({score} points): A large number of PVK parameters and passivation process parameters are missing (>8) when a passivation agent is present."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # 1
        if missing_count >= 6:
            score = 0.2
            reason = f"{indicator}({score} points): Most PVK parameters and passivation process parameters (when a passivation agent is present) are missing (6–7)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # 2
        if missing_count >= 3:
            score = 0.4
            reason = f"{indicator}({score} points): Multiple PVK parameters and passivation process parameters (when a passivation agent is present) are missing (3–5)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # 3
        if missing_count >= 1:
            score = 0.6
            reason = f"{indicator}({score} points): A few PVK parameters and passivation process parameters (when a passivation agent is present) are missing (1–2)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # 4
        if ambiguous_count >= 1:
            score = 0.8
            reason = f"{indicator}({score} points): PVK parameters and passivation process parameters (when a passivation agent is present) are mostly complete (e.g., parameters like 'after ...' where specific numeric values cannot be extracted)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # 5
        score = 1
        reason = f"{indicator}({score} points): PVK parameters and passivation process parameters (when a passivation agent is present) are complete and contain extractable numeric values."  # PVK参数+钝化剂工艺参数（当钝化剂存在时）完整且能提取到具体的数值
        print(reason)
        result["score"] = score
        result["reason"] = reason

        difficulty = get_difficulty(control)
        result["score"] = result["score"]*difficulty

        return result

    except Exception as e:
        print(e)
        score = None
        reason = f"An error occurred ({e})."
        result["score"] = score
        result["reason"] = reason
        return result

# 2
@formula_rationality_bp.route('/RECIPE/formula_rationality', methods=['POST'])
def formula_rationality():
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_formula_rationality(response, control)

    return jsonify(result)

def calculate_formula_rationality(response: dict, control: dict) -> dict:
    '''
        Calculate indicator 'formula rationality' score in evaluation layer.

        Args:
            response: Optimized recipe.
            control: Control recipe.

        Returns:
            Indicator 'formula rationality' score.
    '''


    """
    • Whether the names of perovskite, additive, SAM, and passivator are reasonable
    • Whether the concentration ratios of perovskite, additive, SAM, and passivator are within a reasonable range
    """

    try:

        response, control = get_param({
            "control_FP": control,
            "optimized_FP": response
        })

        response, control = get_fp_str(response, control)

        result = {
            "reason": "initial score",
            "score": 1.0,
        }

        if not (response and control):
            reason = "No valid optimized_FP and control_FP were found."
            print(reason)
            result["score"] = None
            result["reason"] = reason
            return result

        print("Check control: ", control)
        print("Check optimized: ", response)

        indicator = "formula_rationality"

        # Concentration range (based on scoring criteria)
        ranges = {
            "Concentration PVK": (1.0, 1.8),  # 1.0-1.8 M
            "Concentration Additive": (1, 30),  # 1-30 mg/mL
            "Concentration SAM": (0.1, 1.0),  # 0.1-1.0 mg/mL
            "Concentration Passivator": (0.1, 5.0)  # 0.1-5.0 mg/mL
        }

        for key, value in response.items():
            value = str(value)

            if value in INORGANIC:  # Check inorganic compound
                result["score"] = 0.2
                result["reason"] = "The compound is invalid or may contain some inorganic compounds."

            # if "Formula" in key and "PVK" not in key:
            #     if value.strip().lower() not in INVALID_STRINGS:
            #         material_dict = merged[key.strip().lower()]
            #
            #         if value.strip().lower() not in material_dict.keys():
            #             pass

        # Check all concentration fields
        for field in REQUIRED_FIELDS:
            if "Concentration" in field:

                if response.get(field, "").lower() in INVALID_STRINGS:
                    continue

                # Directly extract concentration values
                conc_value = get_valid_number_str(response.get(field, ""))

                if conc_value == "":
                    score = 0
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains values that cannot be parsed."
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result
                else:
                    conc_value = float(conc_value)

                # Determine the range
                if "PVK" in field:
                    min_val, max_val = ranges["Concentration PVK"]
                elif "Additive" in field:
                    min_val, max_val = ranges["Concentration Additive"]
                elif "SAM" in field:
                    min_val, max_val = ranges["Concentration SAM"]
                elif "Passivator" in field:
                    min_val, max_val = ranges["Concentration Passivator"]
                else:
                    continue

                # Check if it is within the range
                if min_val <= conc_value <= max_val:
                    continue

                # Calculate the degree of deviation
                if conc_value < min_val:
                    deviation = (min_val - conc_value) / min_val
                else:  # conc_value > max_val
                    deviation = (conc_value - max_val) / max_val

                # Update the worst score based on the degree of deviation
                if conc_value / max_val >= 100 or conc_value / min_val <= 0.001:
                    score = min(result["score"], 0)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains fundamentally invalid concentration values [conc_value/max_val ≥ 100 or conc_value/min_val ≤ 0.001]."  # {indicator}({score} 分): {field}={conc_value} 有浓度值根本上无效【conc_value/max_val >= 100 or conc_value/min_val <= 0.001】
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result
                if conc_value / max_val >= 10 or conc_value / min_val <= 0.01:
                    score = min(result["score"], 0.2)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains significantly incorrect concentration values [conc_value/max_val ≥ 10 or conc_value/min_val ≤ 0.01]."  # {indicator}({score} 分): {field}={conc_value} 有浓度值显著错误【conc_value/max_val >= 10 or conc_value/min_val <= 0.01】
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result
                if conc_value / max_val >= 1 or conc_value / min_val <= 0.1:
                    score = min(result["score"], 0.4)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains clearly abnormal concentration values (or irrelevant compounds may have been extracted) [conc_value/max_val ≥ 1 or conc_value/min_val ≤ 0.1]."  # {indicator}({score} 分): {field}={conc_value} 有浓度值存在明显异常值（或提取了没用的化合物）【conc_value/max_val >= 1 or conc_value/min_val <= 0.1】
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result
                if deviation > 0.05:
                    score = min(result["score"], 0.6)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains concentration values that deviate from the standard range (or inorganic compounds may have been extracted) [deviation > 0.05]."  # {indicator}({score} 分): {field}={conc_value} 有浓度值偏离标准范围（或提取了无机化合物）【deviation > 0.05】
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result
                else:
                    score = min(result["score"], 0.8)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains concentration values with slight deviation (or inorganic compounds may have been extracted) [deviation ≤ 0.05]."  # {indicator}({score} 分): {field}={conc_value} 有浓度值存在轻微偏差（或提取了无机化合物）【deviation <= 0.05】
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result

        if result["score"] == 1:
            score = result["score"]
            reason = f"{indicator} ({score} points): All concentration values are extractable and fall within the domain knowledge ranges (e.g., precursors 1.0–1.8 M; additives 1–30 mg/mL; SAMs 0.1–1 mg/mL; passivation agents 0.1–5 mg/mL)."  # {indicator}({score} 分): 所有浓度值可提取且均在领域知识范围内（例如：前驱体1.0–1.8 M；添加剂1–30 mg/mL；SAMs 0.1–1 mg/mL；钝化剂0.1–5 mg/mL）
            result["reason"] = reason

        difficulty = get_difficulty(control)
        result["score"] = result["score"] * difficulty

        return result

    except Exception as e:
        print(e)
        score = None
        reason = f"An error occurred ({e})."
        result["score"] = score
        result["reason"] = reason
        return result

# 3
@parameter_rationality_bp.route('/RECIPE/parameter_rationality', methods=['POST'])
def parameter_rationality():
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_parameter_rationality(response, control)

    return jsonify(result)

def calculate_parameter_rationality(response: dict, control: dict) -> dict:
    '''
        Calculate indicator 'parameter rationality' score in evaluation layer.

        Args:
            response: Optimized recipe.
            control: Control recipe.

        Returns:
            Indicator 'parameter rationality' score.
    '''

    """
        Process parameter reliability evaluation
        Use logic similar to formula_rationality
    """

    try:

        response, control = get_param({
            "control_FP": control,
            "optimized_FP": response
        })

        response, control = get_fp_str(response, control)

        result = {
            "reason": "initial score",
            "score": 1.0,
        }

        if not (response and control):
            reason = "No valid optimized_FP and control_FP were found."
            print(reason)
            result["score"] = None
            result["reason"] = reason
            return result

        indicator = "parameter_rationality"

        # Define the reasonable range of parameters
        parameter_ranges = {
            # Spin coating parameters
            "Spin Coating Speed SAM": (2000, 5000),  # rpm
            "Spin Coating Time SAM": (20, 30),  # s
            "Spin Coating Speed PVK 1": (500, 2200),  # rpm
            "Spin Coating Time PVK 1": (5, 30),  # s
            "Spin Coating Speed PVK 2": (3500, 7000),  # rpm
            "Spin Coating Time PVK 2": (21, 50),  # s
            "Spin Coating Speed Passivator": (2000, 6000),  # rpm
            "Spin Coating Time Passivator": (15, 40),  # s

            # Annealing parameters
            "Annealed Temperature SAM": (90, 120),  # °C
            "Annealed Temperature PVK": (90, 120),  # °C
            "Annealed Temperature Passivator": (80, 120),  # °C

            # Time parameters
            "Annealed Time SAM": (5, 20),  # min
            "Annealed Time PVK": (5, 60),  # min
            "Annealed Time Passivator": (2, 15),  # min

            # Antisolvent parameters
            "Antisolvent Dropping Timing": (2, 20),  # s
            "Antisolvent Volume": (80, 300),  # µL
            "Passivator Dropping Timing": (5, 18),  # s
            "Passivator Volume": (60, 200)  # µL
        }

        # Check each parameter
        for field, (min_val, max_val) in parameter_ranges.items():
            # Get field value
            field_value = response.get(field, "")
            if not isinstance(field_value, str):
                field_value = str(field_value)

            # Skip if empty
            if field_value.lower() in INVALID_STRINGS:
                continue

            # Extract digits
            value_str = get_valid_number_str(field_value)

            if value_str == "":
                score = 0
                reason = f"{indicator} ({score} points): The value of {field} cannot be parsed."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result

            value = float(value_str)

            # Check if it is within the range
            if min_val <= value <= max_val:
                continue

            # Calculate the degree of deviation
            if value < min_val:
                deviation = (min_val - value) / min_val
            else:  # value > max_val
                deviation = (value - max_val) / max_val

            # Use scoring logic similar to formula_rationality
            # But the parameter ranges may be more relaxed

            if deviation > 0.50:
                score = min(result["score"], 0)
                reason = f"{indicator} ({score} points): {field} = {value} is fundamentally invalid [deviation > 0.50]."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result
            elif deviation > 0.30:
                score = min(result["score"], 0.2)
                reason = f"{indicator} ({score} points): {field} = {value} is significantly incorrect [deviation > 0.30]."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result
            elif deviation > 0.20:
                score = min(result["score"], 0.4)
                reason = f"{indicator} ({score} points): {field} = {value} is clearly abnormal [deviation > 0.20]."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result
            elif deviation > 0.10:
                score = min(result["score"], 0.6)
                reason = f"{indicator} ({score} points): {field} = {value} deviates from the standard range [deviation > 0.10]."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result
            elif deviation > 0.05:
                score = min(result["score"], 0.8)
                reason = f"{indicator} ({score} points): {field} = {value} shows a slight deviation [deviation > 0.05]."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result
            else:
                score = min(result["score"], 0.9)
                reason = f"{indicator} ({score} points): {field} = {value} shows a minor deviation [deviation > 0]."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result

        # If all checks pass
        if result["score"] == 1:
            score = result["score"]
            reason = f"{indicator} ({score} points): All parameters fall within reasonable ranges."
            print(reason)
            result["reason"] = reason

        difficulty = get_difficulty(control)
        result["score"] = result["score"] * difficulty

        return result

    except Exception as e:
        print(e)
        score = None
        reason = f"An error occurred ({e})."
        print(reason)
        result["score"] = score
        result["reason"] = reason
        return result

# 4
@performance_rationality_bp.route('/RECIPE/performance_rationality', methods=['POST'])
def performance_rationality():
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_performance_rationality(response, control)

    return jsonify(result)

def calculate_performance_rationality(response: dict, control: dict) -> dict:
    '''
        Calculate indicator 'performance rationality' score in evaluation layer.

        Args:
            response: Optimized recipe.
            control: Control recipe.

        Returns:
            Indicator 'performance rationality' score.
    '''

    def safe_float(value_str):
        """Safely convert to float"""
        if not value_str or value_str == "":
            return None
        try:
            return float(value_str)
        except (ValueError, TypeError):
            return None

    try:

        response, control = get_param({
            "control_FP": control,
            "optimized_FP": response
        })

        response, control = get_fp_str(response, control)

        result = {
            "reason": "initial score",
            "score": 0.6,
        }

        default_score = result["score"]

        if not (response and control):
            reason = "No valid optimized_FP and control_FP were found."
            print(reason)
            result["score"] = None
            result["reason"] = reason
            return result

        indicator = "performance_rationality"

        # Extract optimized group performance
        opt_pce = safe_float(get_valid_number_str(response.get("PCE", "")))
        opt_ff = safe_float(get_valid_number_str(response.get("FF", "")))
        opt_jsc = safe_float(get_valid_number_str(response.get("Jsc", "")))
        opt_voc = safe_float(get_valid_number_str(response.get("Voc", "")))

        # Extract control group performance
        ctrl_pce = safe_float(get_valid_number_str(control.get("PCE", "")))
        ctrl_ff = safe_float(get_valid_number_str(control.get("FF", "")))
        ctrl_jsc = safe_float(get_valid_number_str(control.get("Jsc", "")))
        ctrl_voc = safe_float(get_valid_number_str(control.get("Voc", "")))

        # Check whether the optimized group data is complete
        if any(v is None for v in [opt_pce, opt_ff, opt_jsc, opt_voc]):
            score = default_score
            reason = f"{indicator} ({score} points): The performance data of the optimized group is incomplete."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # Check whether the control group data is complete
        if any(v is None for v in [ctrl_pce, ctrl_ff, ctrl_jsc, ctrl_voc]):
            score = default_score
            reason = f"{indicator} ({score} points): The performance data of the control group is incomplete."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # ============ Zero-point check: most severe issue ============
        # 1. Exceeds physical limits
        if opt_pce > 30.0:
            score = 0
            reason = f"{indicator} ({score} points): pce = {opt_pce}% exceeds the physical limit (>30%)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # 2. optimized is worse than the control
        if opt_pce <= ctrl_pce:
            score = 0
            reason = f"{indicator} ({score} points): The optimized group pce ({opt_pce}%) ≤ the control group pce ({ctrl_pce}%)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # ============ Check the reasonableness of FF, Voc, and Jsc ============
        # Define the reasonable range
        pce_reasonable = 1.0 <= opt_pce <= 27.0
        voc_reasonable = 0.5 <= opt_voc <= 1.22
        ff_reasonable = 60 <= opt_ff <= 85
        jsc_reasonable = 15 <= opt_jsc <= 26

        reasonable_ranges = [pce_reasonable, voc_reasonable, ff_reasonable, jsc_reasonable]

        # ============ One-point check: obviously unrealistic values ============
        # In addition to PCE, other parameters should also be checked
        if (opt_pce > 28.5 or
            opt_voc > 1.25 or
            opt_ff > 88 or
            opt_jsc > 27
        ):
            score = 0.2
            reason = f"{indicator} ({score} points): Performance values are clearly unrealistic (pce > 28.5%, voc > 1.25 V, ff > 88%, jsc > 27)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # ============ Two-point check: exaggerated or unrealistic metrics ============
        # Check for exaggeration
        inflated_signs = [
            27.2 <= opt_pce <= 28.5,
            opt_voc > 1.22,
            opt_ff > 85,
            opt_jsc > 26
        ]

        if any(inflated_signs) or not all(reasonable_ranges):
            # Print which specific parameter has an issue
            issues = []
            if not pce_reasonable: issues.append(f"pce={opt_pce}")
            if not voc_reasonable: issues.append(f"voc={opt_voc}")
            if not ff_reasonable: issues.append(f"ff={opt_ff}")
            if not jsc_reasonable: issues.append(f"jsc={opt_jsc}")

            score = 0.4
            reason = f"{indicator} ({score} points): Exaggerated or unrealistic metrics detected: {', '.join(issues)}."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        # Calculate improvement
        pce_improvement = opt_pce - ctrl_pce

        voc_improvement = opt_voc - ctrl_voc if ctrl_voc else 0
        ff_improvement = opt_ff - ctrl_ff if ctrl_ff else 0
        jsc_improvement = opt_jsc - ctrl_jsc if ctrl_jsc else 0

        # ============ Three-point check: limited improvement ============
        if 0 < pce_improvement < 1:
            # Check whether other parameters have significantly improved
            other_improvements = (voc_improvement > 0.01 or
                                  ff_improvement > 1 or
                                  jsc_improvement > 0.5)

            if not other_improvements:
                score = 0.6
                reason = f"{indicator} ({score} points): Limited pce improvement ({pce_improvement:.2f}%), with no significant improvement in other parameters."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result
            else:
                score = 0.7
                reason = f"{indicator} ({score} points): Limited pce improvement, but other parameters show improvement."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result

        # ============ Four-point check: moderate improvement ============
        if 1 <= pce_improvement < 2:
            # Check whether the improvement is scientifically reasonable (at least one other parameter also shows improvement)
            improvements_count = sum([
                voc_improvement > 0.02,
                ff_improvement > 2,
                jsc_improvement > 1
            ])

            if improvements_count >= 1:
                score = 0.8
                reason = f"{indicator} ({score} points): Moderate pce improvement ({pce_improvement:.2f}%), with improvements in other parameters as well."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result
            else:
                score = 0.7
                reason = f"{indicator}({score} points): Moderate improvement in pce but other parameters did not improve."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result

        # ============ Five-point check: significant improvement ============
        if pce_improvement >= 2:
            # Check for multi-parameter improvement (scientifically supported improvement)
            improvements_count = sum([
                voc_improvement > 0.03,
                ff_improvement > 3,
                jsc_improvement > 1.5
            ])

            if improvements_count >= 2:
                score = 1
                reason = f"{indicator}({score} points): Significant improvement in pce ({pce_improvement:.2f}%), multiple parameters significantly improved."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result
            elif improvements_count >= 1:
                score = 0.9
                reason = f"{indicator}({score} points): Significant improvement in pce but only one other parameter improved."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result
            else:
                score = 0.8
                reason = f"{indicator}({score} points): Significant improvement in pce but other parameters did not improve."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result

        # Default case (should not reach here)
        score = default_score
        reason = f"{indicator}({score} points): Default rating."
        print(reason)
        result["score"] = score
        result["reason"] = reason

        difficulty = get_difficulty(control)
        result["score"] = result["score"] * difficulty

        return result

    except Exception as e:
        print(e)
        score = None
        reason = f"An error occurred ({e})."
        print(reason)
        result["score"] = score
        result["reason"] = reason
        return result

# 5
@recipe_recommendation_bp.route('/RECIPE/recipe_recommendation', methods=['POST'])
def recipe_recommendation():
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_recipe_recommendation(response, control)

    return jsonify(result)


def calculate_recipe_recommendation(response: dict, control: dict) -> dict:
    '''
        Calculate indicator 'recipe recommendation' score in evaluation layer.

        Args:
            response: Optimized recipe.
            control: Control recipe.

        Returns:
            Indicator 'recipe recommendation' score.
    '''

    def piecewise_difficulty(x):
        """
        Piecewise difficulty function
        x < 10: Linear growth from (0,0) to (10,0.3)
        x ≥ 10: Cubic function
        """

        # (10, 0.3)
        # (15, 0.4)
        # (20, 0.6)
        # (25, 1.0)
        # This growth pattern is: slow growth in the early stage, accelerating growth in the later stage. This is a typical convex function (increasing growth rate)

        if x < 10:
        # if x < 15:
            # Linear: from (0,0) to (10,0.3)
            return 0.03 * x
            # return 0.03 * (x-5)
        else:
            # Cubic function (determined to pass through four points)
            a = 0.00333
            b = -0.07
            c = 0.6667
            return a * x ** 2 + b * x + c
            # return a * (x-5) ** 2 + b * (x-5) + c

    def get_score_predictor(control_pce, optimized_pce):
        configs = [
            {"pce_range": (0, 10), "threshold": 2, "base_score": 0, "difficulty_adj": 0},
            {"pce_range": (10, 15), "threshold": 1, "base_score": 2.5, "difficulty_adj": 5},
            {"pce_range": (15, 20), "threshold": 0.5, "base_score": 5, "difficulty_adj": 10},
            {"pce_range": (20, 25), "threshold": 0.2, "base_score": 8, "difficulty_adj": 15},
            {"pce_range": (25, float('inf')), "threshold": 0.1, "base_score": 10, "difficulty_adj": 20}
        ]

        temp = optimized_pce - control_pce

        for config in configs:
            low, high = config["pce_range"]
            if low <= control_pce < high:
                threshold = config["threshold"]
                base_score = config["base_score"]
                difficulty_adj = config["difficulty_adj"]
                break

        # 计算分数
        if temp < threshold-0.5*2:
            level = 0
        elif temp < threshold-0.5*1:
            level = 1
        elif temp < threshold-0.5*0:
            level = 2
        else:
            level = 3

        level_scores = [0, 10, 20, 30]

        if level==0:
            if control_pce>=20:
                score = max(7.5,5*temp+14)
            elif control_pce>=15:
                score = max(5,5*temp+10)
            elif control_pce>=10:
                score = max(2.5, 5*temp+5)
            else:
                score = max(0, 5*temp-2.5)
        elif level==1:
            if control_pce>=20:
                score = max(7.5,5*temp+11.5) + 10
            elif control_pce>=15:
                score = max(5,5*temp+7.5) + 10
            elif control_pce>=10:
                score = max(2.5, 5*temp+2.5) + 10
            else:
                score = max(0, 5*temp-5) + 10
        elif level==2:
            if control_pce>=20:
                score = max(7.5,5*temp+9) + 20
            elif control_pce>=15:
                score = max(5,5*temp+5) + 20
            elif control_pce>=10:
                score = max(2.5, 5*temp+0) + 20
            else:
                score = max(0, 5*temp-7.5) + 20
        elif level==3:
            if control_pce>=20:
                score = max(7.5,5*temp+6.5) + 30
            elif control_pce>=15:
                score = max(5,5*temp+2.5) + 30
            elif control_pce>=10:
                score = max(2.5, 5*temp-2.5) + 30
            else:
                score = max(0, 5*temp-10) + 30

        return min(score/35, 1.0)

    try:
        response, control = get_param({
            "control_FP": control,
            "optimized_FP": response
        })

        response, control = get_fp_str(response, control)

        score = None
        result = {
            "reason": "initial score",
            "score": score,
        }

        if not (response and control):
            reason = "No valid optimized_FP and control_FP were found."
            print(reason)
            result["score"] = None
            result["reason"] = reason
            return result

        indicator = "recipe_recommendation"

        for k, v in response.items():

            v = str(v)
            if v.lower().strip() in INVALID_STRINGS or v in INORGANIC:
                v = ""
            response[k] = v

        for k, v in control.items():

            v = str(v)
            if v.lower().strip() in INVALID_STRINGS or v in INORGANIC:
                v = ""
            control[k] = v


        relative_score_weight = 0.4
        ctrl_pce_true = get_valid_number_str(control.get("PCE", None))

        # Must be removed before calculating the predicted value
        for key in ["PCE", "Voc", "FF", "Jsc"]:
            response.pop(key, None)
            control.pop(key, None)

        opt_pce_true = get_valid_number_str(response.get("PCE", None))


        try:
            control_copy = control.copy()
            optimized_only_copy = response.copy()
            
            # Ensure inputs are dictionaries
            if not isinstance(control_copy, dict) or not isinstance(optimized_only_copy, dict):
                raise TypeError(f"control and response must be dict before clean_response")
            
            optimized_copy = clean_response(response, control)
            
            # Ensure output is also a dictionary
            if not isinstance(optimized_copy, dict):
                raise TypeError(f"clean_response() should return dict, got {type(optimized_copy)}")

            # First check whether there are parameter changes
            difference = 0
            for field in REQUIRED_FIELDS:
                val1 = control_copy[field]
                val2 = optimized_copy[field]  # Use the supplemented and completed optimized

                # If all are invalid values, skip
                if val1 in INVALID_STRINGS and val2 in INVALID_STRINGS:
                    continue

                # If one is valid and the other is invalid, it is considered a difference
                if val1 in INVALID_STRINGS or val2 in INVALID_STRINGS:
                    difference = 1
                    break

                # Check whether the specific values are different
                if "Formula" in field:
                    if val1 != val2:
                        difference = 1
                        break
                else:
                    try:
                        crtl_value = float(val1)
                        opt_value = float(val2)
                        if crtl_value != opt_value:
                            difference = 1
                            break
                    except (ValueError, TypeError):
                        if val1 != val2:
                            difference = 1
                            break

            # If there is no parameter change
            if difference == 0:
                # Check whether there are parameters that exist in control but are missing in optimized
                has_missing_params = False

                for field in REQUIRED_FIELDS:
                    val1 = control_copy[field]
                    val2 = optimized_only_copy[field]  # Use the unsupplemented optimized

                    # If control has a valid value while optimized does not (invalid value), it is considered missing
                    if val1 not in INVALID_STRINGS and val2 in INVALID_STRINGS:
                        has_missing_params = True
                        break  # Exit upon finding the first missing parameter

                # Score based on whether parameters are missing
                if has_missing_params:
                    # If missing, give 0.3 points
                    score = 0.3
                    reason = f"{indicator}({score} points): Optimize missing valid parameters in control."
                else:
                    # If completely consistent, give 0 points
                    score = 0
                    reason = f"{indicator}({score} points): Optimize has no parameter changes compared to control."

                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result

            # Ensure control and response are dictionaries before prediction
            if not isinstance(control, dict):
                raise TypeError(f"control must be dict, got {type(control)}")
            if not isinstance(response, dict):
                raise TypeError(f"response must be dict, got {type(response)}")
            
            control_pce_result = get_prediction(control)
            optimized_copy_for_pred = clean_response(response.copy(), control.copy())
            optimized_pce_result = get_prediction(optimized_copy_for_pred)
            
            # Ensure results are dictionaries
            if not isinstance(control_pce_result, dict):
                raise TypeError(f"get_prediction() should return dict for control, got {type(control_pce_result)}")
            if not isinstance(optimized_pce_result, dict):
                raise TypeError(f"get_prediction() should return dict for optimized, got {type(optimized_pce_result)}")
            
            control_pce = control_pce_result.get('pce', None)
            optimized_pce = optimized_pce_result.get('pce', None)

            score = get_score_predictor(float(ctrl_pce_true), optimized_pce)
            temp = optimized_pce - control_pce

            reason = f"{indicator}({score} points): Under the evaluator, optimize compared to control ({optimized_pce:.2f} - {control_pce:.2f} = {temp:.2f})."
            result["score"] = score
            result["reason"] = reason


            result["optimize_PCE_pred"] = str(optimized_pce)
            result["control_PCE_pred"] = str(control_pce)

        except Exception as e:
            import traceback
            score = 0
            reason = f"{indicator}({score} points): error in accuracy_reward ({e})"
            print(reason)
            print(f"Full traceback:\n{traceback.format_exc()}")
            result["score"] = score
            result["reason"] = reason
            result["optimize_PCE_pred"] = ""
            result["control_PCE_pred"] = ""
            return result

        return result

    except Exception as e:
        print(e)
        score = None
        reason = f"An error occurred ({e})."
        print(reason)
        result["score"] = score
        result["reason"] = reason
        return result

@experimental_validation_bp.route('/RECIPE/experimental_validation', methods=['POST'])
def experimental_validation():
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_experimental_validation(response, control)

    return jsonify(result)

def calculate_experimental_validation(response: dict, control: dict) -> dict:
    '''
        Calculate indicator 'experimental validation' score in evaluation layer.

        Args:
            response: Optimized recipe.
            control: Control recipe.

        Returns:
            Indicator 'experimental validation' score.
    '''

    def piecewise_difficulty(x):
        """
        Piecewise difficulty function
        x < 10: Linear growth from (0,0) to (10,0.3)
        x ≥ 10: Cubic function
        """

        # (10, 0.3)
        # (15, 0.4)
        # (20, 0.6)
        # (25, 1.0)
        # This growth pattern is: slow growth in the early stage, accelerating growth in the later stage. This is a typical convex function (increasing growth rate)

        if x < 10:
            # if x < 15:
            # Linear: from (0,0) to (10,0.3)
            return 0.03 * x
            # return 0.03 * (x-5)
        else:
            # Cubic function (determined to pass through four points)
            a = 0.00333
            b = -0.07
            c = 0.6667
            return a * x ** 2 + b * x + c
            # return a * (x-5) ** 2 + b * (x-5) + c

    def get_score_true(control_pce, optimized_pce):
        configs = [
            {"pce_range": (0, 15), "threshold": 3.0, "base_score": 0, "difficulty_adj": 0},
            {"pce_range": (15, 20), "threshold": 2.0, "base_score": 2.5, "difficulty_adj": 5},
            {"pce_range": (20, 25), "threshold": 1.0, "base_score": 5, "difficulty_adj": 10},
            {"pce_range": (25, 28), "threshold": 0.5, "base_score": 8, "difficulty_adj": 15},
            {"pce_range": (28, float('inf')), "threshold": 0.3, "base_score": 10, "difficulty_adj": 20}
        ]

        temp = optimized_pce - control_pce

        for config in configs:
            low, high = config["pce_range"]
            if low <= control_pce < high:
                threshold = config["threshold"]
                base_score = config["base_score"]
                difficulty_adj = config["difficulty_adj"]
                break

        if temp < threshold / 4:
            level = 0
        elif temp < threshold / 2:
            level = 1
        elif temp < threshold:
            level = 2
        else:
            level = 3

        level_scores = [0, 10, 20, 30]

        raw_score = (base_score + level_scores[level]) / 35
        difficulty_component = (0.5 * (control_pce - difficulty_adj) - 5) / 35

        score = raw_score + difficulty_component
        return min(score, 1.0)

    try:

        response, control = get_param({
            "control_FP": control,
            "optimized_FP": response
        })

        response, control = get_fp_str(response, control)

        score = None
        result = {
            "reason": "initial score",
            "score": score,
        }

        if not (response and control):
            reason = "No valid optimized_FP and control_FP were found."
            print(reason)
            result["score"] = None
            result["reason"] = reason
            return result

        indicator = "experimental_validation"

        if not has_performance(response):
            for key in ["PCE", "Voc", "FF", "Jsc"]:
                response.pop(key, None)


        for k, v in response.items():

            v = str(v)
            if v.lower().strip() in INVALID_STRINGS or v in INORGANIC:
                v = ""
            response[k] = v

        for k, v in control.items():

            v = str(v)
            if v.lower().strip() in INVALID_STRINGS or v in INORGANIC:
                v = ""
            control[k] = v

        relative_score_weight = 0.4
        ctrl_pce_true = get_valid_number_str(control.get("PCE", None))
        opt_pce_true = get_valid_number_str(response.get("PCE", None))

        try:
            control_copy = control.copy()
            optimized_only_copy = response.copy()
            optimized_copy = clean_response(response, control)

            # First check whether there are parameter changes
            difference = 0
            for field in REQUIRED_FIELDS:
                val1 = control_copy[field]
                val2 = optimized_copy[field]  # Use the supplemented and completed optimized

                # If all are invalid values, skip
                if val1 in INVALID_STRINGS and val2 in INVALID_STRINGS:
                    continue

                # If one is valid and the other is invalid, it is considered a difference
                if val1 in INVALID_STRINGS or val2 in INVALID_STRINGS:
                    difference = 1
                    break

                # Check whether the specific values are different
                if "Formula" in field:
                    if val1 != val2:
                        difference = 1
                        break
                else:
                    try:
                        crtl_value = float(val1)
                        opt_value = float(val2)
                        if crtl_value != opt_value:
                            difference = 1
                            break
                    except (ValueError, TypeError):
                        if val1 != val2:
                            difference = 1
                            break

            # If there is no parameter change
            if difference == 0:
                # Check whether there are parameters that exist in control but are missing in optimized
                has_missing_params = False

                for field in REQUIRED_FIELDS:
                    val1 = control_copy[field]
                    val2 = optimized_only_copy[field]  # Use the unsupplemented optimized

                    # If control has a valid value while optimized does not (invalid value), it is considered missing
                    if val1 not in INVALID_STRINGS and val2 in INVALID_STRINGS:
                        has_missing_params = True
                        break  # Exit upon finding the first missing parameter

                # Score based on whether parameters are missing
                if has_missing_params:
                    # If missing, give 0.3 points
                    score = 0.3
                    reason = f"{indicator}({score} points): Optimize missing valid parameters in control."
                else:
                    # If completely consistent, give 0 points
                    score = 0
                    reason = f"{indicator}({score} points): Optimize has no parameter changes compared to control."

                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result

            if ctrl_pce_true and opt_pce_true:
                control_pce = float(ctrl_pce_true)
                optimized_pce = float(opt_pce_true)

                score = get_score_true(control_pce, optimized_pce)
                temp = optimized_pce - control_pce

                reason = f"{indicator}({score} points): Experimental validation shows optimize compared to control ({optimized_pce:.2f} - {control_pce:.2f} = {temp:.2f})."
                result["score"] = score
                result["reason"] = reason

            else:

                reason = f"{indicator}({score} points): No experimental value exists."
                result["score"] = 0
                result["reason"] = reason

            result["optimize_PCE"] = str(opt_pce_true)
            result["control_PCE"] = str(ctrl_pce_true)

        except Exception as e:
            score = None
            reason = f"{indicator}({score} 分): error in accuracy_reward ({e})"
            print(reason)
            result["score"] = score
            result["reason"] = reason
            result["optimize_PCE"] = ""
            result["control_PCE"] = ""
            return result

        return result

    except Exception as e:
        print(e)
        score = None
        reason = f"An error occurred ({e})."
        print(reason)
        result["score"] = score
        result["reason"] = reason
        return result


@recipe_bp.route('/RECIPE', methods=['POST'])
def recipe():
    data = request.get_json(force=True)
    response, control = get_param(data)
    result = calculate_recipe(response, control)

    return jsonify(result)

def calculate_recipe(response, control):
    '''
        Calculate part 'recipe recommendation' scores in evaluation layer.

        Args:
            response: Optimized recipe.
            control: Control recipe.

        Returns:
            Part 'recipe recommendation' scores.
    '''

    indicators = config.evaluation.recipe_custom.copy()

    result = {}

    if "recipe_integrity" in indicators:
        recipe_integrity_result = calculate_recipe_integrity(response, control)
        result["recipe_integrity"] = recipe_integrity_result
    if "formula_rationality" in indicators:
        formula_rationality_result = calculate_formula_rationality(response, control)
        result["formula_rationality"] = formula_rationality_result
    if "parameter_rationality" in indicators:
        parameter_rationality_result = calculate_parameter_rationality(response, control)
        result["parameter_rationality"] = parameter_rationality_result
    if "experimental_validation" in indicators:
        experimental_validation_result = calculate_experimental_validation(response, control)
        result["experimental_validation"] = experimental_validation_result

    if "performance_rationality" in indicators:
        performance_rationality_result = calculate_performance_rationality(response, control)
        result["performance_rationality"] = performance_rationality_result
    if "recipe_recommendation" in indicators:
        recipe_recommendation_result = calculate_recipe_recommendation(response, control)
        result["recipe_recommendation"] = recipe_recommendation_result

    return result


# After format check, clean response
def clean_response(response: dict, control: dict) -> dict:
    """
    Clean and normalize recipe response data.
    
    Args:
        response: Optimized recipe dictionary.
        control: Control recipe dictionary.
    
    Returns:
        Cleaned recipe dictionary.
    """
    def fix_json_string(json_str):
        """
        Automatically fix format issues in JSON strings, only handle values without quotes
        """
        # Pattern 1: Number + unit without quotes (e.g., 110 °C, 25 min)
        pattern1 = r':\s*(\d+(?:\.\d+)?)\s*([a-zA-Z°µμ%]+)(?=\s*[,}])'
        fixed_str = re.sub(pattern1, r': "\1 \2"', json_str)

        # Pattern 2: Single numeric values without quotes (e.g., 23.16, 110)
        pattern2 = r':\s*(\d+(?:\.\d+)?)(?=\s*[,}])'
        fixed_str = re.sub(pattern2, r': "\1"', fixed_str)

        return fixed_str

    def normalize_chemical_formula(formula):
        """Convert Unicode subscripts in chemical formulas to ordinary numbers"""
        if not isinstance(formula, str):
            return formula

        # Unicode subscript number mapping
        subscript_map = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
            '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
            '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')'
        }

        # Replace all subscript characters
        for sub, normal in subscript_map.items():
            formula = formula.replace(sub, normal)

        return formula

    def clean_formula(formula: str):
        if not isinstance(formula, str):
            return formula

        # Use regular expression to match the first pair of parentheses and the content before them
        match = re.match(r'^(.+?)\s+\(.*\)$', formula)  # r'^([^(]+?)\s*\(.*\)$'
        if match:
            formula_cleaned = match.group(1).strip()
        else:
            formula_cleaned = formula

        if formula_cleaned.lower() in COMPOUND_MAPPING_INVERT.keys():
            formula_cleaned = COMPOUND_MAPPING_INVERT[formula_cleaned.lower()]

        formula_cleaned = normalize_chemical_formula(formula_cleaned)

        print(f"Original formula: {formula} -> After cleaning: {formula_cleaned}")
        return formula_cleaned


    # Ensure response is a dictionary
    if not isinstance(response, dict):
        raise TypeError(f"response must be dict, got {type(response)}")
    if not isinstance(control, dict):
        raise TypeError(f"control must be dict, got {type(control)}")
    
    for key, value in response.items():
        value = str(value)
        value = normalize_chemical_formula(value)

        if "formula" in key.lower():

            if "pvk" in key.lower():
                response[key] = get_formula_pvk(value)
            else:

                if value != "":
                    response[key] = clean_formula(value)

        else:
            if value not in INVALID_STRINGS:
                response[key] = get_valid_number(value)
            else:
                # Only assign if control[key] exists and is not a list/dict
                if key in control:
                    control_value = control[key]
                    # If control value is a valid number string, use it; otherwise keep empty
                    if isinstance(control_value, (int, float)) or (isinstance(control_value, str) and get_valid_number(control_value)):
                        response[key] = get_valid_number(str(control_value))
                    else:
                        response[key] = ""  # Default to empty string instead of potentially invalid value
                else:
                    response[key] = ""

    return response

def clean_response_only(response: dict) -> dict:

    def normalize_chemical_formula(formula):
        """Convert Unicode subscripts in chemical formulas to ordinary numbers"""
        if not isinstance(formula, str):
            return formula

        # Unicode subscript number mapping
        subscript_map = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
            '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
            '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')'
        }

        # Replace all subscript characters
        for sub, normal in subscript_map.items():
            formula = formula.replace(sub, normal)

        return formula

    def clean_formula(formula: str):
        if not isinstance(formula, str):
            return formula

        # Use regular expression to match the first pair of parentheses and the content before them
        match = re.match(r'^(.+?)\s+\(.*\)$', formula)  # r'^([^(]+?)\s*\(.*\)$'
        if match:
            formula_cleaned = match.group(1).strip()
        else:
            formula_cleaned = formula

        if formula_cleaned.lower() in compound_mapping_invert.keys():
            formula_cleaned = compound_mapping_invert[formula_cleaned.lower()]

        formula_cleaned = normalize_chemical_formula(formula_cleaned)

        print(f"Original formula: {formula} -> After cleaning: {formula_cleaned}")
        return formula_cleaned


    for key, value in response.items():
        value = str(value)
        value = normalize_chemical_formula(value)

        if "formula" in key.lower():

            if "pvk" in key.lower():
                response[key] = get_formula_pvk(value)
            else:

                if value != "":
                    response[key] = clean_formula(value)

        else:
            if value not in INVALID_STRINGS:
                response[key] = get_valid_number(value)
            else:
                response[key] = value

    return response

# if __name__ == '__main__':
#     data = {"control_FP": {"ff": "74.942%", "jsc": "23.137 mA/cm²", "pce": "11.862%", "voc": "0.6738 V", "Formula PVK": "Cs₀.₀₅MA₀.₂₃FA₀.₇₂PbI₂.₄Br₀.₆", "Formula SAM 1": "Me-4PACz", "Formula SAM 2": "", "Formula SAM 3": "", "Annealed Time PVK": "15 min", "Concentration PVK": "1.62 mol/L", "Formula Additive 1": "MACl", "Formula Additive 2": "", "Formula Additive 3": "", "Concentration SAM 1": "0.33 mg/mL", "Concentration SAM 2": "", "Concentration SAM 3": "", "Formula Passivator 1": "", "Formula Passivator 2": "", "Formula Passivator 3": "", "Passivator Volume (μL)": "", "Spin Coating Time PVK 1": "10 s", "Spin Coating Time PVK 2": "40 s", "Annealed Temperature PVK": "100°C", "Annealed Time Passivator": "", "Antisolvent Volume (μL)": "160", "Concentration Additive 1": "10.0 mg/mL", "Concentration Additive 2": "", "Concentration Additive 3": "", "Spin Coating Speed PVK 1": "1200 rpm", "Spin Coating Speed PVK 2": "5000 rpm", "Concentration Passivator 1": "", "Concentration Passivator 2": "", "Concentration Passivator 3": "", "Passivator Dropping Timing": "", "Antisolvent Dropping Timing": "8 s before end", "Spin Coating Time Passivator": "", "Spin Coating Speed Passivator": "", "Annealed Temperature Passivator": ""}}
#     opt, ctrl = get_param(data)
#     print(ctrl)
