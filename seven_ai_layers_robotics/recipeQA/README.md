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
    "output": "<think>Alright, let's tackle this problem. I need to analyze why the optimized device with m-F-PEACl shows better performance compared to the control. The control has a PCE of 15.6%, while the optimized one with m-F-PEACl reaches 17.4%. The key changes are in the perovskite layer, specifically using m-F-PEACl instead of whatever was in the control.\n\nFirst, looking at the background knowledge for both compounds. The control isn't specified, but since the optimized uses m-F-PEACl, I'll compare m-F-PEACl against typical perovskite without such additives. The main improvements are in Jsc (20.8 to 21.5 mA/cm²) and Voc (1.01 to 1.09 V), while FF stays the same at 74.3%.\n\nStarting with Voc increase. The background info on m-F-PEACl mentions dual-halide passivation: F⁻ fills halide vacancies, Cl⁻ neutralizes Pb²⁺ dangling bonds. This reduces trap-state density, which directly lowers non-radiative recombination. Less recombination means higher Voc because the quasi-Fermi level splitting improves. Also, the meta-fluoro substituent creates a strong dipole, improving energy-level alignment with the perovskite valence band. Better alignment reduces energy losses at the interface, contributing to higher Voc.\n\nNext, Jsc improvement. The background says m-F-PEACl forms a thin, ordered Ruddlesden-Popper overlayer. This layer suppresses ion migration and reduces defect density. Fewer defects mean less scattering and better charge transport. Also, the phenyl ring's π-π stacking passivates under-coordinated Pb²⁺ sites, which might enhance electron-hole separation. The improved crystallinity and phase purity (as mentioned in m-Br-PEACl's section, but likely similar here) lead to better light absorption and charge collection, hence higher Jsc.\n\nFF remains unchanged. The background notes that m-F-PEACl enhances charge separation and energy-level alignment, but FF stability suggests balanced charge transport. The hydrophobic C-F bond improves moisture resistance, which might prevent FF degradation over time, but since it's the same in the reported average, maybe the immediate effect on series/shunt resistance is neutralized by other factors. The dual-halide passivation reduces recombination, which usually helps FF, but here it's unchanged. Possibly, the series resistance from the HTL or other layers isn't affected, or the passivation mainly impacts Voc and Jsc without altering the resistive components significantly.\n\nWait, the control and optimized both use the same HTL process (NiOx on FTO). So the difference is solely in the perovskite layer with m-F-PEACl. The unchanged FF might indicate that while recombination is reduced (helping Voc), the charge extraction efficiency at interfaces is already optimal in the control, so no further FF gain. Or the reduction in trap density doesn't significantly lower series resistance in this setup.\n\nAlso, m-F-PEACl's minimal lattice disturbance (due to small F size) avoids introducing new defects, which might explain why FF doesn't drop. The ordered RP overlayer ensures smooth charge transfer without adding resistive barriers.\n\nFor Jsc, the slight increase (20.8 to 21.5) could come from better charge collection due to reduced recombination and possibly enhanced light management from the overlayer. The background mentions improved phase purity, which reduces δ-phase impurities, leading to more uniform absorption.\n\nPutting it all together: m-F-PEACl's dual passivation (F⁻ and Cl⁻) slashes trap density, boosting Voc by minimizing non-radiative losses. The interfacial dipole from m-F improves energy alignment, further aiding Voc. The ordered overlayer and reduced defects enhance charge extraction, increasing Jsc. FF stays stable because the passivation doesn't introduce resistive losses, and the existing transport layers are already efficient.\n\nNeed to ensure all points tie back to the provided knowledge without external info. Avoid mentioning m-Br-PEACl's details unless relevant, but since the question is about m-F-PEACl, focus on its mechanisms. Also, note that Cl⁻ might depart during conversion, but the initial passivation still sets the film quality.</think><answer>### Mechanism-Level Analysis of m-F-PEACl Formulation Effects  \n\nThe optimized device incorporating **m-F-PEACl** (meta-fluoro-phenethylammonium chloride) exhibits a **+0.08 V increase in Voc** (1.01 V → 1.09 V) and **+0.7 mA/cm² gain in Jsc** (20.8 → 21.5 mA/cm²) versus the control, while FF remains stable at 74.3%. This performance enhancement arises from *m-F-PEACl*-specific molecular mechanisms that suppress recombination and optimize interfacial energetics, as detailed below:  \n\n#### **1. Voc Enhancement via Suppressed Non-Radiative Recombination**  \n- **Formulation → Defect Passivation:**  \n  The *meta*-fluoro substituent (m-F) and Cl⁻ counterion enable **dual-halide passivation**:  \n  - F⁻ selectively occupies **halide vacancies (Vₓ)** due to fluorine’s high electronegativity and optimal ionic radius, eliminating deep-level traps.  \n  - Cl⁻ neutralizes **under-coordinated Pb²⁺ dangling bonds** at grain boundaries via hydrogen bonding with the –NH₃⁺ group, reducing Pb-related trap states.  \n- **Defect Passivation → Voc Gain:**  \n  This cooperative passivation slashes trap-state density by >1 order of magnitude, directly suppressing **non-radiative Shockley-Read-Hall recombination**. Consequently, quasi-Fermi level splitting increases, elevating Voc by 80 mV. The absence of a heavy-atom effect (unlike Br analogues) prevents spin-orbit coupling-induced recombination losses, further preserving Voc.  \n\n#### **2. Jsc Improvement via Optimized Charge Extraction**  \n- **Formulation → Interfacial Energetics & Morphology:**  \n  - The *m*-F group’s strong σ-electron-withdrawing nature **lowers the HOMO level** of the phenethylammonium cation, enabling **gentle band-edge alignment** with the perovskite valence band. This minimizes energy offsets at the perovskite/HTL interface.  \n  - Simultaneously, the fluorine-induced dipole **adjusts the interfacial work function**, enhancing hole extraction into the NiOx HTL.  \n  - The small molecular volume of *m*-F-PEACl promotes formation of a **thin, ordered Ruddlesden–Popper (RP) overlayer** (n = 2–3 phases) without disrupting bulk crystallinity. This overlayer suppresses ion migration and δ-phase impurities, yielding phase-pure films with reduced RMS roughness.  \n- **Interfacial/Morphology Effects → Jsc Gain:**  \n  Improved energy-level alignment reduces interfacial energy losses, while the RP overlayer’s defect passivation minimizes charge scattering. This enhances **charge collection efficiency** and extends carrier diffusion lengths, directly increasing photocurrent density by 3.4%. The hydrophobic C–F bond further prevents moisture-induced degradation during operation, sustaining Jsc stability.  \n\n#### **3. FF Stability via Balanced Transport**  \n- **Formulation → Transport Dynamics:**  \n  The ethylene linker (–CH₂CH₂–) provides conformational flexibility, allowing the –NH₃⁺ group to dock into perovskite cages while the fluoro-aryl segment forms a **continuous hydrophobic overlayer**. This structure:  \n  - Prevents Cl⁻-induced lattice strain (due to fluorine’s minimal mass), avoiding resistive grain boundaries.  \n  - Suppresses halide ion migration via the RP phase barrier, reducing hysteresis.  \n- **Transport Effects → FF Preservation:**  \n  Balanced electron/hole extraction is maintained as the RP overlayer passivates traps *without* introducing insulating barriers. Series resistance remains unchanged (evidenced by stable FF), while shunt resistance increases due to reduced pinholes from optimized crystallization kinetics.  \n\n### Conclusion  \n*m-F-PEACl*’s molecular design uniquely leverages **fluorine’s electronegativity-driven dipole** and **dual-halide passivation** to simultaneously:  \n(i) Quench halide and Pb²⁺ defects → **Voc ↑ via recombination suppression**,  \n(ii) Tune interfacial energetics and morphology → **Jsc ↑ via efficient charge extraction**,  \n(iii) Enable strain-free RP phase formation → **FF stability via balanced transport**.  \nThe absence of heavy-atom effects (vs. Br analogues) and minimal lattice perturbation maximize Voc gains, while fluorine-specific hydrophobicity ensures operational stability. This mechanism explains the 1.8% absolute PCE improvement (15.6% → 17.4%) without FF trade-offs.</answer>"
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


