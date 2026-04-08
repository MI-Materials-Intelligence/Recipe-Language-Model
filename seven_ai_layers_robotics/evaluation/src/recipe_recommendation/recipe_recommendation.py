import os

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Blueprint, jsonify, request

path = Path(__file__).resolve().parents[2]
os.chdir(path)
sys.path.append(str(Path(__file__).resolve().parents[3]))

from recipe_recommendation.predictor.main_predictor import get_prediction
from seven_ai_layers_robotics.config import config

recipe_integrity_bp = Blueprint('recipe_integrity', __name__)
formula_rationality_bp = Blueprint('formula_rationality', __name__)
parameter_rationality_bp = Blueprint('parameter_rationality', __name__)
performance_rationality_bp = Blueprint('performance_rationality', __name__)
recipe_recommendation_bp = Blueprint('recipe_recommendation', __name__)
experimental_validation_bp = Blueprint('experimental_validation', __name__)
recipe_bp = Blueprint('recipe', __name__)

pd.set_option("future.no_silent_downcasting", True)

COMPOUND_MAPPING: dict = {}
COMPOUND_MAPPING_INVERT: dict = {}


def _load_compound_mapping() -> dict:
    """Load compound mapping from configuration file.
    
    Returns:
        Dictionary mapping compound abbreviations to full names.
    """
    with open(config.get_evaluation_data_path('data/compound_mapping.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def _init_compound_mapping() -> None:
    """Initialize compound mapping globals."""
    global COMPOUND_MAPPING, COMPOUND_MAPPING_INVERT
    COMPOUND_MAPPING = _load_compound_mapping()
    COMPOUND_MAPPING_INVERT = get_compound_mapping_invert(COMPOUND_MAPPING)

def get_compound_mapping_invert(compound_mapping: dict) -> dict:
    """Create inverted mapping from compound full name to abbreviation.
    
    Args:
        compound_mapping: Dictionary mapping compound abbreviations to full names.

    Returns:
        Inverted dictionary mapping compound full names (lowercase) to abbreviations.
    """
    compound_mapping_invert = {}
    for k, v in compound_mapping.items():
        v_ = v.split(" (")[1][:-1].lower()
        compound_mapping_invert[f"{v_}"] = k.lower()

    return compound_mapping_invert


def get_valid_number(string: str) -> str:
    """Extract the first valid number from a string using regex.
    
    Args:
        string: Input string potentially containing a number.

    Returns:
        Extracted number as string, or '0' if no number found.
    """
    reg = re.compile(r'\d*\.\d+|\d+')
    matches = re.search(reg, string)
    if matches:
        return matches.group(0)
    return 0


def get_formula_pvk(string: str) -> str:
    """Extract perovskite formula from string using regex pattern.
    
    Args:
        string: Input string containing perovskite formula.

    Returns:
        Extracted perovskite formula string.
    """
    reg = re.compile(r'[A-Za-z]+\d\.{0,1}\d*')
    matches = re.findall(reg, string)

    formula_pvk = ''.join(matches)
    return formula_pvk

def clean_formula(formula: str) -> str:
    """Clean chemical formula by removing content in parentheses.
    
    Args:
        formula: Raw chemical formula string.

    Returns:
        Cleaned formula with parenthetical content removed.
    """
    if not isinstance(formula, str):
        return formula

    match = re.match(r'^([^(]+?)\s*\([^)]*\)', formula)
    if match:
        formula_cleaned = match.group(1).strip()
    else:
        formula_cleaned = formula

    return formula_cleaned


def process_response_formula(response: str) -> str:
    """Process LLM response to extract and clean formula JSON.
    
    Args:
        response: Raw LLM response string containing JSON.

    Returns:
        Cleaned JSON string with processed formula fields.
    """
    json_start = response.rfind("{")
    json_end = response.rfind("}")
    json_content = response[json_start:json_end + 1]

    json_content = json_content.replace("\n", " ")
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

def get_formula_parameters_as_strings(response: dict, control: dict) -> tuple[dict, dict]:
    """Convert recipe parameters to uniform string format.

    Args:
        response: Optimized recipe dictionary.
        control: Control recipe dictionary.

    Returns:
        Tuple of (response, control) with all values converted to strings.
    """

    try:
        if isinstance(response, str):
            response = json.loads(response)
        if isinstance(control, str):
            control = json.loads(control)

        response = json.loads(process_response_formula(json.dumps(response)))

        for key, value in response.items():
            response[key] = str(value)

        for key, value in control.items():
            control[key] = str(value)

        return response, control

    except Exception as e:
        print(f"The input may be neither JSON nor a JSON string ({e})")
        return {}, {}

def get_valid_number_str(string: str) -> str:
    """Extract valid digits from string, handling invalid values.
    
    Args:
        string: Input string potentially containing numeric value.

    Returns:
        Extracted number as string, or empty string if invalid.
    """
    if not isinstance(string, str):
        return ""

    string = string.strip()
    if not string or string.lower() in INVALID_STRINGS:
        return ""

    numbers = re.findall(r'[-+]?\d*\.?\d+', string)
    if numbers:
        try:
            return numbers[0]
        except (ValueError, IndexError):
            return ""
    return ""


def get_param(data: dict) -> tuple[dict, dict]:
    """Extract and normalize optimized and control recipe parameters.
    
    Args:
        data: Dictionary containing optimized_fp and control_fp fields.

    Returns:
        Tuple of (optimize, control) with normalized keys and complete fields.
    """

    optimize = data.get("optimized_fp", {}).copy()
    control = data.get("control_fp", {}).copy()

    if optimize != {}:
        keys_to_update = {}
        for key in list(optimize.keys()):
            if " (μL)" in key:
                new_key = key.replace(" (μL)", "")
                keys_to_update[new_key] = optimize[key]
        optimize.update(keys_to_update)

        for key in keys_to_update:
            old_key = key + " (μL)"
            optimize.pop(old_key, None)


        for field in REQUIRED_FIELDS:
            if field not in optimize:
                optimize[field] = ""

    if control != {}:
        keys_to_update = {}
        for key in list(control.keys()):
            if " (μL)" in key:
                new_key = key.replace(" (μL)", "")
                keys_to_update[new_key] = control[key]
        control.update(keys_to_update)

        for key in keys_to_update:
            old_key = key + " (μL)"
            control.pop(old_key, None)


        for field in REQUIRED_FIELDS:
            if field not in control:
                control[field] = ""

    return optimize, control

def get_difficulty(control: dict) -> float:
    """Calculate difficulty coefficient based on experimental stage complexity.
    
    Args:
        control: Control recipe dictionary.

    Returns:
        Difficulty coefficient (0.5, 0.7, or 1.0).
    """

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
    """Check if optimized recipe contains experimental performance values.
    
    Args:
        optimized: Optimized recipe dictionary.

    Returns:
        True if PCE performance value exists, False otherwise.
    """

    PCE = optimized.get("PCE", "")
    if PCE in INVALID_STRINGS:
        return False

    return True


@recipe_integrity_bp.route('/RECIPE/recipe_integrity', methods=['POST'])
def recipe_integrity() -> tuple:
    """Handle recipe integrity evaluation API request.
    
    Returns:
        JSON response containing recipe integrity score.
    """
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_recipe_integrity(response, control)

    return jsonify(result)

def calculate_recipe_integrity(response: dict, control: dict) -> dict:
    """Calculate recipe integrity indicator score based on completeness and consistency.

    Args:
        response: Optimized recipe dictionary.
        control: Control recipe dictionary.

    Returns:
        Dictionary containing recipe integrity score and reason.
    """


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
            "control_fp": control,
            "optimized_fp": response
        })

        response, control = get_formula_parameters_as_strings(response, control)

        if not (response and control):
            reason = "No valid optimized_fp and control_fp were found."
            print(reason)
            result["reason"] = reason
            return result

        indicator = "recipe_integrity"

        if has_structural_contradictions(response):
            score = 0
            reason = f"{indicator}({score} points): A concentration value exists, but the corresponding formulation field is empty."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        missing_count = 0
        ambiguous_count = 0

        for field in PVK_FIELDS:
            value = str(response.get(field, "")).strip()

            if not value or value.lower() in INVALID_STRINGS:
                missing_count += 1
            else:
                if field != "Formula PVK":
                    if not any(char.isdigit() for char in value) and value.lower() not in INVALID_STRINGS:
                        ambiguous_count += 1

        formula_passivator_1 = str(response.get("Formula Passivator 1", "")).strip()

        if formula_passivator_1 and formula_passivator_1.lower() not in INVALID_STRINGS:
            for field in PASSIVATOR_P_FIELDS:
                value = str(response.get(field, "")).strip()

                if not value or value.lower() in INVALID_STRINGS:
                    missing_count += 1
                else:
                    if not any(char.isdigit() for char in value) and value.lower() not in INVALID_STRINGS:
                        ambiguous_count += 1

        if missing_count >= 8:
            score = 0
            reason = f"{indicator}({score} points): A large number of PVK parameters and passivation process parameters are missing (>8) when a passivation agent is present."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        if missing_count >= 6:
            score = 0.2
            reason = f"{indicator}({score} points): Most PVK parameters and passivation process parameters (when a passivation agent is present) are missing (6-7)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        if missing_count >= 3:
            score = 0.4
            reason = f"{indicator}({score} points): Multiple PVK parameters and passivation process parameters (when a passivation agent is present) are missing (3-5)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        if missing_count >= 1:
            score = 0.6
            reason = f"{indicator}({score} points): A few PVK parameters and passivation process parameters (when a passivation agent is present) are missing (1-2)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        if ambiguous_count >= 1:
            score = 0.8
            reason = f"{indicator}({score} points): PVK parameters and passivation process parameters (when a passivation agent is present) are mostly complete (e.g., parameters like 'after ...' where specific numeric values cannot be extracted)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        score = 1
        reason = f"{indicator}({score} points): PVK parameters and passivation process parameters (when a passivation agent is present) are complete and contain extractable numeric values."
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

@formula_rationality_bp.route('/RECIPE/formula_rationality', methods=['POST'])
def formula_rationality() -> tuple:
    """Handle formula rationality evaluation API request.
    
    Returns:
        JSON response containing formula rationality score.
    """
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_formula_rationality(response, control)

    return jsonify(result)

def calculate_formula_rationality(response: dict, control: dict) -> dict:
    """Calculate formula rationality indicator score based on compound names and concentration ranges.

    Args:
        response: Optimized recipe dictionary.
        control: Control recipe dictionary.

    Returns:
        Dictionary containing formula rationality score and reason.
    """


    try:

        response, control = get_param({
            "control_fp": control,
            "optimized_fp": response
        })

        response, control = get_formula_parameters_as_strings(response, control)

        result = {
            "reason": "initial score",
            "score": 1.0,
        }

        if not (response and control):
            reason = "No valid optimized_fp and control_fp were found."
            print(reason)
            result["score"] = None
            result["reason"] = reason
            return result

        indicator = "formula_rationality"

        ranges = {
            "Concentration PVK": (1.0, 1.8),  # 1.0-1.8 M
            "Concentration Additive": (1, 30),
            "Concentration SAM": (0.1, 1.0),
            "Concentration Passivator": (0.1, 5.0)
        }

        for key, value in response.items():
            value = str(value)

            if value in INORGANIC:
                result["score"] = 0.2
                result["reason"] = "The compound is invalid or may contain some inorganic compounds."

        for field in REQUIRED_FIELDS:
            if "Concentration" in field:

                if response.get(field, "").lower() in INVALID_STRINGS:
                    continue

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

                if min_val <= conc_value <= max_val:
                    continue

                if conc_value < min_val:
                    deviation = (min_val - conc_value) / min_val
                else:
                    deviation = (conc_value - max_val) / max_val

                if conc_value / max_val >= 100 or conc_value / min_val <= 0.001:
                    score = min(result["score"], 0)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains fundamentally invalid concentration values [conc_value/max_val >= 100 or conc_value/min_val <= 0.001]."
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result
                if conc_value / max_val >= 10 or conc_value / min_val <= 0.01:
                    score = min(result["score"], 0.2)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains significantly incorrect concentration values [conc_value/max_val >= 10 or conc_value/min_val <= 0.01]."
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result
                if conc_value / max_val >= 1 or conc_value / min_val <= 0.1:
                    score = min(result["score"], 0.4)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains clearly abnormal concentration values (or irrelevant compounds may have been extracted) [conc_value/max_val >= 1 or conc_value/min_val <= 0.1]."
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result
                if deviation > 0.05:
                    score = min(result["score"], 0.6)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains concentration values that deviate from the standard range (or inorganic compounds may have been extracted) [deviation > 0.05]."
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result
                else:
                    score = min(result["score"], 0.8)
                    reason = f"{indicator} ({score} points): {field} = {conc_value} contains concentration values with slight deviation (or inorganic compounds may have been extracted) [deviation <= 0.05]."
                    print(reason)
                    result["score"] = score
                    result["reason"] = reason
                    return result

        if result["score"] == 1:
            score = result["score"]
            reason = f"{indicator} ({score} points): All concentration values are extractable and fall within the domain knowledge ranges (e.g., precursors 1.0-1.8 M; additives 1-30 mg/mL; SAMs 0.1-1 mg/mL; passivation agents 0.1-5 mg/mL)."
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

@parameter_rationality_bp.route('/RECIPE/parameter_rationality', methods=['POST'])
def parameter_rationality() -> tuple:
    """Handle parameter rationality evaluation API request.
    
    Returns:
        JSON response containing parameter rationality score.
    """
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_parameter_rationality(response, control)

    return jsonify(result)

def calculate_parameter_rationality(response: dict, control: dict) -> dict:
    """Calculate parameter rationality indicator score based on process parameter reliability.

    Args:
        response: Optimized recipe dictionary.
        control: Control recipe dictionary.

    Returns:
        Dictionary containing parameter rationality score and reason.
    """

    """
        Process parameter reliability evaluation
        Use logic similar to formula_rationality
    """

    try:

        response, control = get_param({
            "control_fp": control,
            "optimized_fp": response
        })

        response, control = get_formula_parameters_as_strings(response, control)

        result = {
            "reason": "initial score",
            "score": 1.0,
        }

        if not (response and control):
            reason = "No valid optimized_fp and control_fp were found."
            print(reason)
            result["score"] = None
            result["reason"] = reason
            return result

        indicator = "parameter_rationality"

        parameter_ranges = {
            "Spin Coating Speed SAM": (2000, 5000),
            "Spin Coating Time SAM": (20, 30),
            "Spin Coating Speed PVK 1": (500, 2200),
            "Spin Coating Time PVK 1": (5, 30),
            "Spin Coating Speed PVK 2": (3500, 7000),
            "Spin Coating Time PVK 2": (21, 50),
            "Spin Coating Speed Passivator": (2000, 6000),
            "Spin Coating Time Passivator": (15, 40),

            "Annealed Temperature SAM": (90, 120),
            "Annealed Temperature PVK": (90, 120),
            "Annealed Temperature Passivator": (80, 120),

            "Annealed Time SAM": (5, 20),
            "Annealed Time PVK": (5, 60),
            "Annealed Time Passivator": (2, 15),

            "Antisolvent Dropping Timing": (2, 20),
            "Antisolvent Volume": (80, 300),
            "Passivator Dropping Timing": (5, 18),
            "Passivator Volume": (60, 200)
        }

        for field, (min_val, max_val) in parameter_ranges.items():
            field_value = response.get(field, "")
            if not isinstance(field_value, str):
                field_value = str(field_value)

            if field_value.lower() in INVALID_STRINGS:
                continue

            value_str = get_valid_number_str(field_value)

            if value_str == "":
                score = 0
                reason = f"{indicator} ({score} points): The value of {field} cannot be parsed."
                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result

            value = float(value_str)

            if min_val <= value <= max_val:
                continue

            if value < min_val:
                deviation = (min_val - value) / min_val
            else:  # value > max_val
                deviation = (value - max_val) / max_val


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

@performance_rationality_bp.route('/RECIPE/performance_rationality', methods=['POST'])
def performance_rationality() -> tuple:
    """Handle performance rationality evaluation API request.
    
    Returns:
        JSON response containing performance rationality score.
    """
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_performance_rationality(response, control)

    return jsonify(result)

def calculate_performance_rationality(response: dict, control: dict) -> dict:
    """Calculate performance rationality indicator score based on physical limits and improvement rationality.

    Args:
        response: Optimized recipe dictionary with performance values.
        control: Control recipe dictionary with performance values.

    Returns:
        Dictionary containing performance rationality score and reason.
    """

    def safe_float(value_str):
        """Safely convert string to float with error handling.
        
        Args:
            value_str: String value to convert.
            
        Returns:
            Float value if conversion successful, None otherwise.
        """
        if not value_str or value_str == "":
            return None
        try:
            return float(value_str)
        except (ValueError, TypeError):
            return None

    try:

        response, control = get_param({
            "control_fp": control,
            "optimized_fp": response
        })

        response, control = get_formula_parameters_as_strings(response, control)

        result = {
            "reason": "initial score",
            "score": 0.6,
        }

        default_score = result["score"]

        if not (response and control):
            reason = "No valid optimized_fp and control_fp were found."
            print(reason)
            result["score"] = None
            result["reason"] = reason
            return result

        indicator = "performance_rationality"

        opt_pce = safe_float(get_valid_number_str(response.get("PCE", "")))
        opt_ff = safe_float(get_valid_number_str(response.get("FF", "")))
        opt_jsc = safe_float(get_valid_number_str(response.get("Jsc", "")))
        opt_voc = safe_float(get_valid_number_str(response.get("Voc", "")))

        ctrl_pce = safe_float(get_valid_number_str(control.get("PCE", "")))
        ctrl_ff = safe_float(get_valid_number_str(control.get("FF", "")))
        ctrl_jsc = safe_float(get_valid_number_str(control.get("Jsc", "")))
        ctrl_voc = safe_float(get_valid_number_str(control.get("Voc", "")))

        if any(v is None for v in [opt_pce, opt_ff, opt_jsc, opt_voc]):
            score = default_score
            reason = f"{indicator} ({score} points): The performance data of the optimized group is incomplete."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        if any(v is None for v in [ctrl_pce, ctrl_ff, ctrl_jsc, ctrl_voc]):
            score = default_score
            reason = f"{indicator} ({score} points): The performance data of the control group is incomplete."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        if opt_pce > 30.0:
            score = 0
            reason = f"{indicator} ({score} points): pce = {opt_pce}% exceeds the physical limit (>30%)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        if opt_pce <= ctrl_pce:
            score = 0
            reason = f"{indicator} ({score} points): The optimized group pce ({opt_pce}%) <= the control group pce ({ctrl_pce}%)."
            print(reason)
            result["score"] = score
            result["reason"] = reason
            return result

        pce_reasonable = 1.0 <= opt_pce <= 27.0
        voc_reasonable = 0.5 <= opt_voc <= 1.22
        ff_reasonable = 60 <= opt_ff <= 85
        jsc_reasonable = 15 <= opt_jsc <= 26

        reasonable_ranges = [pce_reasonable, voc_reasonable, ff_reasonable, jsc_reasonable]

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

        inflated_signs = [
            27.2 <= opt_pce <= 28.5,
            opt_voc > 1.22,
            opt_ff > 85,
            opt_jsc > 26
        ]

        if any(inflated_signs) or not all(reasonable_ranges):
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

        pce_improvement = opt_pce - ctrl_pce

        voc_improvement = opt_voc - ctrl_voc if ctrl_voc else 0
        ff_improvement = opt_ff - ctrl_ff if ctrl_ff else 0
        jsc_improvement = opt_jsc - ctrl_jsc if ctrl_jsc else 0

        if 0 < pce_improvement < 1:
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

        if 1 <= pce_improvement < 2:
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

        if pce_improvement >= 2:
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

@recipe_recommendation_bp.route('/RECIPE/recipe_recommendation', methods=['POST'])
def recipe_recommendation():
    data = request.get_json(force=True)
    response, control = get_param(data)

    result = calculate_recipe_recommendation(response, control)

    return jsonify(result)


def calculate_recipe_recommendation(response: dict, control: dict) -> dict:
    """Calculate indicator 'recipe recommendation' score in evaluation layer.

    Args:
        response: Optimized recipe.
        control: Control recipe.

    Returns:
        Indicator 'recipe recommendation' score.
    """

    def piecewise_difficulty(x):
        """
        Piecewise difficulty function
        x < 10: Linear growth from (0,0) to (10,0.3)
        x >= 10: Cubic function
        """


        if x < 10:
            return 0.03 * x
        else:
            a = 0.00333
            b = -0.07
            c = 0.6667
            return a * x ** 2 + b * x + c

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
            "control_fp": control,
            "optimized_fp": response
        })

        response, control = get_formula_parameters_as_strings(response, control)

        score = None
        result = {
            "reason": "initial score",
            "score": score,
        }

        if not (response and control):
            reason = "No valid optimized_fp and control_fp were found."
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

        for key in ["PCE", "Voc", "FF", "Jsc"]:
            response.pop(key, None)
            control.pop(key, None)

        opt_pce_true = get_valid_number_str(response.get("PCE", None))


        try:
            control_copy = control.copy()
            optimized_only_copy = response.copy()
            
            if not isinstance(control_copy, dict) or not isinstance(optimized_only_copy, dict):
                raise TypeError(f"control and response must be dict before clean_response")
            
            optimized_copy = clean_response(response, control)
            
            if not isinstance(optimized_copy, dict):
                raise TypeError(f"clean_response() should return dict, got {type(optimized_copy)}")

            difference = 0
            for field in REQUIRED_FIELDS:
                val1 = control_copy[field]
                val2 = optimized_copy[field]  # Use the supplemented and completed optimized

                if val1 in INVALID_STRINGS and val2 in INVALID_STRINGS:
                    continue

                if val1 in INVALID_STRINGS or val2 in INVALID_STRINGS:
                    difference = 1
                    break

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

            if difference == 0:
                has_missing_params = False

                for field in REQUIRED_FIELDS:
                    val1 = control_copy[field]
                    val2 = optimized_only_copy[field]  # Use the unsupplemented optimized

                    if val1 not in INVALID_STRINGS and val2 in INVALID_STRINGS:
                        has_missing_params = True
                        break  # Exit upon finding the first missing parameter

                if has_missing_params:
                    score = 0.3
                    reason = f"{indicator}({score} points): Optimize missing valid parameters in control."
                else:
                    score = 0
                    reason = f"{indicator}({score} points): Optimize has no parameter changes compared to control."

                print(reason)
                result["score"] = score
                result["reason"] = reason
                return result

            if not isinstance(control, dict):
                raise TypeError(f"control must be dict, got {type(control)}")
            if not isinstance(response, dict):
                raise TypeError(f"response must be dict, got {type(response)}")
            
            control_pce_result = get_prediction(control)
            optimized_copy_for_pred = clean_response(response.copy(), control.copy())
            optimized_pce_result = get_prediction(optimized_copy_for_pred)
            
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
    """Calculate indicator 'experimental validation' score in evaluation layer.

    Args:
        response: Optimized recipe.
        control: Control recipe.

    Returns:
        Indicator 'experimental validation' score.
    """

    def piecewise_difficulty(x):
        """
        Piecewise difficulty function
        x < 10: Linear growth from (0,0) to (10,0.3)
        x >= 10: Cubic function
        """


        if x < 10:
            return 0.03 * x
        else:
            a = 0.00333
            b = -0.07
            c = 0.6667
            return a * x ** 2 + b * x + c

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
            "control_fp": control,
            "optimized_fp": response
        })

        response, control = get_formula_parameters_as_strings(response, control)

        score = None
        result = {
            "reason": "initial score",
            "score": score,
        }

        if not (response and control):
            reason = "No valid optimized_fp and control_fp were found."
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

            difference = 0
            for field in REQUIRED_FIELDS:
                val1 = control_copy[field]
                val2 = optimized_copy[field]  # Use the supplemented and completed optimized

                if val1 in INVALID_STRINGS and val2 in INVALID_STRINGS:
                    continue

                if val1 in INVALID_STRINGS or val2 in INVALID_STRINGS:
                    difference = 1
                    break

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

            if difference == 0:
                has_missing_params = False

                for field in REQUIRED_FIELDS:
                    val1 = control_copy[field]
                    val2 = optimized_only_copy[field]  # Use the unsupplemented optimized

                    if val1 not in INVALID_STRINGS and val2 in INVALID_STRINGS:
                        has_missing_params = True
                        break  # Exit upon finding the first missing parameter

                if has_missing_params:
                    score = 0.3
                    reason = f"{indicator}({score} points): Optimize missing valid parameters in control."
                else:
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
            reason = f"{indicator}({score} points): error in accuracy_reward ({e})"
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
        pattern1 = r':\s*(\d+(?:\.\d+)?)\s*([a-zA-Z°µμ%]+)(?=\s*[,}])'
        fixed_str = re.sub(pattern1, r': "\1 \2"', json_str)

        pattern2 = r':\s*(\d+(?:\.\d+)?)(?=\s*[,}])'
        fixed_str = re.sub(pattern2, r': "\1"', fixed_str)

        return fixed_str

    def normalize_chemical_formula(formula):
        """Convert Unicode subscripts in chemical formulas to ordinary numbers"""
        if not isinstance(formula, str):
            return formula

        subscript_map = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
            '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
            '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')'
        }

        for sub, normal in subscript_map.items():
            formula = formula.replace(sub, normal)

        return formula

    def clean_formula(formula: str):
        if not isinstance(formula, str):
            return formula

        match = re.match(r'^(.+?)\s+\(.*\)$', formula)
        if match:
            formula_cleaned = match.group(1).strip()
        else:
            formula_cleaned = formula

        if formula_cleaned.lower() in COMPOUND_MAPPING_INVERT.keys():
            formula_cleaned = COMPOUND_MAPPING_INVERT[formula_cleaned.lower()]

        formula_cleaned = normalize_chemical_formula(formula_cleaned)

        return formula_cleaned


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
                if key in control:
                    control_value = control[key]
                    if isinstance(control_value, (int, float)) or (isinstance(control_value, str) and get_valid_number(control_value)):
                        response[key] = get_valid_number(str(control_value))
                    else:
                        response[key] = ""
                else:
                    response[key] = ""

    return response

def clean_response_only(response: dict) -> dict:

    def normalize_chemical_formula(formula):
        """Convert Unicode subscripts in chemical formulas to ordinary numbers"""
        if not isinstance(formula, str):
            return formula

        subscript_map = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
            '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
            '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')'
        }

        for sub, normal in subscript_map.items():
            formula = formula.replace(sub, normal)

        return formula

    def clean_formula(formula: str):
        if not isinstance(formula, str):
            return formula

        match = re.match(r'^(.+?)\s+\(.*\)$', formula)
        if match:
            formula_cleaned = match.group(1).strip()
        else:
            formula_cleaned = formula

        if formula_cleaned.lower() in compound_mapping_invert.keys():
            formula_cleaned = compound_mapping_invert[formula_cleaned.lower()]

        formula_cleaned = normalize_chemical_formula(formula_cleaned)

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

def init_app():
    _init_compound_mapping()
