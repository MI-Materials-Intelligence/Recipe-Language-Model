# Generating Layer

## Overview

Structured robotic recipe reports are generated from robotic experimental data. Formulas, parameters, performance, and mechanistic information are organised into a standardised format.

Key Atomic skills:
- **Characterization Reporing**: Characterization report generation from matched data with in situ characterization.
- **Edge Reporting**: Edge report generation from single experimental data.
- **Single-Variable Reporting**: Variable report generation from matched data with single variable. 


## Layer Structure with Atomic Skills

```
Generating/
├── data/
│   
└── src/
    ├── characterization_reporting/     # Characterization report generation module
    │   ├── __init__.py
    │   ├── add_report.py
    │   ├── hash.py
    │   ├── pass_report.py
    │   ├── process_report.py
    │   └── sam_report.py
    ├── edge_reporting/                 # Edge report generation module
    │   ├── __init__.py
    │   ├── step2_report.py
    │   ├── step3_deepseek.py
    │   └── templates_new_revised.py
    ├── variable_reporting/             # Variable report generation module
    │   ├── __init__.py
    │   ├── single_report.py
    │   └── single_report_prepare.py
    ├── __init__.py
    ├── characterisation_reporting_main.py
    ├── edge_reporting_main.py
    └── variable_reporting_main.py
```

## Database Requirements

Requires access to Learning layer outputs and experimental metadata.

## Output Data

Outputs SFT training pairs, complete characterization reports, and single-variable comparison reports.

## Basic Usage

### Environment Setup

```bash
conda activate rlm_agent
cd seven_layers/Generating
```

### Usage Example

```python
from src.characterization_reporting import process_report
from src.edge_reporting import step2_report
from src.variable_reporting import single_report

# Characterization report generation
report = process_report(experiment_id="exp_001")

# Edge report generation
edge_cases = step2_report(experiment_records)

# variable report generation
comparison_report = single_report(
    variable_type="annealing_temperature",
    control_value=100,
    experimental_values=[120, 140, 160]
)
```

### Command Line Tools

```bash
# Characterization report generation
python src/characterisation_reporting_main.py

# Edge report generation
python src/edge_reporting_main.py

# variable report generation
python src/variable_reporting_main.py
```

### Key Modules for Executing Task

- **characterisation_reporting_main.py**: Script for characterization report generation.
- **edge_reporting_main.py**: Script for edge report generation.
- **variable_reporting_main.py**: Script for variable report generation.
