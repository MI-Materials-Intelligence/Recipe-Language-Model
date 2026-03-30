# Evaluation Layer

## Overview

Recommended recipe reports undergo joint numerical and semantic evaluation to assess the capabilities of recipe recommendation and mechanistic reasoning.

Key Atomic Skills:
- **Recipe Recommendation**: Numerical evaluation covering recipe integrity, formula rationality, parameter rationality, and experimental validation. 
- **Mechanistic Reasoning**: Semantic evaluation covering domain knowledge, mechanism integrity, interpretation, comprehensiveness and coherence. 

## Layer Structure with Atomic Skills

```
Evaluation/
├── data/
│   
└── src/
    ├── evaluation/                     # General evaluation module
    │   └── evaluation_custom.py
    ├── mechanistic_reasoning/          # Mechanistic reasoning evaluation
    │   └── mechanistic_reasoning.py
    ├── recipe_recommendation/          # Recipe recommendation evaluation
    │   ├── predictor/
    │   │   ├── main_predictor.py
    │   │   ├── predictor_ff.py
    │   │   ├── predictor_jsc.py
    │   │   ├── predictor_pce.py
    │   │   └── predictor_voc.py
    │   └── recipe_recommendation.py
    ├── MIRecipeEvaluator.py            # Unified evaluator interface
    └── __init__.py
```

## Database Requirements

Requires access to experimental records and evaluation scoring data.

Configuration Example:
```toml
[database]
host = "localhost"
port = 13330
user = "root"
password = "your_password"
database = "rlm_agent"

[evaluation]
enable_auto_evaluation = true
batch_size = 50
confidence_threshold = 0.75
```

## Output Data

Outputs comprehensive recipe evaluation reports, mechanistic reasoning evaluation reports, and batch evaluation statistics.

## Basic Usage

### Environment Setup

```bash
conda activate rlm_agent
cd seven_layers/Evaluation
```

### Usage Example

```python
from src.MIRecipeEvaluator import MIRecipeEvaluator

# Initialize evaluator
evaluator = MIRecipeEvaluator()

# Evaluate single recipe
evaluation_result = evaluator.evaluate_recipe(
    recipe={
        "composition": "FA0.85MA0.15PbI3",
        "additives": ["MACl", "PEAI"],
        "conditions": {...}
    },
    evaluation_type="comprehensive"
)

print(f"Overall Score: {evaluation_result['overall_score']}")
```

### Batch Evaluation

```python
recipes = [...]  # Recipe list
results = evaluator.batch_evaluate(
    recipes=recipes,
    batch_size=50,
    save_intermediate=True
)

# Generate statistics report
stats = evaluator.generate_statistics(results)
evaluator.save_report(stats, "batch_evaluation_report.json")
```

### Performance Prediction

```python
from src.recipe_recommendation.predictor.predictor_pce import PCEPredictor

# Initialize predictor
pce_pred = PCEPredictor()

# Predict PCE
prediction = pce_pred.predict(
    composition="FA0.85MA0.15PbI3",
    additives=["1% MACl", "2% PEAI"],
    conditions={"annealing_temp": 120}
)

print(f"Predicted PCE: {prediction['value']} ± {prediction['uncertainty']}%")
```

### Key Modules for Executing Task

- **MIRecipeEvaluator.py**: Unified evaluation module for recipe recommendation and mechanistic reasoning. 
- **recipe_recommendation/predictor/**: Predictive modules for device-performance metrics, including PCE, Voc, Jsc, and FF. 
- **mechanistic_reasoning/mechanistic_reasoning.py**: Evaluation modules for mechanistic reasoning analysis.
