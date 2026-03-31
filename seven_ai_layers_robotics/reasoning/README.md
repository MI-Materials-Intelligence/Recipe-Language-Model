# Reasoning Layer

## Overview

In the reasoning layer, the fine-tuned domain-specific RLM to generate mechanistic interpretations, performance explanations, and recipe optimization suggestions from experimental records. These reasoning results serve as an important bridge between trained model capability and practical scientific decision-making, and also provide candidate knowledge and reasoning evidence for the downstream Evaluation Layer and Optimization Layer.

## Layer Structure

```
Reasoning/
├── data/
│   
└── src/
    ├── __init__.py
    ├── perovskite_report_generator.py    # Perovskite report generator
    ├── prompts.py                        # Prompt template library
    ├── totext_db.py                      # Database text conversion tool
    └── __init__.py
```

## Input Demo

```json
{
  "No": 2435,
  "Formula PVK": "Cs0.05MA0.1FA0.85PbI3.0",
  "Concentration PVK": 1.73,
  "Spin Coating Speed PVK 1": 1000,
  "Spin Coating Time PVK 1": 10,
  "Spin Coating Speed PVK 2": 5000,
  "Spin Coating Time PVK 2": 40,
  "Antisolvent Dropping Timing": 10,
  "Antisolvent Volume": 200,
  "Annealed Temperature PVK": 110,
  "Annealed Time PVK": 15,
  "PCE": 15.9,
  "FF": 77.7,
  "Voc": 0.98,
  "Jsc": 20.7
}
```

## Output Demo

```json
{"1_Abstract": " Inverted (p–i–n) perovskite solar cells are highly promising for efficient and stable photovoltaics, but their performance remains constrained by non-radiative recombination at buried interfaces and insufficient control over perovskite crystallization. …… This rational, multi-parameter optimization provides a scalable and effective pathway toward high-performance, industrially viable inverted perovskite solar cells.", 
"2_Introduction": "The device displayed a champion PCE of 15.9%, with a VOC of 0.98 V, a JSC of 20.7 mA/cm², and an FF of 77.7%. 1.73 mol/L perovskite precursor solution with the composition of Cs0.05MA0.1FA0.85PbI3.0 was prepared. …… Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"3_Result_Discussion": "The device lacks an interfacial layer designed to mitigate interfacial recombination and improve perovskite crystallization. …… Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
"4_Conclusion": {"4_1_Table": "| F/P Optimization | Performance | Mechanism |\n| Introduction of 4,4,4-NA SAM (0.33 mg/mL in ethanol) and reduction of perovskite precursor concentration to 1.65 mol/L with optimized antisolvent (150 µL ethyl acetate at 15 s). …… "},
"5_Supporting_Information": "4,4,4-NA acts as a multifunctional interfacial modifier. …… These effects collectively prolong photoluminescence lifetime and improve charge transport and extraction, thereby contributing to enhanced device performance"}

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

- **perovskite_report_generator.py**: Report generation for recommended recipes.
- **prompts.py**: Prompt template management for report generation. 
- **totext_db.py**: Natural-language conversion for database records.
