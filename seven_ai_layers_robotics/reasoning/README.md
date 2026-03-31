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
{"1_Abstract": "Inverted (p–i–n) perovskite solar cells (PSCs) hold significant promise for high-efficiency, stable photovoltaics, yet interfacial recombination and moisture-induced degradation at the perovskite–hole-transport layer interface remain critical bottlenecks. To address these challenges, we replaced bulk-incorporated phenethylammonium iodide (PEAI) in the precursor solution with a post-deposition phenethylammonium bromide (PEABr) surface treatment—1.0 mg/mL in isopropanol—applied onto a (111)-oriented Cs₀.₀₅MA₀.₁₆FA₀.₇₉PbI₂.₉Br₀.₁ perovskite film (1.73 mol/L) pre-coated with a Me-4PACz self-assembled monolayer (0.33 mg/mL). This strategic shift from bulk additive engineering to targeted surface passivation enabled formation of a thin, oriented 2D PEA₂Pb(BrₓI₁₋ₓ)₄ phase at grain boundaries and the top surface, where the ammonium group passivates undercoordinated Pb²⁺ and halide vacancies via strong N–H···I/Br hydrogen bonding, while the hydrophobic phenyl ring enhances moisture resistance through π–π stacking. Concurrently, bromide incorporation improved energy-level alignment with Me-4PACz, reducing interfacial recombination and facilitating hole extraction. As a result, the optimized devices achieved a substantially enhanced power conversion efficiency (PCE) of 18.03–19.59%, outperforming the PEAI-containing control (17.4%), alongside marked improvements in open-circuit voltage (Voc: 1.075–1.115 V vs. 1.09 V), short-circuit current density (Jsc: 23.00–23.40 mA/cm² vs. 21.5 mA/cm²), and fill factor (FF: 73.6–75.6% vs. 74.3%). The Jsc gain arises from suppressed surface recombination and more efficient charge collection, while Voc and FF enhancements stem from reduced trap-assisted recombination and superior interfacial energetics. This approach demonstrates that precise, post-fabrication surface functionalization—rather than bulk compositional tuning—offers a robust pathway to simultaneously boost efficiency, operational stability, and scalability in inverted PSCs.", 
"2_Introduction": "PSCs with (111)-preferred crystallographic orientation displayed a remarkable PCE of 17.4%, with VOC of 1.09 V, JSC of 21.5 mA/cm², and FF of 74.3%. The composition of perovskite is 1.73 mol/L Cs0.05MA0.16FA0.79PbI2.9Br0.1. A SAM consisting of Me-4PACz (0.33 mg/mL) was incorporated to achieve a more uniform and well-ordered perovskite interface. To prepare the precursor solution with PEAI (0.5 mg/mL), the additive was added to the precursor solution. The perovskite solutions were spin-coated onto the substrate at 1000 rpm for 10 s and then, 5000 rpm for 30 s. 160 µL CB was dripped onto the center of film at 6 s before the end of the spin-coating procedure. Employing an anneal step at 110 °C for 25 min delivered improved crystalline quality and grain uniformity.", 
"3_Result_Discussion": "The baseline formulation employs a (111)-preferred Cs₀.₀₅MA₀.₁₆FA₀.₇₉PbI₂.₉Br₀.₁ perovskite at 1.73 mol/L with PEAI (0.5 mg/mL) added directly to the precursor solution and a Me-4PACz SAM (0.33 mg/mL). This yields a PCE of 17.4%, with Voc of 1.09 V, Jsc of 21.5 mA/cm², and FF of 74.3%. While PEAI partially passivates grain boundaries and surfaces via its phenyl group’s hydrophobic shielding and ammonium-mediated hydrogen bonding to undercoordinated Pb²⁺, its bulk incorporation limits interfacial optimization. The moderate Jsc and FF indicate persistent non-radiative recombination at surfaces and grain boundaries, alongside suboptimal hole extraction. The absence of a dedicated surface-passivating layer leaves the perovskite vulnerable to moisture ingress and interfacial recombination losses, preventing higher Voc and Jsc.  \n\nReplacing PEAI with a PEABr post-treatment addresses these limitations. PEABr (1.0 mg/mL in IPA) forms a thin, oriented PEA₂Pb(BrₓI₁₋ₓ)₄ 2D layer at the perovskite surface and grain boundaries. The phenethylammonium cation’s ammonium group passivates halide vacancies and Pb⁰ defects via strong N–H···I/Br hydrogen bonding, while its phenyl ring enhances hydrophobicity through π–π stacking. The bromide anion aids in forming a thermodynamically stable 2D phase that improves energy-level alignment with the Me-4PACz SAM, reducing interfacial recombination and boosting hole extraction. This dual passivation suppresses trap-assisted recombination, elevating Voc and FF, while the hydrophobic barrier minimizes moisture-induced degradation during operation. Although bulk Br⁻ incorporation is minimal due to the thin 2D layer, it avoids significant bandgap widening or phase segregation risks. The trade-off of slightly increased series resistance from the organic layer is offset by superior recombination suppression and extraction, net improving FF.  \n\nThe optimized formulation retains the perovskite composition (1.73 mol/L Cs₀.₀₅MA₀.₁₆FA₀.₇₉PbI₂.₉Br₀.₁) and Me-4PACz SAM (0.33 mg/mL) but replaces precursor-incorporated PEAI with a PEABr surface treatment. This adjustment elevates performance to a Voc range of [1.075, 1.115] V, Jsc range of [23.00, 23.40] mA/cm², FF range of [73.6, 75.6]%, and PCE range of [18.03, 19.59]%. The Jsc gain stems from reduced surface recombination and improved charge extraction, while the Voc and FF improvements arise from suppressed trap states and better interfacial energetics.  \n\n- Remove PEAI from the perovskite precursor solution.  \n- Apply PEABr at 1.0 mg/mL in isopropanol as a post-deposition surface treatment.", 
"4_Conclusion": {"4_1_Table": "| F/P Optimization | Performance | Mechanism |\n| Removal of PEAI from precursor solution and replacement with PEABr (1.0 mg/mL in IPA) post-treatment | VOC: 1.09 V → 1.115 V (+0.025 V) | Ammonium group of phenethylammonium passivates halide vacancies and Pb⁰ defects via N–H···I/Br hydrogen bonding; bromide enables formation of thermodynamically stable, oriented PEA₂Pb(BrₓI₁₋ₓ)₄ 2D layer improving energy-level alignment with Me-4PACz SAM, suppressing interfacial non-radiative recombination and elevating quasi-Fermi level splitting. |\n| Removal of PEAI from precursor solution and replacement with PEABr (1.0 mg/mL in IPA) post-treatment | JSC: 21.5 mA cm⁻² → 23.40 mA cm⁻² (+1.9 mA cm⁻²) | Reduced surface recombination and improved hole extraction due to better band alignment and defect passivation at perovskite/Me-4PACz interface; hydrophobic phenyl ring (via π–π stacking) minimizes moisture-induced trap formation during operation, preserving charge-carrier lifetime. |\n| Removal of PEAI from precursor solution and replacement with PEABr (1.0 mg/mL in IPA) post-treatment | FF: 74.3% → 75.6% (+1.3 pct) | Suppressed trap-assisted recombination and enhanced interfacial energetics improve charge extraction efficiency; although the organic 2D layer introduces slight series resistance, net gain in recombination suppression and hole transfer kinetics dominates, increasing fill factor. |\n| Removal of PEAI from precursor solution and replacement with PEABr (1.0 mg/mL in IPA) post-treatment | PCE: 17.4% → 19.59% (+2.235 pct) | Combined effect of Voc increase (improved quasi-Fermi level splitting), Jsc gain (reduced surface recombination and enhanced extraction), and FF improvement (optimized interfacial charge dynamics and defect passivation) yields substantial PCE enhancement. |", "4_2_Optimized_Formula_Parameter": {"FF": "73.6–75.6%", "Jsc": "23.00–23.40 mA/cm²", "PCE": "18.03–19.59%", "Voc": "1.075–1.115 V", "Formula PVK": "Cs0.05MA0.16FA0.79PbI2.9Br0.1", "Formula SAM 1": "Me-4PACz", "Formula SAM 2": "", "Formula SAM 3": "", "Annealed Time PVK": "25 min", "Concentration PVK": "1.73 mol/L", "Formula Additive 1": "PEAI", "Formula Additive 2": "", "Formula Additive 3": "", "Concentration SAM 1": "0.33 mg/mL", "Concentration SAM 2": "", "Concentration SAM 3": "", "Formula Passivator 1": "PEABr", "Formula Passivator 2": "", "Formula Passivator 3": "", "Passivator Volume (μL)": "", "Spin Coating Time PVK 1": "10 s", "Spin Coating Time PVK 2": "30 s", "Annealed Temperature PVK": "110 °C", "Annealed Time Passivator": "", "Antisolvent Volume (μL)": "160", "Concentration Additive 1": "0.5 mg/mL", "Concentration Additive 2": "", "Concentration Additive 3": "", "Spin Coating Speed PVK 1": "1000 rpm", "Spin Coating Speed PVK 2": "5000 rpm", "Concentration Passivator 1": "1.0 mg/mL in IPA", "Concentration Passivator 2": "", "Concentration Passivator 3": "", "Passivator Dropping Timing": "", "Antisolvent Dropping Timing": "6 s before end of spin-coating", "Spin Coating Time Passivator": "", "Spin Coating Speed Passivator": "", "Annealed Temperature Passivator": ""}}, 
"5_Supporting_Information": "PEABr is phenethylammonium bromide, a low-dimensional perovskite builder. Its phenethylammonium cation (PEA⁺) forms hydrogen bonds with under-coordinated halides and Pb²⁺ at grain boundaries and surfaces, passivating defects. The hydrophobic phenyl ring suppresses moisture ingress, while Br⁻ anions fill halide vacancies and assist in forming ordered low-dimensional perovskite phases. This reduces non-radiative recombination and ion migration, enhancing stability and efficiency.  \n\nMe-4PACz is a phosphonic acid-based self-assembled monolayer (SAM) with a methoxy-carbazole core. It chemisorbs onto ITO via Pb–O–P bonds, eliminating oxide surface traps and creating a dipole layer that aligns the electrode work function with the perovskite valence band. This minimizes interfacial energy barriers, suppresses Schottky-like recombination, and improves hole extraction. The butyl spacer ensures upright molecular orientation, reducing interfacial disorder, while methoxy groups stabilize the dipole orientation, critical for reducing voltage losses.  \n\nTogether, PEABr enhances bulk and surface passivation, slowing ion migration and degradation, while Me-4PACz optimizes interfacial energetics and extraction. Their combined use reduces recombination at multiple levels—bulk, grain boundaries, and interfaces—synergistically boosting performance and stability without direct contact effects."}

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
