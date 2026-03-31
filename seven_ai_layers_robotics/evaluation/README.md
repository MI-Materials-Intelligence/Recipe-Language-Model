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
"2_Introduction": "The device displayed a champion PCE of 15.821%, with a VOC of 0.9823 V, a JSC of 20.734 mA/cm², and an FF of 77.678%. 1.73 mol/L perovskite precursor solution with the composition of Cs0.05MA0.1FA0.85PbI3.0 was prepared. …… To implement this, introduce a 4,4,4-NA SAM at 0.33 mg/mL in ethanol on the substrate prior to perovskite deposition. Reduce the perovskite precursor concentration to 1.65 mol/L for the Cs₀.₀₅MA₀.₁FA₀.₈₅PbI₃.₀ composition. Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"3_Result_Discussion": "The device lacks an interfacial layer designed to mitigate interfacial recombination and improve perovskite crystallization. …… Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"4_Conclusion": {"4_1_Table": "| F/P Optimization | Performance | Mechanism |\n| Introduction of 4,4,4-NA SAM (0.33 mg/mL in ethanol) and reduction of perovskite precursor concentration to 1.65 mol/L with optimized antisolvent (150 µL ethyl acetate at 15 s). …… "},
"5_Supporting_Information": "4,4,4-NA acts as a multifunctional interfacial modifier. …… These effects collectively prolong photoluminescence lifetime and improve charge transport and extraction, thereby contributing to enhanced device performance"}
```

## Output Demo

```json
{"score": {"overall": 0.76, "Mechanistic_Reasoning": 0.36, "Recipe_Recommendation": 0.40}, "reason": {"Mechanistic_Reasoning": {"domain_knowledge": {"score": 0.70, "reason": "llm: The chemical names and structures are accurate, with only minor ambiguities that do not affect the mechanistic interpretation.; substance: 0.4"}, "mechanism_coherence": {"score": 0.6, "reason": "The explanation is largely coherent, with several weak links or mild contradictions that require mentally filling in missing connections, but the narrative direction is still understandable."}, "mechanism_integrity": {"score": 0.8, "reason": "The mechanism framework is mostly complete, with a minor weakness in the link between formulation and structure, but the overall chain remains continuous and understandable."}, "mechanism_interpretation": {"score": 0.8, "reason": "The interpretation is mostly correct and clearly stated, with minor inaccuracies that do not affect the main mechanistic direction."}, "mechanism_comprehensiveness": {"score": 0.7, "reason": "The explanation covers 2-3 mechanistic layers, showing reasonable breadth, but lacks deeper intrinsic analysis and some characterization support."}}, "Recipe_Recommendation": {"recipe_integrity": {"score": 0.5, "reason": "recipe_integrity(1 points): PVK parameters and passivation process parameters (when a passivation agent is present) are complete and contain extractable numeric values."}, "formula_rationality": {"score": 0.5, "reason": "formula_rationality (1.0 points): All concentration values are extractable and fall within the domain knowledge ranges (e.g., precursors 1.0–1.8 M; additives 1–30 mg/mL; SAMs 0.1–1 mg/mL; passivation agents 0.1–5 mg/mL)."}, "parameter_rationality": {"score": 0.5, "reason": "parameter_rationality (1.0 points): All parameters fall within reasonable ranges."}, "experimental_validation": {"score": 0.9403, "reason": "experimental_validation(0.9403 points): Experimental validation shows optimize compared to control (18.70 - 15.82 = 2.88).", "control_PCE": "15.821", "optimize_PCE": "18.7"}}}}
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
