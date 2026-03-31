# RecipeQA Layer

## Overview

In the RecipeQA layer, the recipe reports are further converted into semantically structured question–answer pairs (RecipeQA). The primary objective of this layer is to construct high-quality, domain-specific training corpora through key atomic skills of Report to QA (convert recipe reports into semantically structured RecipeQA) and Distillation (knowledge distillation for RecipeQA).

Key Atomic skills:
- Report to QA: convert recipe reports into semantically structured RecipeQA
- Distillation: knowledge distillation for RecipeQA completion

## Layer Structure with Atomic Skills

```
RecipeQA/
├── data/
│  
└── src/
    ├── distillation/                   # Knowledge distillation module
    │   └── optimized.py                # Optimized corpus generation
    ├── report_to_qa/                   # Report to Q&A module
    │   └── single_v2_db.py             # Single-variable corpus generation v2
    ├── corpus_coordinator.py           # Corpus coordinator (main entry)
    └── __init__.py
```

## Input Demo

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

## Output Demo

```json
{
    "instruction": "Based on the perovskite formulation and process description, mechanistically analyze the device's Voc, FF, Jsc, and PCE.",
    "input": "Control Device Fabrication: The hole transport layer (HTL) was fabricated by spin coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto a fluorine-doped tin oxide (FTO) substrate, followed by annealing at 100°C for 10 minutes. …… The control device achieved an average power conversion efficiency (PCE) of 15.6% with a short-circuit current density (JSC) of 20.8 mA/cm², an open-circuit voltage (VOC) of 1.01 V, and a fill factor (FF) of 74.3%. Optimization Device Fabrication: The hole transport layer (HTL) was fabricated by spin-coating 60 μL of a NiOx solution (10 mg/mL in ultrapure water) onto an FTO substrate, followed by annealing at 100°C for 10 minutes. …… The optimised device achieved an average power conversion efficiency (PCE) of 17.4% with a short-circuit current density (JSC) of 21.5 mA/cm², an open-circuit voltage (VOC) of 1.09 V, and a fill factor (FF) of 74.3%.",
    "output": "<think>Alright, let's tackle this problem. I need to analyze why the optimized device with PEAI shows better performance compared to the control. ……</think><answer>Methylammonium chloride (MACl) is a small, volatile additive composed of a methylammonium cation (MA⁺) and a chloride anion (Cl⁻) that is commonly used to assist in perovskite film formation. …… As a result, replacing MACl with PEAI leads to clear improvements in performance: the PCE increases from 15.6% to 17.4%, the VOC increases from 1.01 V to 1.09 V due to the suppression of nonradiative recombination, and the JSC increases from 20.8 to 21.5 mA cm⁻² due to better crystallinity and a reduced defect density [DOI:10.1038/s41566-019-0398-2].</answer>"
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

- **corpus_coordinator.py**: Unified corpus generation coordinator
- **distillation/optimized.py**: Optimized recipe corpus generation
- **report_to_qa/single_v2_db.py**: Single-variable corpus generation


