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
## Input Demo

```json
{"1_Abstract": " Inverted (p–i–n) perovskite solar cells are highly promising for efficient and stable photovoltaics, but their performance remains constrained by non-radiative recombination at buried interfaces and insufficient control over perovskite crystallization. …… This rational, multi-parameter optimization provides a scalable and effective pathway toward high-performance, industrially viable inverted perovskite solar cells.", 
"2_Introduction": "The device displayed a champion PCE of 15.821%, with a VOC of 0.9823 V, a JSC of 20.734 mA/cm², and an FF of 77.678%. 1.73 mol/L perovskite precursor solution with the composition of Cs0.05MA0.1FA0.85PbI3.0 was prepared. …… Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"3_Result_Discussion": "The device lacks an interfacial layer designed to mitigate interfacial recombination and improve perovskite crystallization. …… Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"4_Conclusion": {"4_1_Table": "| F/P Optimization | Performance | Mechanism |\n| Introduction of 4,4,4-NA SAM (0.33 mg/mL in ethanol) and reduction of perovskite precursor concentration to 1.65 mol/L with optimized antisolvent (150 µL ethyl acetate at 15 s). …… "},
"5_Supporting_Information": "4,4,4-NA acts as a multifunctional interfacial modifier. …… These effects collectively prolong photoluminescence lifetime and improve charge transport and extraction, thereby contributing to enhanced device performance"}
```

## Output Demo

```json
{"score": {"overall": 0.76, "Mechanistic_Reasoning": 0.36, "Recipe_Recommendation": 0.40}}}}}
```

## Basic Usage

1. **Initialize Database**  
   Run the SQL script to create tables:
   ```bash
   mysql -u <user> -p <database> < schema.sql
   ```

2. **Configure Settings**  
   Edit `config.toml` with your database and path details.

3. **Run Program**  
   ```bash
   conda activate rlm
   python main.py
   ```

### Key Modules for Executing Task

- **MIRecipeEvaluator.py**: Unified evaluation module for recipe recommendation and mechanistic reasoning. 
- **recipe_recommendation/predictor/**: Predictive modules for device-performance metrics, including PCE, Voc, Jsc, and FF. 
- **mechanistic_reasoning/mechanistic_reasoning.py**: Evaluation modules for mechanistic reasoning analysis.
