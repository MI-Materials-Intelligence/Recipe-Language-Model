from flask import Blueprint, jsonify, request

from recipe_recommendation.predictor.predictor_ff import get_ff
from recipe_recommendation.predictor.predictor_jsc import get_jsc
from recipe_recommendation.predictor.predictor_pce import get_pce
from recipe_recommendation.predictor.predictor_voc import get_voc

main_predictor_bp = Blueprint('main_predictor', __name__)


@main_predictor_bp.route('/main_predictor', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    prediction = get_prediction(data)
    return jsonify({
        'data': data,
        'prediction': prediction
    })


def to_string(data: dict) -> dict:
    """Convert all values in JSON format to uniform strings."""
    data_copy = data.copy()

    for key, value in data_copy.items():
        data_copy[key] = str(value)

    return data_copy


def get_prediction(data: dict) -> dict:
    """Predict PCE/FF/Voc/Jsc.

    Args:
        data: Recipe.

    Returns:
        PCE/FF/Voc/Jsc prediction.
    """
    data = data.copy()
    data = to_string(data)

    for key in ["PCE", "FF", "Jsc", "Voc"]:
        data.pop(key, None)

    pce = float(get_pce(data))
    jsc = float(get_jsc(data))
    voc = float(get_voc(data))
    ff = pce * 100 / (jsc * voc)
    return {
        'pce': pce,
        'jsc': jsc,
        'voc': voc,
        'ff': ff
    }
