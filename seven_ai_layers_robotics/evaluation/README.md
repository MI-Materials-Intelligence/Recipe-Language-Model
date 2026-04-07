# Evaluation Layer

## Overview

In the evaluation layer, the recipe recommendations and mechanistic reasoning are evaluated, in order to measure their effectiveness, reliability, and scientific validity. Through key atomic skills of recipe recommendation and mechanistic reasoning, the aspects of recipe integrity, formula rationality, parameter rationality, experimental validation, domain knowledge, mechanism integrity, interpretation, comprehensiveness and coherence are systematically assessed.

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
    │   ├── __init__.py
    │   ├── recipe_recommendation.py
    │   └── predictor/
    │       ├── main_predictor.py
    │       ├── predictor_ff.py
    │       ├── predictor_jsc.py
    │       ├── predictor_pce.py
    │       └── predictor_voc.py
    ├── __init__.py
    └── MIRecipeEvaluator.py            # Unified evaluator interface
```
## Input Demo

```json
{"1_Abstract": " Inverted (p–i–n) perovskite solar cells are highly promising for efficient and stable photovoltaics, but their performance remains constrained by non-radiative recombination at buried interfaces and insufficient control over perovskite crystallization. …… This rational, multi-parameter optimization provides a scalable and effective pathway toward high-performance, industrially viable inverted perovskite solar cells.", 
"2_Introduction": "The device displayed a champion PCE of 15.9%, with a VOC of 0.98 V, a JSC of 20.8 mA/cm², and an FF of 77.7%. 1.73 mol/L perovskite precursor solution with the composition of Cs0.05MA0.1FA0.85PbI3.0 was prepared. …… Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"3_Result_Discussion": "The device lacks an interfacial layer designed to mitigate interfacial recombination and improve perovskite crystallization. …… Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"4_Conclusion": {"4_1_Table": "| F/P Optimization | Performance | Mechanism |\n| Introduction of 4,4,4-NA SAM (0.33 mg/mL in ethanol) and reduction of perovskite precursor concentration to 1.65 mol/L with optimized antisolvent (150 µL ethyl acetate at 15 s). …… "},
"5_Supporting_Information": "4,4,4-NA acts as a multifunctional interfacial modifier. …… These effects collectively prolong photoluminescence lifetime and improve charge transport and extraction, thereby contributing to enhanced device performance"}
```

## Output Demo

```json
{"score": {"overall": 0.76, "Mechanistic_Reasoning": 0.36, "Recipe_Recommendation": 0.40}}
```

## Basic Usage

> **Note**: If the database has been initialized or the environment configured by other layers, skip the corresponding steps.

1. **Environment Setup**  
   Create and activate virtual environment:
   ```bash
   conda create -n rlm python=3.9 -y
   conda activate rlm
   pip install -r requirements.txt
   ```

2. **Initialize Database**  
   Run SQL script to create tables (skip if already executed by other layers). Input data comes from the Reasoning layer generated reports.
   ```bash
   cd seven_ai_layers_robotics && mysql -u <user> -p <database> < schema.sql
   ```

3. **Configure Settings**  
   Copy `config.example.toml` to `config.toml` and edit with your database connection and API keys.

4. **Run Program**  
   ```bash
   python main.py evaluation
   ```

### Key Modules for Executing Task

- **MIRecipeEvaluator.py**: Unified evaluation module for recipe recommendation and mechanistic reasoning.
- **recipe_recommendation/predictor/**: Predictive modules for device-performance metrics (PCE, Voc, Jsc, FF).
- **mechanistic_reasoning/mechanistic_reasoning.py**: Evaluation modules for mechanistic reasoning analysis.
