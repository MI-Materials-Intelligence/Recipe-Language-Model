from flask import request, jsonify, Blueprint

from recipe_recommendation.predictor.predictor_pce import get_PCE
from recipe_recommendation.predictor.predictor_ff import get_FF
from recipe_recommendation.predictor.predictor_jsc import get_Jsc
from recipe_recommendation.predictor.predictor_voc import get_Voc

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
    # Convert all values in JSON format to uniform strings

    data_copy = data.copy()

    for key, value in data_copy.items():
        data_copy[key] = str(value)

    return data_copy

def get_prediction(data: dict) -> dict:
    '''
        Predict PCE/FF/Voc/Jsc.

        Args:
            data: Recipe.

        Returns:
            PCE/FF/Voc/Jsc prediction.
    '''

    data = data.copy()
    data = to_string(data)

    for key in ["PCE", "FF", "Jsc", "Voc"]:
        data.pop(key, None)

    PCE = float(get_PCE(data))
    Jsc = float(get_Jsc(data))
    Voc = float(get_Voc(data))
    FF = PCE*100 / (Jsc*Voc)

    return {
        'pce': PCE,
        'jsc': Jsc,
        'voc': Voc,
        'ff': FF
    }
