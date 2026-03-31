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
  "No": 14852,
  "Formula PVK": "Cs0.05MA0.16FA0.79PbI2.9Br0.1",
  "Concentration PVK": 1.73,
  "Formula Additive 1": "PEAI",
  "Concentration Additive 1": 0.50,
  "Formula SAM 1": "Me-4PACz",
  "Concentration SAM 1": 0.33,
  "Spin Coating Speed PVK 1": 1000,
  "Spin Coating Time PVK 1": 10,
  "Spin Coating Speed PVK 2": 5000,
  "Spin Coating Time PVK 2": 30,
  "Antisolvent Dropping Timing": 6,
  "Antisolvent Volume": 160,
  "Annealed Temperature PVK": 110,
  "Annealed Time PVK": 25,
  "PCE": 17.4,
  "FF": 74.3,
  "Voc": 1.09,
  "Jsc": 21.5
}
```

## Output Demo

```json
{"1_Abstract": " Inverted (p–i–n) perovskite solar cells are highly promising for efficient and stable photovoltaics, but their performance remains constrained by non-radiative recombination at buried interfaces and insufficient control over perovskite crystallization. …… This rational, multi-parameter optimization provides a scalable and effective pathway toward high-performance, industrially viable inverted perovskite solar cells.", 
"2_Introduction": "The device displayed a champion PCE of 15.821%, with a VOC of 0.9823 V, a JSC of 20.734 mA/cm², and an FF of 77.678%. 1.73 mol/L perovskite precursor solution with the composition of Cs0.05MA0.1FA0.85PbI3.0 was prepared. …… To implement this, introduce a 4,4,4-NA SAM at 0.33 mg/mL in ethanol on the substrate prior to perovskite deposition. Reduce the perovskite precursor concentration to 1.65 mol/L for the Cs₀.₀₅MA₀.₁FA₀.₈₅PbI₃.₀ composition. Modify the antisolvent step to 150 µL of ethyl acetate added at 15 s after the start of the second spin-coating stage.", 
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
