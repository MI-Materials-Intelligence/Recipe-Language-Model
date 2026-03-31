# Generating Layer

## Overview

In the generating layer, the tokenised recipes are comprised into the recipe report with fabrication details, mechanistic descriptions, an optimisation summary, and supporting information. Through atomic skills of edge reporting (generation from single experimental data), single-variable reporting (generation from matched data with single variable), and characterization reporting (generation from matched data with in situ characterization), these processed data are converted into robotic recipe reports.

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

## Input Demo

```json
{
  "analysis_type": "Formula Additive 1",
  "reverse_diff_class": "MACl -> PEAI",
  "sample_id_1": "13873",
  "sample_id_2": "14852",
  "control_device_fabrication": "The hole transport layer (HTL) was fabricated by spin coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto a fluorine-doped tin oxide (FTO) substrate, followed by annealing at 100°C for 10 minutes. …… The control device achieved an average power conversion efficiency (PCE) of 15.6% with a short-circuit current density (JSC) of 20.8 mA/cm², an open-circuit voltage (VOC) of 1.01 V, and a fill factor (FF) of 74.3%.",
  "optimised_device_fabrication": "The hole transport layer (HTL) was fabricated by spin-coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto an FTO substrate, followed by annealing at 100°C for 10 minutes. …… The optimised device achieved an average power conversion efficiency (PCE) of 17.4% with a short-circuit current density (JSC) of 21.5 mA/cm², an open-circuit voltage (VOC) of 1.09 V, and a fill factor (FF) of 74.3%."
  }
```

## Output Demo

```json
{
  "1_Abstract": {
    "1_1_Abstract": "Inverted (p-i-n) perovskite solar cells benefit significantly from additive engineering, in which subtle changes in precursor composition can strongly affect crystallisation and defect passivation. ……. The results demonstrate that PEAI acts as an effective surface-passivating additive, simultaneously reducing the amount of residual PbI₂ and promoting larger, more uniform perovskite grains, thereby enabling higher device efficiency.",
    "1_2_Sample_information": {
      "Analysis_Type": "Formula Additive 1",
      "Change_Category": "MACl -> PEAI",
      "Variable_Type": "Fc10",
      "sample_id_1": "13873, control device",
      "sample_id_2": "14852, optimised device"
    }
  },
  "2_Introduction": {
    "2_1_Control_F_P": "The hole transport layer (HTL) was fabricated by spin coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto a fluorine-doped tin oxide (FTO) substrate, followed by annealing at 100°C for 10 minutes. …… The control device achieved an average power conversion efficiency (PCE) of 15.6% with a short-circuit current density (JSC) of 20.8 mA/cm², an open-circuit voltage (VOC) of 1.01 V, and a fill factor (FF) of 74.3%.",
    "2_2_Optimised_F_P": "The hole transport layer (HTL) was fabricated by spin-coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto an FTO substrate, followed by annealing at 100°C for 10 minutes. …… The optimised device achieved an average power conversion efficiency (PCE) of 17.4% with a short-circuit current density (JSC) of 21.5 mA/cm², an open-circuit voltage (VOC) of 1.09 V, and a fill factor (FF) of 74.3%."
  },
  "3_Result_Discussion": {
    "3_1_Improvement": "The only variable that differed between the two devices was the additive incorporated into the perovskite precursor. The control device used MACl (0.5 mg/mL), whereas the optimised device used PEAI (0.5 mg/mL), with all other fabrication parameters held constant. This substitution led to notable improvements in device performance: the power conversion efficiency (PCE) increased from 15.6% to 17.4%, the open-circuit voltage (VOC) increased from 1.01 V to 1.09 V, and the short-circuit current density (JSC) increased from 20.8 to 21.5 mA/cm².",
    "3_2_Mechanism": "Methylammonium chloride (MACl) is a small, volatile additive composed of a methylammonium cation (MA⁺) and a chloride anion (Cl⁻) that is commonly used to assist in perovskite film formation. …… As a result, replacing MACl with PEAI leads to clear improvements in performance: the PCE increases from 15.6% to 17.4%, the VOC increases from 1.01 V to 1.09 V due to the suppression of nonradiative recombination, and the JSC increases from 20.8 to 21.5 mA cm⁻² due to better crystallinity and a reduced defect density [DOI:10.1038/s41566-019-0398-2]."
  },
  "4_Conclusions": "| F/P Optimisation | Device Performance | Mechanism |\n|---|---|---|\n| Switching the additive from MACl to PEAI at 0.5 mg/mL | The Voc increased from 1.01 V to 1.09 V | Strong coordination between the PEA⁺ cation and undercoordinated Pb²⁺ enables surface passivation and promotes more complete perovskite conversion |",
  "5_Supporting_Information": {
    "substance": "MACl (methylammonium chloride) is composed of CH3 NH3+ and Cl-: CH3 NH3+ indirectly stabilises the perovskite octahedral framework and regulates the crystallisation rate. …… Its structural characteristics are mainly reflected in the cationic part: the phenyl ring is connected to an ethyl chain via a methylene group (-CH2-), and the terminal of the ethyl chain is linked to a positively charged ammonium group (-NH3⁺)[DOI:10.1038/s41566-019-0398-2].",
    "References": "DOI:10.1002/adma.202007126; DOI:10.1016/j.joule.2019.06.014; DOI:10.1038/s41566-019-0398-2; DOI:10.1038/s41566-025-01746-6"
  }
}
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

- **characterisation_reporting_main.py**: Script for characterization report generation.
- **edge_reporting_main.py**: Script for edge report generation.
- **variable_reporting_main.py**: Script for variable report generation.
