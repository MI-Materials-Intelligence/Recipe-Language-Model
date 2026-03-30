# perovskite_text_generator.py
import random

# ---------------------------
# 模板列表定义
# ---------------------------
# 同义和短语库定义
# --------------------------------------

# 制备相关表述（Prepared Phrases, 15条）
prepared_phrases = [
    "was prepared",
    "was formulated",
    "was synthesized",
    "was generated",
    "was developed",
    "was crafted",
    "was produced",
    "was engineered",
    "was established",
    "was put together",
    "was constituted",
    "was assembled",
    "was devised",
    "was meticulously prepared",
    "was refined and produced"
]

# 引言和背景描述（Introductory Phrases, 15条）
intro_segments = [
"Based on a systematically tuned set of experimental parameters, this perovskite solar cell {prepared_term}, ultimately achieving a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "Drawing upon carefully optimized conditions, the perovskite device {prepared_term}, resulting in a PCE of {pce}%, with a fill factor of {ff}%, an open-circuit voltage of {voc} V, and a short-circuit current density of {jsc} mA/cm².",
        "By refining specific fabrication parameters, a perovskite solar cell {prepared_term}, culminating in performance metrics including a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "Through deliberate control of solution composition, coating speeds, and thermal treatments, this perovskite cell {prepared_term}, leading to a PCE of {pce}%, a fill factor of {ff}%, a Voc of {voc} V, and a Jsc of {jsc} mA/cm².",
        "Using a parameter-driven approach, we have engineered a perovskite solar cell that {prepared_term}, thus realizing a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "This work arises from meticulous parameter optimization, where a perovskite solar device {prepared_term}, reflecting a PCE of {pce}%, with an FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "Within a framework of controlled experimental inputs, a perovskite cell configuration {prepared_term}, ultimately manifesting a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "Each step—from solution concentration to annealing—was tuned to shape this perovskite solar cell, which {prepared_term}, yielding a PCE of {pce}%, an FF of {ff}%, a Voc of {voc} V, and a Jsc of {jsc} mA/cm².",
        "Guided by experimental parameters such as spin speeds, antisolvent timing, and annealing profiles, this device {prepared_term}, realizing a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "Informed by incremental parameter refinements, the perovskite assembly {prepared_term}, resulting in a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "A methodical exploration of fabrication parameters ensured the perovskite cell {prepared_term}, translating each controlled variable into a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "This study emerges from parameter-centric experimentation, producing a perovskite solar cell that {prepared_term}, with a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "By interlinking experimental conditions with device architecture, a perovskite solar cell {prepared_term}, affirming a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "Through iterative refinements in substrate preparation, solution concentration, and coating protocols, this perovskite device {prepared_term}, echoing a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "Systematic parameter adjustments underlie the fabrication of a perovskite cell that {prepared_term}, capturing how controlled conditions influence a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².",
        "The combined treatment featured a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².", # 20250411文献模板
        "Consequently, the device resulted in device efficiency of {pce}%, together with an enhanced fill factor (FF) of {ff}%, short-circuit current density of {jsc} mA/cm²and open circuit voltage (VOC) of {voc} V.",# 20250411文献模板
        "The PCE reached for the device was {pce}%, with a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}%." , # 20250411文献模板
        "With this engineering, the resulting PSCs obtained a PCE of {pce}%, a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm²." , # 20250411文献模板
        "The control device displays a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}%, turning out a moderate PCE of {pce}%." , # # 20250411文献模板
        "The device shows the highest PCE of {pce}% with negligible hysteresis, a VOC of {voc} V, a JSC of {jsc} mA/cm² and a FF of {ff}%." , # 20250411文献模板
        " The device achieves a notably enhanced PCE of {pce}%, corresponding to a JSC of {jsc} mA/cm², a VOC of {voc} V, and an FF of {ff}%. " , # 20250411文献模板
        "The PSCs exhibited a superior PCE of {pce}% (JSC: {jsc} mA/cm², VOC: {voc} V, FF: {ff}%).",  # 20250411文献模板
        "The target device achieved a champion PCE of {pce}% (VOC: {voc} V, JSC: {jsc} mA/cm², FF: {ff}%)."  # 20250411文献模板
        "The target PSCs achieved an average power conversion efficiency (PCE) of {pce}% with a short-circuit current density (JSC) of {jsc} mA/cm², an open-circuit voltage (VOC) of {voc} V and a fill factor (FF) of {ff}%." , # 20250411文献模板
        "The best performance, which showed {pce}% certificated efficiency with a VOC of {voc} V, a JSC of {jsc} mA/cm², and a FF of {ff}%." , # 20250411文献模板
        "The PSCs achieved a champion power conversion efficiency (PCE) of {pce}% under an active area of 0.09 cm², with a VOC value of {voc} V, an FF value of {ff}%, and a current density (JSC) of {jsc} mA/cm².", # 20250411文献模板
        "The PCE devices reached {pce}% and featured a VOC of {voc} V, FF of {ff}%, and short-circuit current density (JSC) of {jsc} mA/cm².",  # 20250411文献模板
        "The inverted devices achieved optimal PCEs of {pce}%, a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  # 20250411文献模板
        "The resulting hybrid SAMs-modified PSC achieve a champion PCE of {pce}%, with VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm²." , # 20250411文献模板
        "PSCs based on additives achieved a PCE of {pce}%, with a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  # 20250411文献模板
        "A higher PCE of {pce}% of the target device is achieved, where JSC, VOC and FF are {jsc} mA/cm², {voc} V and {ff}%, respectively.",  # 20250411文献模板
        "The champion device fabricated by perovskite film showed a PCE of {pce}% with open-circuit voltage (VOC) of {voc} V, short current density (JSC) of {jsc} mA/cm², and a fill factor (FF) of {ff}%.", # 20250411文献模板
        "Remarkably, it achieved an impressive PCE of {pce}% with a high VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",  # 20250424文献模板
        "The performance parameters (PCE, open-circuit voltage (VOC), short-circuit current density (JSC) and fill factor (FF)) of the control PSCs are significantly improved ({pce}%, {voc} V, {jsc} mA/cm², and {ff}%)." , # 20250424文献模板
        "The device achieved a remarkable PCE of {pce}%, with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",  # 20250424文献模板
        "The device demonstrated a champion efficiency of {pce}%, with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%."  # 20250424文献模板
        "The device achieved a champion PCE of {pce}% with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",  # 20250424文献模板
        "The solar cells showed a champion PCE of {pce}% with a VOC of {voc} V, a JSC of {jsc} mA/cm², and a FF of {ff}%." , # 20250424文献模板
        "A champion PCE of {pce}% with a JSC of {jsc} mA/cm², a VOC of {voc} V, and a FF of {ff}% was achieved with optimized perovskite layer prepared with non-stoichiometric precursor solution (NSPS)." , # 20250424文献模板
        "The device exhibited a PCE of {pce}%, with VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm²." , # 20250424文献模板
        "The champion device showed a PCE of {pce}%, with JSC of {jsc} mA/cm², FF of {ff}%, and VOC of {voc} V." , # 20250424文献模板
        "The resulting hybrid SAMs-modified PSC achieve a champion PCE of {pce}%, with VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm²." , # 20250424文献模板
        "PSCs based on additives achieved a PCE of {pce}%, with a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  # 20250424文献模板
        "With the improved uniformity of SAM, the SAM-based devices showed a maximum PCE of {pce}%, with a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  # 20250424文献模板
        "The inverted devices based on perovskite achieved optimal PCEs of {pce}%, a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  # 20250424文献模板
        "The control device displays a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}%, tuning out a PCE of {pce}%.",  # 20250424文献模板
        "The PSCs achieved a quasi-steady-state PCE of {pce}% (VOC: {voc} V, JSC: {jsc} mA/cm², FF: {ff}%).",  # 20250424文献模板
        "The inverted PSCs achieved a champion PCE of {pce}% with an open-circuit voltage (VOC) of {voc} V, short-circuit current density (JSC) of {jsc} mA/cm², and fill factor (FF) of {ff}%.",  # 20250424文献模板
        "The champion device showed a JSC of {jsc} mA/cm², a VOC of {voc} V, and a FF of {ff}%, resulting in a PCE of {pce}%.",  # 20250424文献模板
        "The champion target devices showed a JSC of {jsc} mA/cm², a VOC of {voc} V, and a FF of {ff}%, resulting in a PCE of {pce}%.", # 20250424文献模板
        "The device showed the highest certified PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%."  # 20250424文献模板
        "The device shows a maximum PCE of {pce}%, with an open-circuit voltage (VOC) of {voc} V, a short-circuit current density (JSC) of {jsc} mA/cm², and a fill factor (FF) of {ff}%.",# 20250424文献模板
        "PSCs with (111)-preferred crystallographic orientation displayed a remarkable PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",# 20250424文献模板
        "The target PSCs achieved an average power conversion efficiency (PCE) of {pce}% with a short-circuit current density (JSC) of {jsc} mA/cm², an open-circuit voltage (VOC) of {voc} V, and a fill factor (FF) of {ff}%.",# 20250424文献模板
        "The best performance device showed a {pce}% certificated efficiency with a VOC of {voc} V, a JSC of {jsc} mA/cm², and a FF of {ff}%.",# 20250424文献模板
        "The PSCs achieved a champion power conversion efficiency (PCE) of {pce}%, with VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².", # 20250424文献模板
        "The PCE of devices reached {pce}%, featuring VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  # 20250424文献模板
        "The devices exhibited an increased PCE from {pce}% to {pce}%, with a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",# 20250424文献模板
        "The champion device offers a high PCE of {pce}% for the reverse scan (JSC of {jsc} mA/cm², VOC of {voc} V, and FF of {ff}%).",# 20250424文献模板
        "A higher PCE of {pce}% is achieved with JSC of {jsc} mA/cm², VOC of {voc} V, and FF of {ff}%.",  # 20250424文献模板
        "The PCE for the device reached {pce}%, with a JSC of {jsc} mA/cm², a VOC of {voc} V and a FF of {ff}%.",  # 20250424文献模板
        "PSC with device efficiency (PCE) of {pce}%, VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}% was obtained.",# 20250424文献模板
        "This resulted in improved performance with a PCE beyond {pce}%, a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}%.",# 20250424文献模板
        "The fabricated device resulted in a PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.", # 20250424文献模板
        "The certified PCE was determined to be {pce}% with JSC of {jsc} mA/cm², VOC of {voc} V, and FF of {ff}%.",# 20250424文献模板
        "A PCE of {pce}% with a VOC of {voc} V, a JSC of {jsc} mA/cm², and an FF of {ff}% was obtained.",  # 20250424文献模板
        "The PSCs demonstrated improved PCE of {pce}% (with FF of {ff}%, VOC of {voc} V, and JSC of {jsc} mA/cm²).", # 20250424文献模板
        "The PSCs demonstrated a champion PCE of {pce}%, with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.", # 20250424文献模板
        "The PCE of the device was increased to {pce}% with an FF of {ff}%, VOC of {voc} V and JSC of {jsc} mA/cm².",# 20250424文献模板
        "The champion PCE of the device can be further improved to {pce}% (VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%).",# 20250424文献模板
        "PSCs with a PCE of {pce}%, a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}% are demonstrated.",# 20250424文献模板
        "A significantly higher JSC of {jsc} mA/cm² is obtained while preserving VOC of {voc} V and FF of {ff}%, resulting in the highest PCE of {pce}% at reverse scan.",# 20250424文献模板
        "The current density-voltage (J-V) characteristics show that the target PSCs delivered a PCE of {pce}%, with an elevated VOC of {voc} V, a JSC of {jsc} mA/cm², and an FF of {ff}%.",# 20250424文献模板
        "The cells showed an increase in VOC to {voc} V, accompanied by a slight increase in FF to {ff}% and JSC to {jsc} mA/cm², resulting in a peak PCE of {pce}%.",# 20250424文献模板
        "The device shows the highest PCE of {pce}% with a VOC of {voc} V, a JSC of {jsc} mA/cm², and an FF of {ff}%.",# 20250424文献模板
        "In contrast, the device achieves a notably enhanced PCE of {pce}%, with a JSC of {jsc} mA/cm², VOC of {voc} V, and FF of {ff}%.", # 20250424文献模板
        "The PSCs exhibited a superior PCE of {pce}% (JSC: {jsc} mA/cm², VOC: {voc} V, FF: {ff}%).",  # 20250424文献模板
        "The PSC device gives the highest PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.", # 20250424文献模板
        "The device achieved an impressive PCE of {pce}% with an open-circuit voltage of {voc} V, short-circuit current density of {jsc} mA/cm², and fill factor of {ff}%.", # 20250424文献模板
        "The champion device achieved a remarkable power conversion efficiency (PCE) of {pce}%, with a VOC of {voc} V, a JSC of {jsc} mA/cm², and a FF of {ff}%, outperforming devices modified with other SAMs.",# 20250424文献模板
        "The PSCs show a champion PCE of {pce}% with VOC of {voc} V, JSC of {jsc} mA/cm² and FF of {ff}%.",  # 20250424文献模板
        "The solar cells showed a drastically enhanced VOC, which led to a maximum efficiency of {pce}% (with FF of {ff}%, JSC of {jsc} mA/cm², and VOC of {voc} V).",# 20250424文献模板
        "The champion device achieves an outstanding PCE of {pce}%, with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%, marking a significant improvement over the control device.",# 20250424文献模板
        "The device achieves a champion PCE of {pce}% with an open-circuit voltage (VOC) of {voc} V, a short-circuit current (JSC) of {jsc} mA/cm², and a fill factor (FF) of {ff}%.",# 20250424文献模板
        "The device displayed a champion PCE of {pce}%, with a VOC of {voc} V, a JSC of {jsc} mA/cm², and an FF of {ff}%.",# 20250424文献模板
        "The PSCs displayed a significantly enhanced PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",# 20250424文献模板
    ]

# intro_segments = [
#     "Based on a systematically tuned set of experimental parameters, this perovskite solar cell {prepared_term}, ultimately achieving a PCE of {pce}%.",
#     "Under carefully optimized conditions, the perovskite device was fabricated, achieving a PCE of {pce}%.",
#     "By refining specific fabrication parameters, a perovskite solar cell {prepared_term}, culminating in a PCE of {pce}%.",
#     "Through deliberate control of solution composition, coating speeds, and thermal treatments, this perovskite cell {prepared_term}, leading to a PCE of {pce}%.",
#     "Using a parameter-driven approach, we have engineered a perovskite solar cell that {prepared_term}, thus realizing a PCE of {pce}%.",
#     "This work arises from meticulous parameter optimization, where a perovskite solar device {prepared_term}, reflecting a PCE of {pce}%.",
#     "Within a framework of controlled experimental inputs, a perovskite cell configuration {prepared_term}, ultimately manifesting a PCE of {pce}%.",
#     "Each step—from solution concentration to annealing—was carefully optimized to {prepared_term} this perovskite solar cell, achieving a PCE of {pce}%.",
#     "Guided by experimental parameters such as spin speeds, antisolvent timing, and annealing profiles, this device {prepared_term}, realizing a PCE of {pce}%.",
#     "Guided by incremental parameter refinements, the perovskite assembly {prepared_term}, achieving a PCE of {pce}%.",
#     "Based on a methodical exploration of fabrication parameters, the perovskite cell {prepared_term}, reaches the PCE of {pce}%.",
#     "By strategically aligning experimental conditions with device architecture, a perovskite solar cell {prepared_term}, demonstrating a PCE of {pce}%.",
#     "Through iterative refinements in substrate preparation, solution concentration, and coating protocols, this perovskite device {prepared_term}, echoing a PCE of {pce}%.",
# ]

# 钙钛矿材料和配方描述（Perovskite Formula Segments, 15条）
perovskite_formula_segments = [
    "A perovskite precursor solution was first prepared using {formula_pvk} at {concentration_pvk} mol/L.",
    "Starting with a {formula_pvk} solution at {concentration_pvk} mol/L, the base solution was formulated to form the core perovskite layer.",
    "With {formula_pvk} at {concentration_pvk} mol/L forming the primary solution, the perovskite precursor was synthesized accordingly.",
    "The core perovskite solution, composed of {formula_pvk} at {concentration_pvk} mol/L, served as the foundational matrix for the solar cell.",
    "By dissolving {formula_pvk} at {concentration_pvk} mol/L as the primary ingredient, the perovskite precursor was effectively prepared.",
    "The perovskite ink, prepared from {formula_pvk} at {concentration_pvk} mol/L, formed the base layer for subsequent fabrication steps.",
    "In formulating the active solution, {formula_pvk} at {concentration_pvk} mol/L was utilized to establish the perovskite layer.",
    "Starting with a {formula_pvk} ({concentration_pvk} mol/L) solution, the perovskite precursor was carefully crafted for optimal performance.",
    "A solution of {formula_pvk} at {concentration_pvk} mol/L provided the foundational matrix for the perovskite layer.",
    "The formulation began with {formula_pvk} at {concentration_pvk} mol/L, establishing the core perovskite solution.",
    "By preparing a base solution of {formula_pvk} at {concentration_pvk} mol/L, the perovskite precursor was ready for further enhancements.",
    "A perovskite precursor featuring {formula_pvk} at {concentration_pvk} mol/L was prepared to initiate the fabrication process.",
    "The process involved first dissolving {formula_pvk} at {concentration_pvk} mol/L to create the primary perovskite solution.",
    "A stable precursor mixture was achieved by taking a {formula_pvk} solution ({concentration_pvk} mol/L) as the base.",
    "Commencing with a {formula_pvk} solution at {concentration_pvk} mol/L, the perovskite precursor was meticulously formulated.",
    "The composition of perovskite is {concentration_pvk} mol/L {formula_pvk}.", # 20250411文献模板
    "The {formula_pvk} ({concentration_pvk} mol/L) perovskite precursor solution was prepared.", # 20250411文献模板
    "The perovskite composition is {formula_pvk}, and the initial stock perovskite solution is {concentration_pvk} mol/L.", # 20250411文献模板
    # "The perovskite precursor is {formula_pvk}.", # 20250424文献模板
    "The composition of the {concentration_pvk} mol/L perovskite film with band gap is {formula_pvk}.", # 20250411文献模板
    "The {concentration_pvk} mol/L perovskite precursor solution with a chemical formula of {formula_pvk}.", # 20250411文献模板
    "The perovskite precursor solutions were prepared by dissolving {concentration_pvk} mol/L {formula_pvk}.", # 20250411文献模板
    "{concentration_pvk} mol/L {formula_pvk} perovskite precursors were prepared.", # 20250411文献模板
    "For the perovskite composition {formula_pvk}, {concentration_pvk} mol/L perovskite precursor solution was prepared.", # 20250411文献模板
    "The {concentration_pvk} mol/L perovskite solution ({formula_pvk}) was prepared, shaken overnight to fully dissolve, and then used to prepare perovskite films.", # 20250411文献模板
    "The perovskite precursor solution ({formula_pvk}) was prepared with a concentration of {concentration_pvk} mol/L in a mixed anhydrous solvent of DMF/DMSO (4/1, v/v).", # 20250411文献模板
    "The perovskite ({formula_pvk}) solution was prepared with a concentration of {concentration_pvk} mol/L in mixed solvent of DMF and DMSO.", # 20250411文献模板
    "Then, perovskite precursor solution ({concentration_pvk} mol/L) was prepared at the stoichiometric ratio of {formula_pvk}.", # 20250411文献模板
    "A {concentration_pvk} mol/L perovskite precursor solution was constructed by mixing FAI, PbI2, methylammonium iodide and caesium iodide in DMF: DMSO mixed solvent with the chemical formula of {formula_pvk}.",  # 20250424文献模板
    "For the inorganic perovskite layers, {concentration_pvk} mol/L {formula_pvk} inorganic perovskite precursor solution was prepared in DMSO solvent.",  # 20250424文献模板
    # "The perovskite precursor solution was prepared with a concentration of {concentration_pvk} mol/L using PbI2 and MAI dissolved in a mixed DMF/DMSO solvent.",  # 20250424文献模板
    "The perovskite ({formula_pvk}) precursor solution was prepared with a concentration of {concentration_pvk} mol/L in a mixed solvent of DMF and DMSO.",  # 20250424文献模板
    "The mixed perovskite ({formula_pvk}) precursor solution was prepared with a total concentration of {concentration_pvk} mol/L in DMF/DMSO co-solvent.",  # 20250424文献模板
    "The perovskite precursor solution was prepared based on the perovskite composition of {formula_pvk} in anhydrous DMF solvent (total concentration of {concentration_pvk} mol/L).",  # 20250424文献模板
    "The perovskite precursor solution ({concentration_pvk} mol/L) was prepared in a solvent mixture of DMF and DMSO according to the formula of {formula_pvk}.",  # 20250424文献模板
    "The perovskite solution ({concentration_pvk} mol/L) was made according to the composition of {formula_pvk} in a mixed solvent of DMF/DMSO.",  # 20250424文献模板
    "The perovskite precursor solution ({formula_pvk}) was prepared with a concentration of {concentration_pvk} mol/L in a mixed anhydrous solvent of DMF/DMSO (5/1, v/v).",  # 20250424文献模板
    "The perovskite ({formula_pvk}) solution was prepared with a concentration of {concentration_pvk} mol/L in mixed solvent of DMF and DMSO.",  # 20250424文献模板
    "The {concentration_pvk} mol/L perovskite solution ({formula_pvk}) was prepared, shaken overnight to fully dissolve, and then used to prepare perovskite films.",  # 20250424文献模板
    "For the perovskite composition {formula_pvk}, {concentration_pvk} mol/L perovskite precursor solution was prepared.",  # 20250424文献模板
    "The precursor solutions for all {formula_pvk} films were prepared by dissolving equimolar concentrations ({concentration_pvk} mol/L).",  # 20250424文献模板
    "The perovskite precursor solution ({concentration_pvk} mol/L, {formula_pvk}) was prepared.",  # 20250424文献模板
    "{concentration_pvk} mol/L perovskite precursor solutions were prepared with the chemical formula of {formula_pvk}.",  # 20250424文献模板
    "For the perovskite film, {concentration_pvk} mol/L precursor solution was prepared according to the chemical formula of {formula_pvk}.",  # 20250424文献模板
    "The {formula_pvk} precursor solution ({concentration_pvk} mol/L) was prepared in the mixed solvent of DMF and DMSO.",  # 20250424文献模板
    "The perovskite precursor solution ({concentration_pvk} mol/L) was prepared in mixed solvents of DMF and DMSO according to chemical formula of {formula_pvk}.",  # 20250424文献模板
    "The perovskite precursor solution ({concentration_pvk} mol/L) composed of a formula of {formula_pvk}.",  # 20250424文献模板
    "The perovskite solution ({concentration_pvk} mol/L) was prepared according to chemical formula of {formula_pvk}.",  # 20250424文献模板
    "The {formula_pvk} perovskite film was prepared with a concentration of {concentration_pvk} mol/L.",  # 20250424文献模板
    "The {concentration_pvk} mol/L perovskite precursor solution with a chemical formula of {formula_pvk} was prepared.",  # 20250424文献模板
    "The perovskite precursor solutions were prepared using {concentration_pvk} mol/L {formula_pvk}.",  # 20250424文献模板
    "{concentration_pvk} mol/L {formula_pvk} perovskite precursors were prepared.",  # 20250424文献模板
    "For the preparation of perovskite precursor solution, {concentration_pvk} mol/L {formula_pvk} perovskite precursor was prepared in DMF:DMSO (4:1 volume ratio, v:v) mixed solvent.",  # 20250424文献模板
    "Perovskite precursor solution ({concentration_pvk} mol/L) was prepared based on the stoichiometric ratio of {formula_pvk}.",  # 20250424文献模板
    "The {formula_pvk} perovskite precursor ({concentration_pvk} mol/L) was spin-coated onto the substrate.",  # 20250424文献模板
    "The {formula_pvk} ({concentration_pvk} mol/L) perovskite precursor solution was prepared.",  # 20250424文献模板
    "{formula_pvk} was prepared at a concentration of {concentration_pvk} mol/L.",  # 20250424文献模板
    "The perovskite composition was {formula_pvk}, and the initial stock perovskite solution was {concentration_pvk} mol/L.",  # 20250424文献模板
    "The composition of perovskite is {concentration_pvk} mol/L {formula_pvk}.",  # 20250424文献模板
    "The perovskite solution, {concentration_pvk} mol/L {formula_pvk} was prepared.",  # 20250424文献模板
    "The composition of the {concentration_pvk} mol/L perovskite film is {formula_pvk}.",  # 20250424文献模板
    "The perovskite composition of {formula_pvk} was prepared with a concentration of {concentration_pvk} mol/L.",  # 20250424文献模板
    "The perovskite precursor solution with a molar concentration of {concentration_pvk} mol/L was prepared according to the formula of {formula_pvk}.",  # 20250424文献模板
    "The composition of the {concentration_pvk} mol/L perovskite film is {formula_pvk}.",  # 20250424文献模板
    "A {concentration_pvk} mol/L {formula_pvk} precursor solution was similarly prepared using a mixture of DMF and DMSO.",  # 20250424文献模板
    "{concentration_pvk} mol/L perovskite precursor solution with the composition of {formula_pvk} was prepared.",  # 20250424文献模板
    "For the {formula_pvk}, {concentration_pvk} mol/L perovskite precursor solution was prepared.",  # 20250424文献模板
    "For perovskite film, the solution concentration of {formula_pvk} was {concentration_pvk} mol/L.",  # 20250424文献模板
]

sam_formula_segments_single = [
    "The SAM material {formula_sam1} ({concentration_sam1} mg/mL) was subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM was carried out to improve layer formation and refine the film’s interfacial structure.",
    "SAM material {formula_sam1} ({concentration_sam1} mg/mL) was added to the perovskite solution to fine-tune the interface and stabilize the perovskite layer.",
    "The SAM material {formula_sam1} ({concentration_sam1} mg/mL) was introduced to enhance interfacial properties and improve device performance.",
    "Controlled addition of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM was performed to stabilize the perovskite layer and engineer a more robust interface.",
    "SAM material {formula_sam1} ({concentration_sam1} mg/mL) was added to influence crystal growth at the interface and optimize surface passivation.",
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM improved morphological and electronic interfaces.",
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM was performed to optimize surface passivation and ensure improved interface quality.",
    "Careful addition of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM ensured improved interface quality.",
    "Incorporating {formula_sam1} ({concentration_sam1} mg/mL) as a SAM was critical to adjust interfacial energy levels and refine the perovskite interface.",
    "Adding {formula_sam1} ({concentration_sam1} mg/mL) as a SAM improved the charge extraction at the interface.",
    "A SAM solution, consisting of {formula_sam1} ({concentration_sam1} mg/mL), was added to facilitate a stable perovskite interface.",
    "Integrating {formula_sam1} ({concentration_sam1} mg/mL) as a SAM tailored the interfacial environment, contributing to a more uniform and well-ordered perovskite interface.",
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM improved interface quality and subsequently device performance.",
    "A SAM consisting of {formula_sam1} ({concentration_sam1} mg/mL) was incorporated to achieve a more uniform and well-ordered perovskite interface.",
    "The SAM consisting of {formula_sam1} ({concentration_sam1} mg/mL) was subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM enhanced interface layer formation and refined the film’s interfacial structure.",
    "The sample of {formula_sam1} was fabricated by spin coating the {formula_sam1} solution with a concentration of {concentration_sam1} mg/mL.",  # 20250411文献模板
    "For the SAM solution, {formula_sam1} ({concentration_sam1} mg/mL) was added to the previous solution.",  # 20250411文献模板
    "The hole transport layer (HTL) was fabricated using the SAM solution of {formula_sam1}. The {formula_sam1} concentration is {concentration_sam1} mg/mL.", # 20250411文献模板
    "The {formula_sam1} solution was prepared with a concentration of {concentration_sam1} mg/mL.", # 20250411文献模板
    "A SAM solution ({concentration_sam1} mg/mL {formula_sam1}) was applied to the FTO glass substrates by spin-coating.", # 20250411文献模板
    "{concentration_sam1} mg/mL of {formula_sam1} was added.", # 20250411文献模板
    "A SAM solution consisting of {formula_sam1} ({concentration_sam1} mg/mL) in ethanol was prepared.", # 20250411文献模板
    "The optimal SAM was prepared by using {formula_sam1} ({concentration_sam1} mg/mL)." # 20250411文献模板
    "The sample of {formula_sam1} was fabricated with a concentration of {concentration_sam1} mg/mL.",  # 20250424文献模板
    "Different concentrations of {formula_sam1} were added into the perovskite precursor solution for modification.",  # 20250424文献模板
    "The {formula_sam1} solution was prepared with a concentration of {concentration_sam1} mg/mL.",  # 20250424文献模板
]

# SAM材料和配方描述（SAM Formula Segments, 15条）- 双SAM
sam_formula_segments_dual = [
    "Two SAM materials of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were carried out to improve layer formation and refine the film’s interfacial structure.",
    "SAM materials of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were added to the perovskite solution to fine-tune the interface and stabilize the perovskite layer.",
    "A combination of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were introduced to enhance interfacial properties and improve device performance.",
    "Controlled addition of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were performed to stabilize the perovskite layer and engineer a more robust interface.",
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were added to influence crystal growth at the interface and optimize surface passivation.",
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs improved morphological and electronic interfaces.",
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were performed to optimize surface passivation and ensure improved interface quality.",
    "Careful addition of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs ensured an improved interface quality.",
    "Incorporating {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were critical to adjust interfacial energy levels and refine perovskite interface.",
    "Adding {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs improved the charge extraction at the interface.",
    "SAMs mixture, consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL), were added to facilitate stable perovskite interface.",
    "Integrating {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs tailored the interfacial environment, contributing to a more uniform and well-ordered perovskite interface.",
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs enabled the improvement in interface quality, and subsequently device performance.",
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were incorporated to achieve a more uniform and well-ordered perovskite interface.",
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs enabled the improvement in interface layer formation, further refining the film’s interfacial structure.",
    "While the sample of {formula_sam1} and {formula_sam2} were fabricated by spin coating {formula_sam1} and {formula_sam2} solution with concentration of {concentration_sam1} mg/mL and {concentration_sam2} mg/mL.",  # 20250411文献模板
    "For the SAM solution, {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were added to the previous solution."  # 20250411文献模板
    "The hole transport layer (HTL) was fabricated by using the mixed SAM solution of {formula_sam1} and {formula_sam2}. The {formula_sam1} concentration is {concentration_sam1} mg/mL and {formula_sam2} concentration is {concentration_sam2} mg/mL.", # 20250411文献模板
    "The {formula_sam1} and {formula_sam2} solution were prepared with a concentration of {concentration_sam1} mg/mL and {concentration_sam2} mg/mL.", # 20250411文献模板
    "A mixed SAMs solution ({concentration_sam1} mg/mL {formula_sam2} and {concentration_sam2} mg/mL) were applied to the FTO glass substrates by spin-coating.", # 20250411文献模板
    "{concentration_sam1} mg/mL of {formula_sam1} and {concentration_sam2} mg/mL of {formula_sam2} were added.", # 20250411文献模板
    "Mixed SAMs solution, consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) in ethanol were prepared.", # 20250411文献模板
    "The optimal hybrid SAMs were prepared by mixing {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL).", # 20250411文献模板
    "The {formula_sam1} concentration is {concentration_sam1} mg/mL and {formula_sam2} concentration is {concentration_sam2} mg/mL.",  # 20250424文献模板
    "The {formula_sam1} concentration is {concentration_sam1} mg/mL and {formula_sam2} concentration is {concentration_sam2} mg/mL.",  # 20250424文献模板
    ]

sam_formula_segments_triple = [
    "Three SAM materials of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were carried out to improve layer formation and refine the film’s interfacial structure.",
    "SAM materials of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were added to the perovskite solution to fine-tune the interface and stabilize the perovskite layer.",
    "A combination of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were introduced to enhance interfacial properties and improve device performance.",
    "Controlled addition of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were performed to stabilize the perovskite layer and engineer a more robust interface.",
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were added to influence crystal growth at the interface and optimize surface passivation.",
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs improved morphological and electronic interfaces.",
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were performed to optimize surface passivation and ensure improved interface quality.",
    "Careful addition of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs ensured an improved interface quality.",
    "Incorporating {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were critical to adjust interfacial energy levels and refine perovskite interface.",
    "Adding {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs improved the charge extraction at the interface.",
    "SAMs mixture, consisting of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL), were added to facilitate stable perovskite interface.",
    "Integrating {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs tailored the interfacial environment, contributing to a more uniform and well-ordered perovskite interface.",
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs enabled the improvement in interface quality, and subsequently device performance.",
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were incorporated to achieve a more uniform and well-ordered perovskite interface.",
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs enabled the improvement in interface layer formation, further refining the film’s interfacial structure.",
    "While the sample of {formula_sam1}, {formula_sam2} and {formula_sam3} were fabricated by spin coating {formula_sam1}, {formula_sam2} and {formula_sam3} solution with concentration of {concentration_sam1} mg/mL, {concentration_sam2} mg/mL and {concentration_sam3} mg/mL.",
    "For the SAM solution, {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were added to the previous solution.",

]

additive_formula_segments_single = [
"{formula_add1} ({concentration_add1} mg/mL) was incorporated as an additive.",
    "To enhance device performance, {formula_add1} ({concentration_add1} mg/mL) was added to the perovskite solution as an additive.",
    "We add {formula_add1} ({concentration_add1} mg/mL).",
    "{formula_add1} (with {concentration_add1} mg/mL) additive was incorporated.",
    "We then add {formula_add1} ({concentration_add1} mg/mL) as an additive.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) was then completed.",
    "The controlled addition of {formula_add1} ({concentration_add1} mg/mL) additive was implemented.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) as an additive was carefully prepared.",
    "The presence of {formula_add1} ({concentration_add1} mg/mL) was crucial.",
    "The incorporation of {formula_add1} ({concentration_add1} mg/mL) additive was ensured.",
    "Add {formula_add1} ({concentration_add1} mg/mL) as an additive was essential for stabilizing the perovskite structure.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) enabled the achievement of smoother film surfaces.",
    "To enhance the mechanical properties of the perovskite layer, {formula_add1} ({concentration_add1} mg/mL) was utilized as an additive.",
    "The inclusion of {formula_add1} ({concentration_add1} mg/mL) additive enhanced device longevity.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) was instrumental in fine-tuning the perovskite film's optical properties.",
    "{formula_add1} was incorporated into the solution as an additive at a molar percentage of {concentration_add1} mg/mL.",
    "During solar cell device fabrication, {formula_add1} ({concentration_add1} mg/mL) was added to the precursor solution.",
    "The corresponding additive {formula_add1} was added to the precursor at a molar concentration of {concentration_add1} mg/mL.",
    "The perovskite precursor solution was prepared by mixing {concentration_add1} mg/mL of {formula_add1} additive in the solvent.",
    "To achieve the desired secondary growth solution, {formula_add1} ({concentration_add1} mg/mL) was dissolved in IPA solvent.",
    "To fabricate high-quality perovskite films, {formula_add1} ({concentration_add1} mg/mL) was added to the perovskite precursor solution.",
    "{formula_add1} ({concentration_add1} mg/mL) was added into the precursor solution as an additive.",
    "The perovskite solution was prepared with {formula_add1} in the molar ratio of {concentration_add1} mg/mL, dissolved in the prepared solution.",
    "An equal amount of {formula_add1} ({concentration_add1} mg/mL) was dissolved in dimethylformamide (DMF) and dimethyl sulfoxide (DMSO) with a 4:1 volume ratio.",
    "An equal amount of {formula_add1} ({concentration_add1} mg/mL) was dissolved in DMF and DMSO with an 8:1 volume ratio.",
    "For the modified solution, {formula_add1} ({concentration_add1} mg/mL) was added to the previous solution.",  # 20250411文献模板
    "To prepare the precursor solution with {formula_add1} ({concentration_add1} mg/mL), the additive was added to the precursor solution.",  # 20250411文献模板
    "And chlorinated {formula_add1} under {concentration_add1} mg/mL concentration in the perovskite precursor solution.",  # 20250411文献模板
    "To prepare the precursor solution with {formula_add1} ({concentration_add1} mg/mL), the additive was added to the precursor solution.",  # 20250411文献模板
    "For the additive-treated cells, {formula_add1} ({concentration_add1} mg/mL) was added into the perovskite precursor solution."  # 20250411文献模板
    "{concentration_add1} mg/mL {formula_add1} was then added as additive into the precursor solution.",  # 20250424文献模板
    "{formula_add1} additive was added into the precursor solution at a concentration of {concentration_add1} mg/mL.",  # 20250424文献模板
    "{formula_add1} was added into the perovskite solution as additive with a concentration of {concentration_add1} mg/mL.",  # 20250424文献模板
    "The optimum amount of {formula_add1} added into the precursor solution was {concentration_add1} mg/mL.",  # 20250424文献模板
    "{formula_add1} with concentration {concentration_add1} mg/mL were added into the perovskite solution.",  # 20250424文献模板
    "For the {formula_add1} additive system, the molar ratios of perovskite to {formula_add1} were 15%, 30%, 60%, and 100%.",  # 20250424文献模板
    "Then {concentration_add1} mg/mL {formula_add1} was added to the perovskite precursor solution and stirred for 2 h.",  # 20250424文献模板
    "For the target perovskite, {concentration_add1} mg/mL {formula_add1} was added to the precursor solution, and it was ensured that it is well mixed with the precursor.",  # 20250424文献模板
    "{concentration_add1} mg/mL {formula_add1} was added in the solution to improve the film morphology.",  # 20250424文献模板
    "The piperidinium salt {formula_add1} was dissolved in the perovskite solution obtained with the molar ratio {concentration_add1} mg/mL.",  # 20250424文献模板
    "{concentration_add1} mg/mL {formula_add1} was added to the perovskite precursor solution and stirred for 2 h.",  # 20250424文献模板
    "{concentration_add1} mg/mL {formula_add1} was added into the mixed perovskite solution.",  # 20250424文献模板
    "For the modified solution, {concentration_add1} mg/mL {formula_add1} was added to the precursor solution.",  # 20250424文献模板
    "The target precursor solution was prepared with {formula_add1} ({concentration_add1} mg/mL).",  # 20250424文献模板
    "{concentration_add1} mg/mL of {formula_add1} was added.",  # 20250424文献模板
    "{formula_add1} ({concentration_add1} mg/mL) was added into the perovskite precursor solution.",  # 20250424文献模板
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL), the additive was added to the precursor solution." , # 20250424文献模板

    ]

# 添加剂材料和配方描述（Additive Formula Segments, 15条）- 双添加剂
additive_formula_segments_dual = [
"{formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were incorporated as additives.",
    "To enhance device performance, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added to the perovskite solution as additives.",
    "We add {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL).",
    "{formula_add1} (with {concentration_add1} mg/mL) and {formula_add2} (with {concentration_add2} mg/mL) additives were incorporated.",
    "We then add {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) as additives.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were then completed.",
    "The controlled addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) additives were implemented.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) as additives were carefully prepared.",
    "The presence of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were crucial.",
    "The incorporation of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) additives were ensured.",
    "Add {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) as additiveswere essential for stabilizing the perovskite structure.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) enabled the achievement of smoother film surfaces.",
    "To enhance the mechanical properties of the perovskite layer, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were utilized as additives.",
    "The inclusion of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) additives enhanced device longevity.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were instrumental in fine-tuning the perovskite film's optical properties.",
    "{formula_add1} and {formula_add2} were incorporated into the solution as additives at molar percentages of {concentration_add1} mg/mL and {concentration_add2} mg/mL, respectively.",
    "During solar cell device fabrication, {formula_add1} ({concentration_add1} mg/mL), and {formula_add2} ({concentration_add2} mg/mL) were added to the precursor solution.",
    "The corresponding additives ({formula_add1}, {formula_add2}) were added to the precursors at molar concentration of {concentration_add1} mg/mL and {concentration_add2} mg/mL, respectively.",
    "The perovskite precursor solution is prepared by mixing {concentration_add1} mg/mL of {formula_add1}, and {concentration_add2} mg/mL of {formula_add2} additive in the solvent.",
    "To achieve the desired secondary growth solution, {formula_add1} ({concentration_add1} mg/mL) and/or {formula_add2} ({concentration_add2} mg/mL) were dissolved in IPA solvent.",
    "To fabricate high-quality perovskite films, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added to the perovskite precursor solution.",
    "{formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added into both precursor solutions as additives.",
    "The perovskite solution were a mixture of {formula_add1} and {formula_add2} in the molar ratio of {concentration_add1} mg/mL and {concentration_add2} mg/mL, respectively, dissolved in the prepared solution.",
    "Equal amounts of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were dissolved in dimethylformamide (DMF) and dimethyl sulfoxide (DMSO) with a 4:1 volume ratio.",
    "Equal amounts of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were dissolved in DMF and DMSO with an 8:1 volume ratio.",
    "For the modified solution, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added to the previous solution.",  # 20250411文献模板
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL), the additive were added to the precursor solution.",  # 20250411文献模板
    "And chlorinated {formula_add1} and {formula_add2} under {concentration_add1} mg/mL and {concentration_add2} mg/mL concentrations in perovskite precursor solution.",  # 20250411文献模板
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL), the additives were added to the precursor solution.", # 20250411文献模板
    "For the additives treated cells, the {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added into the perovskite precursor solution.", # 20250411文献模板
    "In addition, {formula_add1} ({concentration_add1} mg/mL), and {formula_add2} ({concentration_add2} mg/mL, 520 mg mL-1 in acetonitrile) were incorporated to improve its conductivity.",  # 20250424文献模板
    "Then, around {concentration_add1} mg/mL of {formula_add1} and {concentration_add2} mg/mL of {formula_add2} were also added into the mixed perovskite solution.",  # 20250424文献模板
    "For the additives treated cells, the {formula_add1} ({concentration_add1} mg/mL) or {formula_add2} ({concentration_add2} mg/mL) were added into the perovskite precursor solution.",  # 20250424文献模板

    ]

additive_formula_segments_triple = [
"{formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were incorporated as additives.",
    "To enhance device performance, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added to the perovskite solution as additives.",
    "We add {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL).",
    "{formula_add1} (with {concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) additives were incorporated.",
    "We then add {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) as additives.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were then completed.",
    "The controlled addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) additives were implemented.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) as additives were carefully prepared.",
    "The presence of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were crucial.",
    "The incorporation of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) additives were ensured.",
    "Add {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) as additives were essential for stabilizing the perovskite structure.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) enabled the achievement of smoother film surfaces.",
    "To enhance the mechanical properties of the perovskite layer, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were utilized as additives.",
    "The inclusion of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) additives enhanced device longevity.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were instrumental in fine-tuning the perovskite film's optical properties.",
    "{formula_add1}, {formula_add2} and {formula_add3} were incorporated into the solution as additives at molar percentages of {concentration_add1} mg/mL, {concentration_add2} mg/mL and {concentration_add3} mg/mL, respectively.",
    "During solar cell device fabrication, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added to the precursor solution.",
    "The corresponding additives ({formula_add1}, {formula_add2}, {formula_add3}) were added to the precursors at molar concentration of {concentration_add1} mg/mL, {concentration_add2} mg/mL and {concentration_add3} mg/mL, respectively.",
    "The perovskite precursor solution is prepared by mixing {concentration_add1} mg/mL of {formula_add1}, {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) additive in the solvent.",
    "To achieve the desired secondary growth solution, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were dissolved in IPA solvent.",
    "To fabricate high-quality perovskite films, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added to the perovskite precursor solution.",
    "{formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added into both precursor solutions as additives.",
    "The perovskite solution were a mixture of {formula_add1}, {formula_add2} and {formula_add3} in the molar ratio of {concentration_add1} mg/mL, {concentration_add2} mg/mL and {concentration_add3} mg/mL, respectively, dissolved in the prepared solution.",
    "Equal amounts of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were dissolved in dimethylformamide (DMF) and dimethyl sulfoxide (DMSO) with a 4:1 volume ratio.",
    "Equal amounts of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were dissolved in DMF and DMSO with an 8:1 volume ratio.",
    "For the modified solution, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added to the previous solution.",  # 20250411文献模板
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL), the additive were added to the precursor solution.",  # 20250411文献模板
    "And chlorinated {formula_add1}, {formula_add2} and {formula_add3} under {concentration_add1} mg/mL, {concentration_add2} mg/mL and {concentration_add3} mg/mL concentrations in perovskite precursor solution." , # 20250411文献模板

    ]

# 工艺步骤描述（Process Segments, 15条）
process_segments = [
"Spin-coating was conducted in two stages: {spin1_speed} rpm for {spin1_time} s, then {spin2_speed} rpm for {spin2_time} s.",
    "A sequential spin-coating procedure was employed, first at {spin1_speed} rpm for {spin1_time} s, followed by {spin2_speed} rpm for {spin2_time} s.",
    "The deposition process involved a two-step spin sequence ({spin1_speed} rpm/{spin1_time} s and {spin2_speed} rpm/{spin2_time} s) to achieve a controlled film thickness.",
    "A well-optimized dual-stage spin routine ({spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s) was chosen to facilitate smooth and homogeneous layer formation.",
    "The layer was cast via a two-step spin approach: initially at {spin1_speed} rpm for {spin1_time} s, then accelerated to {spin2_speed} rpm for {spin2_time} s.",
    "To ensure uniform film deposition, we utilized a double spin stage, starting at {spin1_speed} rpm ({spin1_time} s) and subsequently {spin2_speed} rpm ({spin2_time} s).",
    "The film was deposited under controlled conditions, involving an initial spin of {spin1_speed} rpm ({spin1_time} s) followed by a second spin at {spin2_speed} rpm ({spin2_time} s).",
    "A two-tier spin-coating strategy ({spin1_speed} rpm/{spin1_time} s and {spin2_speed} rpm/{spin2_time} s) produced a uniform and defect-minimized perovskite layer.",
    "Employing a staged spin protocol, the film underwent {spin1_speed} rpm for {spin1_time} s, then {spin2_speed} rpm for {spin2_time} s, enhancing film morphology.",
    "The chosen spin-coating regimen first applied {spin1_speed} rpm for {spin1_time} s, then {spin2_speed} rpm for {spin2_time} s, ensuring layer consistency.",
    "A meticulously timed spin procedure included {spin1_speed} rpm for {spin1_time} s, succeeded by {spin2_speed} rpm for {spin2_time} s to refine crystal growth.",
    "The film formation relied on a two-phase spin cycle: {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, optimizing thickness uniformity.",
    "Implementing a stepwise spin scheme, the layer was first spun at {spin1_speed} rpm ({spin1_time} s) and then at {spin2_speed} rpm ({spin2_time} s), improving surface coverage.",
    "A careful spin regime was adopted: an initial slow spin at {spin1_speed} rpm ({spin1_time} s) to distribute the solution, followed by {spin2_speed} rpm ({spin2_time} s) for crystallization control.",
    "To establish a stable perovskite film, the substrate was spun at {spin1_speed} rpm for {spin1_time} s, then at {spin2_speed} rpm for {spin2_time} s, ensuring even layer formation.",
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  # 20250411文献模板
    "The perovskite precursor was spin-coated onto substrates with two stages program at {spin1_speed} rpm for {spin1_time} s, and {spin2_speed} rpm for {spin2_time} s, respectively.", # 20250411文献模板
    "Specifically, the perovskite precursor solution was first spinning at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "The perovskite precursor was spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "For perovskite films fabrication, the perovskite precursor was spin-coated on the as prepared substrates at {spin1_speed} rpm for {spin1_time} s, subsequently at {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "The perovskite precursor solutions were spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "Then the filtered perovskite precursor was spin-coated on substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "The perovskite film is deposited by spin-coating with {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "Spread perovskite solution spin-coated in two steps, namely, {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "The perovskite precursor solution was deposited on the substrate via a two-step spin coating process; first, the solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "The precursor solution was spin-coated onto the substrate surface at {spin1_speed} rpm for {spin1_time} s, then accelerated to {spin2_speed} rpm and maintained at this speed for {spin2_time} s.", # 20250411文献模板
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "For the perovskite deposition process, the perovskite films were deposited using a two-step spin-coating process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s  and {spin2_speed} rpm for {spin2_time} s, respectively.", # 20250411文献模板
    "The perovskite solution was spin coated on the substrates at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s, respectively.", # 20250411文献模板
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "The precursor solution was spin-coated in a two-step process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.", # 20250411文献模板
    "The perovskite precursor solutions were spin-coated on substrate at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.", # 20250411文献模板
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and then, {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite precursor solution was then spin-coated at {spin1_speed} rpm for {spin1_time} s followed by an additional spin at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The prepared precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s onto the substrate.",  # 20250424文献模板
    "The precursor solution was spin-coated on the substrate at {spin1_speed} rpm for {spin1_time} s and then, {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The precursor solution was deposited on the substrate and spin-coated with a two-step spin-coating procedure: {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite layer was deposited via a two-step spin-coating procedure with {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite solution was spin coated on the substrate at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s, respectively.",  # 20250424文献模板
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "For the perovskite films, the spin-coated process was divided by a consecutive two-step process, the spin rate of the first step is {spin1_speed} rpm for {spin1_time} s, and the spin rate of the second step is {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite layer was spin-coated with a two-step recipe, first at {spin1_speed} rpm for {spin1_time} s followed by {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite solution was deposited on substrate by two consecutive spin-coating steps of {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  # 20250424文献模板
    "The perovskite solutions were spin-coated onto substrate at {spin1_speed} rpm for {spin1_time} s, subsequently at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The spin coating procedure was done in ambient air by a consecutive two-step spin-coating process at first {spin1_speed} rpm for {spin1_time} s and second {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite solution was deposited on the substrate and spun cast at {spin1_speed} rpm for {spin1_time} s followed by {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "For the perovskite film fabrication, the substrate was spun at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "Then, the prepared precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s onto the ITO substrate.",  # 20250424文献模板
    "The perovskite film was deposited by spin-coating onto the substrate using two-step spin-coating process, first at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The precursor solution was deposited on the substrate and spun cast at {spin1_speed} rpm for {spin1_time} s, followed by {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite was deposited via a two-step spin-coating procedure with {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite precursor solution was then spin-coated onto a substrate at {spin1_speed} rpm for {spin1_time} s followed by an additional spin at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "Afterwards, the perovskite precursor solution was deposited on the substrate via a two-step spin coating process; first, the solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The precursor solution was spin-coated onto the substrate surface at {spin1_speed} rpm for {spin1_time} s, then accelerated to {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "For the perovskite deposition process, the perovskite solutions were deposited using a two-step spin-coating process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s (acceleration rate 500 rpm/s) and {spin2_speed} rpm for {spin2_time} s (acceleration rate 1000 rpm/s), respectively.",  # 20250424文献模板
    "The as prepared perovskite precursor was spin-coated onto the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  # 20250424文献模板
    "The precursor solution was spin-coated in a two-step process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  # 20250424文献模板
    "The perovskite precursor solutions were spin-coated on substrate at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "Specifically, the perovskite precursor solution was first deposited at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  # 20250424文献模板
    "The perovskite precursor solution was dripped onto substrate, and a two-step spin-coating procedure was applied. The first step was carried out at {spin1_speed} rpm, followed by {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite is deposited via a two-step spin-coating procedure, first at {spin1_speed} rpm for {spin1_time} s and finally at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite precursor was spin-coated onto the substrates with two stages program at {spin1_speed} rpm for {spin1_time} s, and {spin2_speed} rpm for {spin2_time} s, respectively.",  # 20250424文献模板
    "The precursor solution was spin-coated on substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The prepared precursor solution was spin coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s onto the substrate.",  # 20250424文献模板
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  # 20250424文献模板
    "For perovskite films fabrication, the perovskite precursor was spin-coated on the as prepared substrates at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite precursor solutions were spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite film was deposited by spin-coating at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "Perovskite solution was deposited in two steps, first at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "For the perovskite layer, the prepared perovskite solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "The perovskite film was deposited by spin-coating at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "Then, the perovskite precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板
    "For the fabrication of perovskite films, the perovskite solutions were spin-coated onto the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  # 20250424文献模板

    ]

# 抗溶剂滴加（Antisolvent Segments, 15条）
antisolvent_segments = [
    "During the second spin-coating step, {antisolvent_volume} µL of antisolvent was introduced at last {antisolvent_timing} s.",
    "At last ({antisolvent_timing} s) during the second stage, {antisolvent_volume} µL of antisolvent was gently dispensed to improve crystallization.",
    "To promote better film morphology, {antisolvent_volume} µL of antisolvent was added at last {antisolvent_timing} s in the latter spin-coating step.",
    "A timed antisolvent drop ({antisolvent_volume} µL at last {antisolvent_timing} s) enhanced the perovskite crystallization kinetics.",
    "Precisely at last {antisolvent_timing} s in the second spin sequence, {antisolvent_volume} µL of antisolvent was introduced, aiding grain formation.",
    "The controlled addition of {antisolvent_volume} µL antisolvent at last {antisolvent_timing} s facilitated uniform crystal nucleation.",
    "By delivering {antisolvent_volume} µL of antisolvent at last {antisolvent_timing} s, the final film exhibited improved surface coverage and reduced pinholes.",
    "An antisolvent injection of {antisolvent_volume} µL at last {antisolvent_timing} s stabilized the intermediate phase, leading to enhanced film quality.",
    "The crystallization process was refined by injecting {antisolvent_volume} µL of antisolvent at last {antisolvent_timing} s during spin-coating.",
    "Integrating {antisolvent_volume} µL of antisolvent at last {antisolvent_timing} s prompted more uniform perovskite grain growth.",
    "The carefully timed introduction of {antisolvent_volume} µL antisolvent at last {antisolvent_timing} s played a crucial role in controlling film morphology.",
    "A strategic antisolvent application ({antisolvent_volume} µL at last {antisolvent_timing} s) resulted in well-defined crystal domains.",
    "At last {antisolvent_timing} s, the injection of {antisolvent_volume} µL antisolvent aided in reducing defect density within the perovskite layer.",
    "A gentle antisolvent drop of {antisolvent_volume} µL at last {antisolvent_timing} s guided the perovskite crystals into a more ideal arrangement.",
    "The addition of {antisolvent_volume} µL antisolvent at last {antisolvent_timing} s proved instrumental in achieving uniform film thickness and grain distribution.",
    "At the {antisolvent_timing} s of the second step, {antisolvent_volume} µL antisolvent was dropped.", # 20250411文献模板
    "During the second step, antisolvent CB ({antisolvent_volume} µL) was dropped at the middle of the spinning substrate {antisolvent_timing} s prior to the end of the spinning.", # 20250411文献模板
    "At the {antisolvent_timing} s of spinning, {antisolvent_volume} µL of CB was dripped onto the substrate centre.", # 20250411文献模板
    "After {antisolvent_timing} s into the second stage, {antisolvent_volume} µL CB antisolvent was dropped on top of the spinning substrates.", # 20250411文献模板
    "During spin-coating process, {antisolvent_volume} µL of CB was dropped on the perovskite at {antisolvent_timing} s, prior to the end of the second procedure.", # 20250411文献模板
    "During which CB ({antisolvent_volume} µL) was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.", # 20250411文献模板
    "{antisolvent_volume} µL CB was dropped on the perovskite film at {antisolvent_timing} s before the end of the program.", # 20250411文献模板
    "{antisolvent_volume} µL of CB as antisolvent was dripped onto the substrate quickly at {antisolvent_timing} s during the second spinning step.", # 20250411文献模板
    "At the last {antisolvent_timing} s, {antisolvent_volume} µL of CB solution was dropped on the perovskite.", # 20250411文献模板
    "Then, with {antisolvent_timing} s of spin time remaining, CB ({antisolvent_volume} µL) was dispensed onto the middle of the substrate.", # 20250411文献模板
    "{antisolvent_volume} µL of CB was dripped onto the substrate during spinning.", # 20250411文献模板
    "At {antisolvent_timing} s before the end of the spin-coating procedure, {antisolvent_volume} µL CB was dropped onto the substrates.", # 20250411文献模板
    "At the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL CB was dropped as antisolvent.", # 20250411文献模板
    "CB ({antisolvent_volume} µL) was dropped on the film at {antisolvent_timing} s before the end of the spinning.", # 20250411文献模板
    "A total of {antisolvent_volume} µL of CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.", # 20250411文献模板
    "{antisolvent_volume} µL CB as antisolvent was dropped {antisolvent_timing} s before the end of the spin-coating procedure.", # 20250411文献模板
    "In the last {antisolvent_timing} s of the second step, the anti-solvent ({antisolvent_volume} µL of CB) was dropped in the center at a constant rate", # 20250411文献模板
    "During the second step, {antisolvent_volume} µL of CB was dropped on the spinning substrate {antisolvent_timing} s before the end of the process.", # 20250411文献模板
    "{antisolvent_volume} µL of CB was quickly poured to extract the mixed solvents at the last of {antisolvent_timing} s.", # 20250411文献模板
    "During the second spin coating step, {antisolvent_volume} µL CB was dripped onto the perovskite film at {antisolvent_timing} s before ending the program.", # 20250411文献模板
    "In the last {antisolvent_timing} s of the second step, the antisolvent ({antisolvent_volume} µL of CB) was dropped in the center of the substrate at a constant rate within 1 s.",  # 20250424文献模板
    "{antisolvent_volume} µL CB was dripped onto the center of film at {antisolvent_timing} s before the end of the spin-coating procedure.",  # 20250424文献模板
    "During the second spin coating step, {antisolvent_volume} µL of CB was deposited onto the perovskite film {antisolvent_timing} seconds before the program ended.",  # 20250424文献模板
    "{antisolvent_volume} µL CB as the antisolvent was dripped on the film at {antisolvent_timing} s before the end of the last procedure.",  # 20250424文献模板
    "A {antisolvent_volume} µL CB was dropped onto the substrate at the last {antisolvent_timing} s of the spin-coating, resulting in the formation of dark brown films.",  # 20250424文献模板
    "Then, {antisolvent_volume} µL CB was dropped onto the substrate during the second spin-coating step at the last {antisolvent_timing} s of the spin-coating.",  # 20250424文献模板
    "After {antisolvent_timing} s, {antisolvent_volume} µL CB as antisolvent was casted vertically.",  # 20250424文献模板
    "At the {antisolvent_timing} s of the spin-coating process, {antisolvent_volume} µL antisolvent was rapidly poured onto the perovskite film.",  # 20250424文献模板
    "After {antisolvent_timing} s of the second spin-coating step, {antisolvent_volume} µL of CB was dripped onto the center of the substrate to induce fast crystallization of the perovskite film.",  # 20250424文献模板
    "During the spin-coating process, {antisolvent_volume} µL of CB as anti-solvent was quickly dropped onto the samples at the end of {antisolvent_timing} s.",  # 20250424文献模板
    "{antisolvent_volume} µL of CB was dripped on the spinning substrate during the {antisolvent_timing} s of the second spin-coating step.",  # 20250424文献模板
    "{antisolvent_volume} µL CB as antisolvent was dropped {antisolvent_timing} s before the end of the spin-coating procedure.",  # 20250424文献模板
    "In the last {antisolvent_timing} s of the second step, the antisolvent ({antisolvent_volume} µL of CB) was dropped in the center.",  # 20250424文献模板
    "Antisolvent ({antisolvent_volume} µL) was dropped on the film at {antisolvent_timing} s before the end of the spinning.",  # 20250424文献模板
    "During the second step end of {antisolvent_timing} s, {antisolvent_volume} µL of CB was drop-coated to treat the perovskite films.",  # 20250424文献模板
    "After {antisolvent_timing} s, {antisolvent_volume} µL of antisolvent was rapidly dropped on top of the spinning substrate.",  # 20250424文献模板
    "During the second spin-coating step, {antisolvent_volume} µL of CB was quickly poured onto the substrate after {antisolvent_timing}.",  # 20250424文献模板
    "{antisolvent_volume} µL CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",  # 20250424文献模板
    "During this stage, {antisolvent_volume} µL CB antisolvent was quickly dripped onto the centre of the substrate at {antisolvent_timing} s before the end of the spin-coating process.",  # 20250424文献模板
    "The film was quickly washed with {antisolvent_volume} µL CB at {antisolvent_timing} s during spin-coating.",  # 20250424文献模板
    "At the {antisolvent_timing} s of spinning, {antisolvent_volume} µL of anti-solvent CB was dripped at the center.",  # 20250424文献模板
    "After {antisolvent_timing} s into spin-coating procedure, {antisolvent_volume} µL CB was dripped onto the spinning substrate.",  # 20250424文献模板
    "During the last step, {antisolvent_volume} µL of CB was dropped on the film at {antisolvent_timing} s.",  # 20250424文献模板
    "In the second step, {antisolvent_volume} µL CB was dropped onto the substrate during the last {antisolvent_timing} s of the spinning.",  # 20250424文献模板
    "{antisolvent_volume} µL CB as the antisolvent was dripped on the film at {antisolvent_timing} s before the end of the last procedure.",  # 20250424文献模板
    "{antisolvent_volume} µL CB was dropped on the film at the last {antisolvent_timing} s of the spin-coating.",  # 20250424文献模板
    "{antisolvent_volume} µL CB was dropped onto the substrate during the last {antisolvent_timing} s of the spinning, resulting in the formation of dark brown films.",  # 20250424文献模板
    "{antisolvent_volume} µL CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",  # 20250424文献模板
    "During the second spin coating step, {antisolvent_volume} µL of CB was deposited onto the perovskite film {antisolvent_timing} s before the program ended.",  # 20250424文献模板
    "A total of {antisolvent_volume} µL of CB was slowly dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",  # 20250424文献模板
    "{antisolvent_volume} µL of antisolvent was dripped onto the substrate at {antisolvent_timing} s before the end of spin-coating.",  # 20250424文献模板
    "At {antisolvent_timing} s before the end of the spin-coating procedure, {antisolvent_volume} µL CB was dropped onto the substrates.",  # 20250424文献模板
    "At the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL CB was dropped as antisolvent.",  # 20250424文献模板
    "At the {antisolvent_timing} s of the second step, {antisolvent_volume} µL antisolvent was slowly dripped onto the center of the film at {antisolvent_timing} s before the end of the spinning program.",  # 20250424文献模板
    "During the second step, {antisolvent_volume} µL of CB was dropped on the spinning substrate {antisolvent_timing} s before the end of the process.",  # 20250424文献模板
    "{antisolvent_volume} µL of CB was quickly poured to extract the mixed solvents at the last of {antisolvent_timing} s.",  # 20250424文献模板
    "During the second spin coating step, {antisolvent_volume} µL CB was dripped onto the perovskite film at {antisolvent_timing} s before ending the program.",  # 20250424文献模板
    "{antisolvent_volume} µL of antisolvent was drop-coated onto the substrate at {antisolvent_timing} s before the end of spin-coating.",  # 20250424文献模板
    "{antisolvent_volume} µL of CB was dropped on the perovskite film into the spin coating process at the last of {antisolvent_timing} s.",  # 20250424文献模板
    "During the second step, antisolvent CB ({antisolvent_volume} µL) was dropped at the middle of the spinning substrate {antisolvent_timing} s prior to the end of the spinning.",  # 20250424文献模板
    "At the last {antisolvent_timing} s of spinning, {antisolvent_volume} µL of antisolvent was dripped onto the substrate centre.",  # 20250424文献模板
    "{antisolvent_volume} µL CB antisolvent was dropped on top of the spinning substrates (about 1 cm distance) at the last {antisolvent_timing} s of spinning.",  # 20250424文献模板
    "During spin-coating process, {antisolvent_volume} µL of CB was dropped on the perovskite at {antisolvent_timing} s prior to the end of the second procedure.",  # 20250424文献模板
    "At the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL CB was dropped as antisolvent.",  # 20250424文献模板
    "{antisolvent_volume} µL antisolvent was quickly dripped at the {antisolvent_timing} s before the end of spin coating step.",  # 20250424文献模板
    "During the second spin coating step, {antisolvent_volume} µL of CB was deposited onto the perovskite film {antisolvent_timing} s before the program ended.",  # 20250424文献模板
    "During the second step, CB as antisolvent ({antisolvent_volume} µL) was dropped at the middle of the spinning substrate {antisolvent_timing} s prior to the end of the spinning.",  # 20250424文献模板
    "{antisolvent_volume} µL CB as the antisolvent was dripped on the film at {antisolvent_timing} s before the end of the last procedure.",  # 20250424文献模板
    "At the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL CB was dropped as antisolvent.",  # 20250424文献模板
    "Antisolvent ({antisolvent_volume} µL) was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",  # 20250424文献模板
    "{antisolvent_volume} µL CB was dropped on the perovskite film at {antisolvent_timing} s before the end of the program.",  # 20250424文献模板
    "{antisolvent_volume} µL of CB as antisolvent was dripped onto the substrate quickly at last {antisolvent_timing} s during the second spinning step.",  # 20250424文献模板
    "At the last {antisolvent_timing} s, {antisolvent_volume} µL of CB solution was dropped on the perovskite.",  # 20250424文献模板
    "At the last {antisolvent_timing} s, CB ({antisolvent_volume} µL) was slowly dispensed onto the middle of the substrate.",  # 20250424文献模板
    "When the countdown was {antisolvent_timing} s, {antisolvent_volume} µL CB serving as antisolvent was dropped onto the substrates.",  # 20250424文献模板
    "{antisolvent_volume} µL CB was dropped {antisolvent_timing} s before the end of the procedure.",  # 20250424文献模板
    "According to the antisolvent method, {antisolvent_volume} µL of antisolvent was dropped on the film {antisolvent_timing} s before the end of the program.",  # 20250424文献模板
    "{antisolvent_volume} µL of CB as antisolvent was dripped onto the substrate quickly at {antisolvent_timing} s during the second spinning step.",  # 20250424文献模板
    "Then, with {antisolvent_timing} s of spin time remaining, CB ({antisolvent_volume} µL) was slowly dispensed onto the middle of the substrate.",  # 20250424文献模板
    "At the last {antisolvent_timing} s, {antisolvent_volume} µL of CB solution was dropped on the perovskite.",  # 20250424文献模板
    "At the {antisolvent_timing} s before the end of the progress, {antisolvent_volume} µL CB was evenly dripped onto the substrate.",  # 20250424文献模板
    "During the spin-coating, {antisolvent_volume} µL CB solution was dripped at {antisolvent_timing} s before ending.",  # 20250424文献模板
    "{antisolvent_volume} µL of antisolvent was dropped on the film {antisolvent_timing} s before the end of the program.",  # 20250424文献模板
    "CB ({antisolvent_volume} µL) was dropped at the center of the spinning substrate approximately {antisolvent_timing} s before the end of the spin coating procedure.",  # 20250424文献模板
    "During the spin-coating process, {antisolvent_volume} µL of CB antisolvent was quickly dripped onto the centre of the perovskite film {antisolvent_timing} s before the end of the process.",  # 20250424文献模板
    "During the second step, {antisolvent_volume} µL of CB as anti-solvent was quickly dripped onto the centre of the perovskite film {antisolvent_timing} s before the end of the spin-coating process.",  # 20250424文献模板

    ]

# 退火步骤（Anneal Segments, 15条）
anneal_segments = [
"The resulting films were then annealed at {anneal_temp} °C for {anneal_time} min.",
    "Subsequent thermal treatment was carried out at {anneal_temp} °C for {anneal_time} min to finalize the perovskite crystal structure.",
    "An annealing process at {anneal_temp} °C for {anneal_time} min allowed the perovskite grains to fully mature.",
    "The sample underwent a controlled anneal at {anneal_temp} °C for {anneal_time} min, optimizing the film’s morphological and crystalline properties.",
    "Thermal annealing at {anneal_temp} °C for {anneal_time} min improved crystal ordering and reduced defect density.",
    "A post-deposition anneal at {anneal_temp} °C for {anneal_time} min stabilized the absorber layer and enhanced device performance.",
    "To lock in the desired crystal phase, the film was heated at {anneal_temp} °C for {anneal_time} min.",
    "The device architecture benefited from a final anneal at {anneal_temp} °C for {anneal_time} min, ensuring robust crystallinity.",
    "A precise annealing regimen ({anneal_temp} °C, {anneal_time} min) refined the perovskite microstructure.",
    "Employing an anneal step at {anneal_temp} °C for {anneal_time} min delivered improved crystalline quality and grain uniformity.",
    "The thermal treatment at {anneal_temp} °C for {anneal_time} min was a critical step in achieving stable and high-quality films.",
    "Post-synthesis annealing at {anneal_temp} °C for {anneal_time} min promoted uniform grain growth and optimal device characteristics.",
    "By subjecting the film to {anneal_temp} °C for {anneal_time} min, the perovskite lattice attained its ideal orientation.",
    "The perovskite layer was thermally conditioned at {anneal_temp} °C for {anneal_time} min, consolidating its morphology.",
    "Under well-defined conditions ({anneal_temp} °C, {anneal_time} min), the annealing step completed the perovskite layer formation process.",
    "The films were then annealed at {anneal_temp} °C for {anneal_time} min.",
    "The perovskite sample was subsequently annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "The sample was then annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "The substrates were immediately transferred to the hotplate and annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "Afterwards, the perovskite film was annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "Then the film is annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "Heat-treatment was implemented with the substrates for {anneal_time} min at {anneal_temp} °C.", # 20250411文献模板
    "And then annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "The as-coated film was then annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "The films were then annealed at {anneal_temp} °C for {anneal_time} min.",# 20250411文献模板
    "The film was immediately annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "The subsequent film was then heated at {anneal_temp} °C for {anneal_time} min to obtain the bright perovskite film.", # 20250411文献模板
    "After the spin coating was completed, it was annealed on a hot stage at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "The substrates were sequentially heated at {anneal_temp} °C for {anneal_time} min for perovskite crystal formation.", # 20250411文献模板
    "The perovskite film was annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "The wet film was annealed at {anneal_temp} °C for {anneal_time} min.", # 20250411文献模板
    "Then, the precursor films were placed on a {anneal_temp} °C hotplate for {anneal_time} min.",  # 20250424文献模板
    "The deposited perovskite films were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The resulting wet perovskite films were annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The film was subsequently annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The film was then annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "After spin-coating, the films were annealed on the hot plate at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "After the whole spin-coating process, the substrate was annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The samples were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "Subsequently, the samples were annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The perovskite annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The subsequent film was then heated at {anneal_temp} °C for {anneal_time} min to obtain the bright perovskite film.",  # 20250424文献模板
    "Then, it was annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "After the spin coating was completed, it was annealed on a hot stage at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The film was immediately annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The deposited perovskite films were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "Then the films were annealed at {anneal_temp} °C for {anneal_time} min to form the perovskite layer.",  # 20250424文献模板
    "Then, the as-prepared perovskite films were transferred onto a hotplate and annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The films were dried inside a N2 environment on a hot plate at a temperature of {anneal_temp} for {anneal_time} min.",  # 20250424文献模板
    "Subsequently the substrate was covered under a petri dish on a hotplate and annealed at {anneal_temp} for {anneal_time} in ambient air at 20 % relative humidity.",  # 20250424文献模板
    "Subsequently, the as-deposited films were annealed at {anneal_temp} for {anneal_time}.",  # 20250424文献模板
    "The films were then dried on a hot plate at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "Next, the substrates were quickly transferred for annealing at {anneal_temp} ℃ for {anneal_time} min.",  # 20250424文献模板
    "The substrate was immediately placed on a hotplate and annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The wet perovskite films were then transferred onto hot plate and annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The films were then annealed on a hot plate at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The deposited perovskite films were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The resulting wet perovskite films were annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The as-coated film was then annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "Heat-treatment was implemented with the substrates for {anneal_time} min at {anneal_temp} °C.",  # 20250424文献模板
    "The perovskite film was obtained by annealing at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The substrates were sequentially heated at {anneal_temp} °C for {anneal_time} min for perovskite crystal formation.",  # 20250424文献模板
    "After the spin coating was completed, it was annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "Subsequently, the sample was annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The resulting wet perovskite films were annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "It was then heated at {anneal_temp} °C for {anneal_time} min, resulting in the formation of the perovskite thin films.",  # 20250424文献模板
    "The substrates were immediately transferred to the hotplate and annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "The substrate was then transferred to a thermostatic heater and annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板
    "Then the substrate was annealed at {anneal_temp} °C for {anneal_time} min to form the perovskite layer.",  # 20250424文献模板
    "The resulting perovskite film was then annealed at {anneal_temp} °C for {anneal_time} min.",  # 20250424文献模板

    ]

# instruction 模板（Instruction Templates, 15条）
instruction_templates = [
    "Recommend a set of perovskite solar cell preparation schemes with a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², including materials information and process parameters.",
    "Propose fabrication procedures for perovskite solar cells achieving a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², detailing the materials and methods used.",
    "Suggest a series of preparation strategies for perovskite solar cells targeting a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², encompassing material specifications and processing conditions.",
    "Provide a comprehensive preparation plan for perovskite solar cells with a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², outlining the materials and fabrication parameters.",
    "Design a perovskite solar cell synthesis protocol aiming for a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², incorporating relevant materials and processing steps.",
    "Outline a preparation methodology for perovskite solar cells achieving a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², including material compositions and fabrication techniques.",
    "Develop a set of synthesis procedures for perovskite solar cells targeting a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², detailing the materials and processing conditions involved.",
    "Create a fabrication framework for perovskite solar cells with a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², specifying the materials used and the processing parameters.",
    "Formulate a preparation approach for perovskite solar cells aiming at a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², incorporating both material information and process details.",
    "Draft a set of synthesis steps for perovskite solar cells achieving a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², including material specifications and processing parameters.",
    "Establish a preparation protocol for perovskite solar cells with a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², outlining the necessary materials and fabrication conditions.",
    "Construct a fabrication plan for perovskite solar cells targeting a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², detailing the materials and processing parameters required.",
    "Devise a perovskite solar cell preparation strategy aiming for a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², encompassing both material information and process steps.",
    "Formulate a comprehensive synthesis protocol for perovskite solar cells achieving a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², including details on materials and fabrication processes.",
    "Design a preparation scheme for perovskite solar cells with a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², specifying the materials used and the processing conditions.",
    "Please design a perovskite solar cell based on a systematically tuned set of experimental parameters to achieve a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm². Layout the complete protocol.",
    "Provide a detailed and step-by-step protocol for fabricating the perovskite device under carefully optimized conditions, ensuring that the process achieves a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm². Include specific materials, equipment, deposition techniques, annealing parameters, and any critical environmental controls necessary to replicate the optimized fabrication.",
    "Develop a comprehensive fabrication protocol for a perovskite solar cell, detailing the refined parameters that led to achieving a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm². Specify the materials, deposition methods, annealing conditions, and any critical optimizations in the process to ensure reproducibility and high performance.",
    "Provide a detailed fabrication protocol for the perovskite cell, outlining precise control over solution composition, coating speeds, and thermal treatments to achieve a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm². Include specific material formulations, processing parameters, and quality control measures to ensure reproducibility and performance optimization.",
    "Using a parameter-driven approach, we engineered a perovskite solar cell that achieved a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm².",
    "Outline a comprehensive fabrication protocol detailing the meticulous parameter optimization that led to the perovskite solar cell achieving a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm². Include specific adjustments in material selection, deposition techniques, processing conditions, and performance characterization. ",
    "Develop a detailed fabrication protocol for the perovskite cell, specifying the controlled experimental inputs that led to achieving a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm². Include precise guidelines on material preparation, deposition techniques, processing conditions, and key optimization steps.",
    "Provide a detailed fabrication protocol for the perovskite solar cell, outlining the careful optimization of each step, from solution concentration to annealing, that led to achieving a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm². Include precise material formulations, deposition techniques, thermal processing conditions, and any critical optimization strategies.",
    "Detail a step-by-step fabrication protocol for the perovskite device, emphasizing the tuning of key parameters such as coating speeds, antisolvent timing, and annealing profiles. Specify the exact material compositions, processing techniques, and optimization strategies that enabled the achievement of a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm², ensuring reproducibility and performance consistency.",
    "Design a comprehensive fabrication protocol detailing the incremental refinement of parameters that led to achieving a perovskite solar cell with a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm².",
    "Provide a comprehensive fabrication protocol detailing the systematic optimization of key parameters that enabled the production of high-efficiency perovskite solar cells achieving a PCE of {pce}%, FF of {ff}, Voc of {voc} V, Jsc of {jsc} mA/cm².",
    ]

# instruction_templates = [
#     "Recommend a set of perovskite solar cell preparation schemes with a PCE of {pce}%, including materials information and process parameters.",
#     "Propose fabrication procedures for perovskite solar cells achieving a PCE of {pce}%, detailing the materials and methods used.",
#     "Suggest a series of preparation strategies for perovskite solar cells targeting a PCE of {pce}%, encompassing material specifications and processing conditions.",
#     "Provide a comprehensive preparation plan for perovskite solar cells with a PCE of {pce}%, outlining the materials and fabrication parameters.",
#     "Design a perovskite solar cell synthesis protocol aiming for a PCE of {pce}%, incorporating relevant materials and processing steps.",
#     "Outline a preparation methodology for perovskite solar cells achieving a PCE of {pce}%, including material compositions and fabrication techniques.",
#     "Develop a set of synthesis procedures for perovskite solar cells targeting a PCE of {pce}%, detailing the materials and processing conditions involved.",
#     "Create a fabrication framework for perovskite solar cells with a PCE of {pce}%, specifying the materials used and the processing parameters.",
#     "Formulate a preparation approach for perovskite solar cells aiming at a PCE of {pce}%, incorporating both material information and process details.",
#     "Draft a set of synthesis steps for perovskite solar cells achieving a PCE of {pce}%, including material specifications and processing parameters.",
#     "Establish a preparation protocol for perovskite solar cells with a PCE of {pce}%, outlining the necessary materials and fabrication conditions.",
#     "Construct a fabrication plan for perovskite solar cells targeting a PCE of {pce}%, detailing the materials and processing parameters required.",
#     "Devise a perovskite solar cell preparation strategy aiming for a PCE of {pce}%, encompassing both material information and process steps.",
#     "Formulate a comprehensive synthesis protocol for perovskite solar cells achieving a PCE of {pce}%, including details on materials and fabrication processes.",
#     "Design a preparation scheme for perovskite solar cells with a PCE of {pce}%, specifying the materials used and the processing conditions.",
#     "Please design a perovskite solar cell based on a systematically tuned set of experimental parameters to achieve a PCE of {pce}%. Layout the complete protocol.",
#     "Provide a detailed and step-by-step protocol for fabricating the perovskite device under carefully optimized conditions, ensuring that the process achieves a PCE of {pce}%. Include specific materials, equipment, deposition techniques, annealing parameters, and any critical environmental controls necessary to replicate the optimized fabrication.",
#     "Develop a comprehensive fabrication protocol for a perovskite solar cell, detailing the refined parameters that led to achieving a PCE of {pce}%. Specify the materials, deposition methods, annealing conditions, and any critical optimizations in the process to ensure reproducibility and high performance.",
#     "Provide a detailed fabrication protocol for the perovskite cell, outlining precise control over solution composition, coating speeds, and thermal treatments to achieve a PCE of {pce}%. Include specific material formulations, processing parameters, and quality control measures to ensure reproducibility and performance optimization.",
#     "Using a parameter-driven approach, we engineered a perovskite solar cell that achieved a PCE of {pce}%.",
#     "Outline a comprehensive fabrication protocol detailing the meticulous parameter optimization that led to the perovskite solar cell achieving a PCE of {pce}%. Include specific adjustments in material selection, deposition techniques, processing conditions, and performance characterization. ",
#     "Develop a detailed fabrication protocol for the perovskite cell, specifying the controlled experimental inputs that led to achieving a PCE of {pce}%. Include precise guidelines on material preparation, deposition techniques, processing conditions, and key optimization steps.",
#     "Provide a detailed fabrication protocol for the perovskite solar cell, outlining the careful optimization of each step, from solution concentration to annealing, that led to achieving a PCE of {pce}%. Include precise material formulations, deposition techniques, thermal processing conditions, and any critical optimization strategies.",
#     "Detail a step-by-step fabrication protocol for the perovskite device, emphasizing the tuning of key parameters such as coating speeds, antisolvent timing, and annealing profiles. Specify the exact material compositions, processing techniques, and optimization strategies that enabled the achievement of a PCE of {pce}%, ensuring reproducibility and performance consistency.",
#     "Design a comprehensive fabrication protocol detailing the incremental refinement of parameters that led to achieving a perovskite solar cell with a PCE of {pce}%.",
#     "Provide a comprehensive fabrication protocol detailing the systematic optimization of key parameters that enabled the production of high-efficiency perovskite solar cells achieving a PCE of {pce}%.",
#     ]


# 钝化层材料和工艺描述（Passivation Segments, 15条）
passivation_material_segments_single = [
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was incorporated as passivator.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) was spin-coated onto the sample surface as a passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was added as a passivator.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was used as a passivator in the formulation.",
    "A passivation layer, {formula_passivator1} ({concentration_passivator1} mg/mL), was incorporated into the system.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) served as the passivator in this study.",
    "The passivation process involved the use of {formula_passivator1} ({concentration_passivator1} mg/mL).",
    "The incorporation of {formula_passivator1} ({concentration_passivator1} mg/mL) was used as a passivator to enhance stability.",
    "To improve device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) was applied as a passivation layer via spin-coating onto the sample surface.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) was deposited as a passivation layer on the sample surface using spin-coating.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was spin-coated onto the sample surface to serve as a passivation layer, thereby improving device performance.",
    "In order to boost device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) was deposited onto the sample surface as a passivation layer through spin-coating.",
    "A passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL) was applied to the sample surface by spin-coating to enhance device performance.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was utilized as a passivation layer through spin-coating to enhance device performance.",
    "Spin-coating of {formula_passivator1} ({concentration_passivator1} mg/mL) onto the sample surface was performed to improve device performance.",
    "To achieve better device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) was spin-coated onto the sample surface as a passivation layer.",
    "The application of {formula_passivator1} ({concentration_passivator1} mg/mL) as a passivation layer via spin-coating significantly boosted device performance.",
    "The passivator {formula_passivator1} ({concentration_passivator1} mg/mL) was introduced into the system to improve material properties.",
    "For better device performance, a passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL) was deposited through spin-coating.",
    "To enhance passivation, {formula_passivator1} ({concentration_passivator1} mg/mL) was incorporated into the fabrication process.",
    "The passivation solution was prepared using {formula_passivator1} ({concentration_passivator1} mg/mL).",
    "To improve the stability of the material, {formula_passivator1} ({concentration_passivator1} mg/mL) was applied onto the substrate surface as a protective coating.",
    "To optimize the reaction efficiency, {formula_passivator1} ({concentration_passivator1} mg/mL) was deposited onto the catalyst surface as a modifying layer.",
    "To optimize device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) was uniformly spin-coated onto the perovskite surface to form an effective passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was spin-coated onto the perovskite film to act as an efficient passivation layer.",
    "A passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL) was deposited by spin-coating to improve surface quality.",
    "The {formula_passivator1} ({concentration_passivator1} mg/mL) was coated onto the perovskite surface.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was deposited onto the perovskite film.",
    "For the surface treatment of perovskite films, chalcogen-concave molecular stock solutions of {formula_passivator1} ({concentration_passivator1} mg/mL) were spincoated on the perovskite film",  # 20250411文献模板
    "For the surface passivation layer, the {formula_passivator1} was dissolved in IPA at a concentration of {concentration_passivator1} mg/mL.",  # 20250411文献模板
    "{concentration_passivator1} mg/mL {formula_passivator1} was spin-coated onto the perovskite film.",  # 20250411文献模板
    "A small amount of {formula_passivator1} at a concentration of {concentration_passivator1} mg/mL was added into the chlorobenzene/IPA antisolvent mixture for interface modification.",  # 20250424文献模板
    "{formula_passivator1} as passivation layer was prepared with a concentration of {concentration_passivator1} mg/mL in IPA solution.",  # 20250424文献模板
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was introduced as passivation layer, which was prepared in IPA mixed solution.",  # 20250424文献模板
    "{concentration_passivator1} mg/mL {formula_passivator1} in isopropyl alcohol was prepared as passivating layer.",  # 20250424文献模板
    "For the interfacial passivation layer, {formula_passivator1} with the concentration of {concentration_passivator1} mg/mL in IPA was used.",  # 20250424文献模板
    "The post-passivation layer was prepared by dissolving {concentration_passivator1} mg of {formula_passivator1} in 1 mL IPA and stirring for 1 h." , # 20250424文献模板
    "{concentration_passivator1} {formula_passivator1} was spin-coated onto the perovskite film.",  # 20250424文献模板
    "Later, the {concentration_passivator1} mg/mL {formula_passivator1} (in IPA) was evenly spread on the surface of the perovskite film.",  # 20250424文献模板
    "For the surface passivation layer, the {formula_passivator1} was dissolved in IPA at a concentration of {concentration_passivator1} mg/mL.",  # 20250424文献模板

    ]

passivation_material_segments_dual = [
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were incorporated as passivator.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spin-coated onto the sample surface as a passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were added as a passivator.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were used as a passivator in the formulation.",
    "A passivation layer, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL), was incorporated into the system.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) served as the passivator in this study.",
    "The passivation process involved the use of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL).",
    "The incorporation of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were used as a passivator to enhance stability.",
    "To improve device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were applied as a passivation layer via spin-coating onto the sample surface.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were deposited as a passivation layer on the sample surface using spin-coating.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spin-coated onto the sample surface to serve as a passivation layer, thereby improving device performance.",
    "In order to boost device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were deposited onto the sample surface as a passivation layer through spin-coating.",
    "A passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) was applied to the sample surface by spin-coating to enhance device performance.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) were utilized as a passivation layer through spin-coating to enhance device performance.",
    "Spin-coating of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) onto the sample surface were performed to improve device performance.",
    "To achieve better device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spin-coated onto the sample surface as a passivation layer.",
    "The application of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) as a passivation layer via spin-coating significantly boosted device performance.",
    "The passivator {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were introduced into the system to improve material properties.",
    "For better device performance, a passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) was deposited through spin-coating.",
    "To enhance passivation, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were incorporated into the fabrication process.",
    "The passivation solution were prepared using {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL).",
    "To improve the stability of the material, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were applied onto the substrate surface as a protective coating.",
    "To optimize the reaction efficiency, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were deposited onto the catalyst surface as a modifying layer.",
    "To optimize device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were uniformly spin-coated onto the perovskite surface to form an effective passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spin-coated onto the perovskite film to act as an efficient passivation layer.",
    "A passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) was deposited by spin-coating to improve surface quality.",
    "The {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were coated onto the perovskite surface.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were deposited onto the perovskite film.",
    "For the surface treatment of perovskite films, chalcogen-concave molecular stock solutions of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spincoated on the perovskite film",
    # 20250424文献模板
    "For the surface passivation layer, the {formula_passivator1} and {formula_passivator2} were dissolved in IPA at a concentration of {concentration_passivator1} mg/mL and {concentration_passivator2} mg/mL.",
    # 20250411文献模板
    "For the interfacial passivation layer, {formula_passivator1} and {formula_passivator2} with the concentration of {concentration_passivator1} mg/mL and {concentration_passivator2} mg/mL were used.",
    # 20250411文献模板
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were introduced as passivation layer.",
    # 20250411文献模板
    "For the {formula_passivator1}–{formula_passivator2} modified layer, the treatment solution were prepared by dissolving {concentration_passivator1} mg {formula_passivator1} and {concentration_passivator2} mg {formula_passivator2} into 1 mL IPA.",
    # 20250424文献模板
    "Subsequently, the mixed passivating agents of {formula_passivator1}+{formula_passivator2} ({concentration_passivator1} mg of {formula_passivator1} and {concentration_passivator2} mg of {formula_passivator2}) were dissolved in 1 mL of IPA.",
    # 20250424文献模板

]

passivation_material_segments_triple = [
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were incorporated as passivator.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL)  were spin-coated onto the sample surface as a passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were added as a passivator.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were used as a passivator in the formulation.",
    "A passivation layer, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL), was incorporated into the system.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) served as the passivator in this study.",
    "The passivation process involved the use of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL).",
    "The incorporation of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were used as a passivator to enhance stability.",
    "To improve device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were applied as a passivation layer via spin-coating onto the sample surface.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were deposited as a passivation layer on the sample surface using spin-coating.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were spin-coated onto the sample surface to serve as a passivation layer, thereby improving device performance.",
    "In order to boost device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were deposited onto the sample surface as a passivation layer through spin-coating.",
    "A passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) was applied to the sample surface by spin-coating to enhance device performance.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were utilized as a passivation layer through spin-coating to enhance device performance.",
    "Spin-coating of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) onto the sample surface were performed to improve device performance.",
    "To achieve better device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were spin-coated onto the sample surface as a passivation layer.",
    "The application of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) as a passivation layer via spin-coating significantly boosted device performance.",
    "The passivator {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were introduced into the system to improve material properties.",
    "For better device performance, a passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) was deposited through spin-coating.",
    "To enhance passivation, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were incorporated into the fabrication process.",
    "The passivation solution were prepared using {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL).",
    "To improve the stability of the material, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were applied onto the substrate surface as a protective coating.",
    "To optimize the reaction efficiency, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were deposited onto the catalyst surface as a modifying layer.",
    "To optimize device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were uniformly spin-coated onto the perovskite surface to form an effective passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were spin-coated onto the perovskite film to act as an efficient passivation layer.",
    "A passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) was deposited by spin-coating to improve surface quality.",
    "The {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were coated onto the perovskite surface.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were deposited onto the perovskite film.",
    "For the surface treatment of perovskite films, chalcogen-concave molecular stock solutions of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were spin coated on the perovskite film",  # 20250411文献模板
    "For the surface passivation layer, the {formula_passivator1}, {formula_passivator2} and {formula_passivator3} were dissolved in IPA at a concentration of {concentration_passivator1} mg/mL, {concentration_passivator2} mg/mL and {concentration_passivator3} mg/mL.",  # 20250411文献模板

        ]

passivation_spin_segments = [
    "The spin-coating process was conducted at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Spin-coating of the passivation layer was performed at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Using spin speeds of {spin_speed_passivator} rpm and spin times of {spin_time_passivator} s, the passivation layer was applied.",
    "The passivation layer was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Spin-coating parameters for the passivation layer were set to {spin_speed_passivator} rpm and {spin_time_passivator} s.",
    "A spin-coating speed of {spin_speed_passivator} rpm for {spin_time_passivator} s was utilized for the passivation layer.",
    "The passivation layer was applied via spin-coating at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Spin-coating of passivator at {spin_speed_passivator} rpm for {spin_time_passivator} s formed the passivation layer.",
    "The spin-coating process for the passivation layer involved {spin_speed_passivator} rpm and {spin_time_passivator} s.",
    "To apply the passivation layer, spin-coating was done at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "A spin speed of {spin_speed_passivator} rpm and a spin time of {spin_time_passivator} s were used for the passivation layer.",
    "The passivation layer was spin-coated using {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Spin-coating was executed at {spin_speed_passivator} rpm for {spin_time_passivator} s to apply the passivation layer.",
    "For the passivation layer, spin-coating parameters were {spin_speed_passivator} rpm and {spin_time_passivator} s.",
    "The passivation layer was deposited via spin-coating at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "The spin coating was performed at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "For the surface treatment of perovskite films, the passivators were spincoated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "Then passivators were spin-coated onto the as-prepared perovskite films at a speed of {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "For passivator treatment, the passivators were spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "Then it was spin-coated on the cooled perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "For the surface passivation, passivators were spin-coated on perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "Then, passivation solution was spin-coated on top of the as-prepared perovskite at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "After cooled to room temperature, passivators were deposited by spin-coating with {spin_speed_passivator} rpm.", # 20250411文献模板
    "For the passivation treatment, passivators were spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "Afterwards, passivators were deposited on the perovskite film by spin-coating at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "Subsequently, the passivation solution was dropped on the annealed perovskite films during a spin-coating procedure at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "The passivation mixed solution was spin-coated on the perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "It was spin-coated on top of perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "It was then spin-coated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "It was deposited on the surface of the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "A passivation solution was deposited on the perovskite layer by spin coating at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "The passivation solution was dynamically spin-coated on the annealed perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", # 20250411文献模板
    "The solution was spin-coated onto the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "The solution was spin-coated onto the perovskite films at a speed of {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "It was then spin-coated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "It was deposited on the surface of the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "It was spin-coated on top of perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "The surface treatment was finished by depositing passivation solution onto the perovskite film surface at a spin rate of {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "Then the passivation solution was spin-coated on the inorganic perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "Afterwards, the passivation solution was deposited on the perovskite film by spin-coating at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "Subsequently, the passivation solution was dropped on the annealed perovskite films during a spin-coating procedure at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "The passivation solution was deposited on the perovskite layer by spin coating at {spin_speed_passivator} rpm for {spin_time_passivator} s without further annealing.",  # 20250424文献模板
    "For the surface treatment of perovskite films, the passivation solution was spin-coated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "Then the passivation solution was spin-coated onto the as-prepared perovskite films at a speed of {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "And then it was spin-coated on the cooled perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "The spin coating was performed at {spin_speed_passivator} for {spin_time_passivator}.",  # 20250424文献模板
    "The passivation solution was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "For surface treatment, the passivation solution was spin-coated onto perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "Afterward, the obtained saturated solution as passivating layer was spin-coated on the film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "Next, the passivation solution was dynamically spin-coated onto the as-formed perovskite at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "The passivation solution was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s on top of the perovskite film to form a passivation layer.",  # 20250424文献模板
    "For the surface passivation, the passivation solution was spin-coated on perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "For the passivation treatment, the passivation solution was spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "The passivation solution was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s onto the perovskite film.",  # 20250424文献模板
    "Then, the surface treatment solution was subsequently spin-coated on the film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板
    "The passivation layers were sequentially spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  # 20250424文献模板

    ]

passivation_drop_segments = [
    "Subsequently, {passivator_volume} µL of passivator was dropped at {passivator_timing} s during spin-coating.",
    "During spin-coating, {passivator_volume} µL of passivator was introduced at {passivator_timing} s.",
    "At {passivator_timing} s, {passivator_volume} µL of passivator was added to the spinning passivation layer.",
    "The passivator volume of {passivator_volume} µL was dropped at {passivator_timing} s during spin-coating.",
    "{passivator_volume} µL of passivator was introduced at {passivator_timing} s in the spin-coating process.",
    "During the spin-coating of the passivation layer, {passivator_volume} µL of passivator was added at {passivator_timing} s.",
    "At a timing of {passivator_timing} s, {passivator_volume} µL of passivator was introduced into the spinning passivation layer.",
    "The addition of {passivator_volume} µL passivator occurred at {passivator_timing} s during spin-coating.",
    "To enhance the passivation layer, {passivator_volume} µL of passivator was dropped at {passivator_timing} s during spin-coating.",
    "{passivator_volume} µL of passivator was gently dispensed at {passivator_timing} s during the spin-coating of the passivation layer.",
    "Passivator {passivator_volume} µL was added at {passivator_timing} s during the spin-coating process.",
    "At {passivator_timing} s, a drop of {passivator_volume} µL passivator was introduced during spin-coating.",
    "The spin-coating process included the addition of {passivator_volume} µL passivator at {passivator_timing} s.",
    "To improve passivation, {passivator_volume} µL of passivator was dropped at {passivator_timing} s during spin-coating.",
    "During spin-coating, {passivator_volume} µL of passivator was drop-casted onto the sample at {passivator_timing} s.", # 20250411文献模板

    ]

passivation_anneal_segments = [
    "The passivation layer was then annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min to enhance film quality.",
    "Annealing of the passivation layer was performed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "The passivation layer underwent annealing at {anneal_temp_passivator} °C for {anneal_time_passivator} min to optimize its properties.",
    "To finalize the passivation layer, annealing was conducted at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "After spin-coating, the passivation layer was annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "The annealing process for the passivation layer was carried out at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "Post spin-coating, the passivation layer was annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "To enhance the passivation layer, annealing was performed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "The passivation layer was subjected to annealing at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "Annealing was executed at {anneal_temp_passivator} °C for {anneal_time_passivator} min to finalize the passivation layer.",
    "The passivation layer was thermally treated at {anneal_temp_passivator} °C for {anneal_time_passivator} min to improve its properties.",
    "Post-deposition annealing of the passivation layer was conducted at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "To ensure optimal passivation, the layer was annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "The final step involved annealing the passivation layer at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "To consolidate the passivation layer, annealing was performed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",
    "Thermal treatment involved annealing at {anneal_temp_passivator} °C for {anneal_time_passivator} min to facilitate crystallization.", # 20250411文献模板
    "The film was then annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "The films were subsequently dried at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "And followed by annealing at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "Then annealing at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "And then annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "And then transferred to the hotplate and annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "And heated at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "Subsequently, the sample was annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "Followed by annealing at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "Then, it was annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "Subsequently, the film was annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.", # 20250411文献模板
    "It was then annealed on a hotplate at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min to form the perovskite film.",  # 20250424文献模板
    "Passivator solution was spin-coated and annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",  # 20250424文献模板
    "Then, it was annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",  # 20250424文献模板
    "It was then annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min to remove the solvent residual.",  # 20250424文献模板
    "Thermal treatment involved annealing at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min to facilitate crystallization.",  # 20250424文献模板
    "It was then annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min as a post-treatment for PSCs.",  # 20250424文献模板

    ]

# 固定指令文本
instruction_variants = [
    "Please help me design a perovskite device fabrication scheme that integrates multiple additives, several SAMs, and multiple passivators, along with the complete materials and process parameters required.",
    "Help me create a detailed perovskite solar cell manufacturing plan that incorporates multiple additives, a variety of SAMs, and several passivators, with full material specifications and processing steps.",
    "I would like assistance in developing a robust fabrication protocol for a perovskite solar cell that leverages numerous additives, diverse SAMs, and a range of passivators, including all necessary materials and process settings.",
    "Could you help design a perovskite solar cell production strategy that utilizes various additives, multiple self-assembled monolayers (SAMs), and several passivators, complete with details on materials and process parameters?",
    "Assist me in formulating a perovskite device fabrication approach that employs a combination of several additives, assorted SAMs, and multiple passivators, with comprehensive material information and procedural parameters.",
    "Please develop a complete process and materials plan for fabricating a perovskite solar cell that integrates several additives, multiple SAMs, and distinct passivators.",
    "Help me devise a perovskite solar cell fabrication protocol using a mix of multiple additives, diverse SAMs, and various passivators, providing all necessary materials information and process specifications.",
    "I need a detailed fabrication design for a perovskite device incorporating numerous additives, a selection of SAMs, and multiple passivators, including both material details and processing conditions.",
    "Can you assist in designing a perovskite solar cell production method that involves the use of multiple additives, a variety of SAMs, and several passivators, complete with a full list of materials and processing parameters?",
    "Please help create a comprehensive perovskite device fabrication plan that combines multiple additives, assorted SAMs, and several passivators, with detailed material and process guidelines.",
    "I'm looking for assistance to design a fabrication scheme for perovskite solar cells that features several additives, diverse SAMs, and multiple passivators, along with the requisite materials and process steps.",
    "Assist me in outlining the materials and process parameters needed for a perovskite solar cell that integrates various additives, several SAMs, and a combination of passivators.",
    "Kindly develop a perovskite device fabrication strategy that employs multiple additives, different types of SAMs, and various passivators, accompanied by comprehensive materials and procedural details.",
    "I require a detailed plan for perovskite solar cell fabrication that includes the use of several additives, multiple SAMs, and numerous passivators, as well as all essential materials and process parameters.",
    "Please work with me to design a perovskite solar cell manufacturing framework that utilizes an array of additives, diverse self-assembled monolayers, and a selection of passivators, with full details on the materials and process.",
    "Help me create a robust process and material scheme for a perovskite device that relies on various additives, several types of SAMs, and multiple passivators, ensuring all necessary specifications are addressed.",
    "I need assistance in developing a fabrication protocol for perovskite solar cells that brings together a variety of additives, multiple SAMs, and a set of passivators, with thorough details on the required materials and processing steps.",
    "Could you please design a perovskite device fabrication method that combines several additives, distinct SAMs, and multiple passivators, including comprehensive information on materials and process parameters?",
    "Assist me in formulating a complete manufacturing strategy for perovskite solar cells, incorporating multiple additives, different SAMs, and several passivators, and providing all essential material and process specifications.",
    "Please help develop an all-encompassing perovskite solar cell production plan that integrates an assortment of additives, various SAMs, and a range of passivators, along with detailed materials data and process conditions."
]

sam_spin_anneal_segments = [
    "In details, SAM solution was spin-coated on the substrate at {spin_speed_sam} rpm for {spin_time_sam} s, and annealed at {anneal_temp_sam} °C for {anneal_time_sam} min.",
]

diff_segments = {
    "Formula SAM 1-Adding": [
        "The only difference lies in the self-assembled monolayer: The control device does not have a self-assembled monolayer, while the target  device used {formula_sam1}({concentration_sam1} mg/mL). The PCE increased from {control_device_pce}% to {target_device_pce}%, VOC from {control_device_voc} V to {target_device_voc} V, JSC from {control_device_jsc} to {target_device_jsc} mA/cm², and FF from {control_device_ff}% to {target_device_ff}%.", # from 王兴洁
    ],
    "Formula Passivator 1-Adding": [
        "The only difference lay in the passivation layer: control device had no passivation layer, whereas target device used {formula_passivator1} ({concentration_passivator1} mg/mL). The PCE increased from {control_device_pce}% to {target_device_pce}%, VOC from {control_device_voc} V to {target_device_voc} V, JSC from {control_device_jsc} to {target_device_jsc} mA/cm², and FF from {control_device_ff}% to {target_device_ff}%.", # from 蒋胜筹
    ],
    "Formula Additive 1-Adding": [
        "The only difference was that the control device did not add {formula_additive1} , while the target device added {formula_additive1} ( {concentration_additive1} mg/mL ) . The introduction of {formula_additive1} as an additive brings performance gains: the PCE rose from  {control_device_pce}% to {target_device_pce}%, the short-circuit current density increased from {control_device_jsc} mA cm⁻² to {target_device_jsc} mA cm⁻², and the open-circuit voltage improved from {control_device_voc} V to {target_device_voc} V, while the fill factor declined from {control_device_ff} % to {target_device_ff} % ." # from 雷怡潇
        "The only difference lay in the additive component: the control device contained no {formula_additive1}, whereas the target device incorporated {formula_additive1} ({concentration_additive1} mg/mL). The PCE increased from {control_device_pce}% to {target_device_pce}%, VOC from {control_device_voc} V to {target_device_voc} V, JSC from {control_device_jsc} to {target_device_jsc} mA/cm², and FF from {control_device_ff}% to {target_device_ff}%." # from 王子旋
    ],
}

compared_groups = {
    'Formula Additive 1-Adding': {
        'Formula Additive 1': 'formula_additive1',
        'Concentration Additive 1': 'concentration_additive1'
    },
    'Formula SAM 1-Adding': {
        'Formula SAM 1': 'formula_sam1',
        'Concentration SAM 1': 'concentration_sam1'
    },
    'Formula Passivator 1-Adding': {
        'Formula Passivator 1': 'formula_passivator1',
        'Concentration Passivator 1': 'concentration_passivator1'
    },

}

def generate_compared_group_desc(control_device: dict, target_device: dict, compared_group: str):
    device_info = {
        'control_device_pce': control_device['PCE'],
        'target_device_pce': target_device['PCE'],
        'control_device_voc': control_device['Voc'],
        'target_device_voc': target_device['Voc'],
        'control_device_jsc': control_device['Jsc'],
        'target_device_jsc': target_device['Jsc'],
        'control_device_ff': control_device['FF'],
        'target_device_ff': target_device['FF']
    }

    for column_name, var_name in compared_groups[compared_group].items():
        device_info[var_name] = target_device[column_name]

    return random.choice(diff_segments[compared_group]).format(**device_info)


# ---------------------------
# 核心函数：根据特征字典生成文本
# ---------------------------

def generate_text(features: dict) -> str:
    """
    features: dict 包含键值对，如 'PCE', 'FF', 'Voc', 'Jsc',
    'Formula_PVK', 'Concentration_PVK',
    'Formula_SAM', 'Concentration_SAM',
    'Formula_Additive', 'Concentration_Additive',
    'Spin1_Speed', 'Spin1_Time', 'Spin2_Speed', 'Spin2_Time',
    'Antisolvent_Volume', 'Antisolvent_Timing',
    'Anneal_Temp', 'Anneal_Time',
    'Formula_Passivator', 'Concentration_Passivator',
    'Spin_Passivator_Speed', 'Spin_Passivator_Time',
    'Passivator_Volume', 'Passivator_Timing',
    'Anneal_Temp_Passivator', 'Anneal_Time_Passivator'.
    返回组装好的描述文本。
    """

    parts = []
    # 1. 准备表述
    prepared = random.choice(prepared_phrases)
    intro = random.choice(intro_segments).format(
        prepared_term=prepared,
        pce=features.get('PCE'),
        ff=features.get('FF'),
        voc=features.get('Voc'),
        jsc=features.get('Jsc')
    )
    parts.append(intro)

    # 2. 钙钛矿配方
    if features.get('Formula PVK') and features.get('Concentration PVK'):
        pvk = random.choice(perovskite_formula_segments).format(
            formula_pvk=features['Formula PVK'],
            concentration_pvk=features['Concentration PVK']
        )
        parts.append(pvk)

    # 3. SAM（若提供）
    sam1 = features.get('Formula SAM 1')
    sam2 = features.get('Formula SAM 2')
    sam3 = features.get('Formula SAM 3')

    # TODO: 选择单/双/三SAM模板并格式化
    if sam1 in [''] and sam2 in [''] and sam3 in ['']:
        # 如果全部为空，则不使用任何 SAM 片段
        sam_formula = ""
    elif sam1 not in [''] and sam2 in [''] and sam3 in ['']:
        # 仅第一项有效 → 单 SAM
        sam_formula = random.choice(sam_formula_segments_single).format(
            formula_sam1=features['Formula SAM 1'],
            concentration_sam1=features['Concentration SAM 1']
        )
    elif sam1 not in ['N/A', ''] and sam2 not in ['N/A', ''] and sam3 in ['N/A', '']:
        # 前两项有效 → 双 SAM
        sam_formula = random.choice(sam_formula_segments_dual).format(
            formula_sam1=features['Formula SAM 1'],
            concentration_sam1=features['Concentration SAM 1'],
            formula_sam2=features.get('Formula SAM 2'),
            concentration_sam2=features.get('Concentration SAM 2')
        )
    else:
        # 三项或更多有效 → 三 SAM
        sam_formula = random.choice(sam_formula_segments_triple).format(
            formula_sam1=features['Formula SAM 1'],
            concentration_sam1=features['Concentration SAM 1'],
            formula_sam2=features.get('Formula SAM 2'),
            concentration_sam2=features.get('Concentration SAM 2'),
            formula_sam3=features.get('Formula SAM 3'),
            concentration_sam3=features.get('Concentration SAM 3')
        )

    parts.append(sam_formula)

    # 4. 添加剂（若提供）
    add1, add2, add3 = features.get('Formula Additive 1'), features.get('Formula Additive 2'), features.get('Formula Additive 3')
    if add1 in ['']:
        additive_formula = ""
    else:
        if add2 in [''] and add3 in ['']:
            additive_formula = random.choice(additive_formula_segments_single).format(
                formula_add1=features['Formula Additive 1'],
                concentration_add1=features['Concentration Additive 1'],
        )
        elif add3 in ['']:
            additive_formula = random.choice(additive_formula_segments_dual).format(
                formula_add1=features['Formula Additive 1'],
                concentration_add1=features['Concentration Additive 1'],
                formula_add2=features['Formula Additive 2'],
                concentration_add2=features['Concentration Additive 2'],
        )
        else:
            additive_formula = random.choice(additive_formula_segments_triple).format(
                formula_add1=features['Formula Additive 1'],
                concentration_add1=features['Concentration Additive 1'],
                formula_add2=features['Formula Additive 2'],
                concentration_add2=features['Concentration Additive 2'],
                formula_add3=features['Formula Additive 3'],
                concentration_add3=features['Concentration Additive 3']
        )

    parts.append(additive_formula)

    # 5. 旋涂工艺
    spin_process = random.choice(process_segments).format(
            spin1_speed=features['Spin Coating Speed PVK 1'],
            spin1_time=features['Spin Coating Time PVK 1'],
            spin2_speed=features['Spin Coating Speed PVK 2'],
            spin2_time=features['Spin Coating Time PVK 2']
        )
    parts.append(spin_process)

    # 6. 抗溶剂
    antisolvent_process = random.choice(antisolvent_segments).format(
            antisolvent_volume=features['Antisolvent Volume'],
            antisolvent_timing=features['Antisolvent Dropping Timing']
        )
    parts.append(antisolvent_process)

    # 7. 退火
    anneal_process = random.choice(anneal_segments).format(
            anneal_temp=features['Annealed Temperature PVK'],
            anneal_time=features['Annealed Time PVK']
        )
    parts.append(anneal_process)

    # 8. 钝化（若提供 材料 + 工艺）
    pass1, pass2, pass3 = features.get('Formula Passivator 1'), features.get('Formula Passivator 2'), features.get('Formula Passivator 3')
    if pass1 in ['']:
        passivation_formula = ""
        passivation_spin = ""
        passivation_drop = ""
        passivation_anneal = ""
    else:
        if pass2 in [''] and pass3 in ['']:
            passivation_formula = random.choice(passivation_material_segments_single).format(
                formula_passivator1=features['Formula Passivator 1'],
                concentration_passivator1=features['Concentration Passivator 1']
            )
            passivation_spin = random.choice(passivation_spin_segments).format(
                spin_speed_passivator=features['Spin Coating Speed Passivator'],
                spin_time_passivator=features['Spin Coating Time Passivator']
            )
            passivation_drop = random.choice(passivation_drop_segments).format(
                passivator_timing=features['Passivator Dropping Timing'],
                passivator_volume=features['Passivator Volume']
            )
            passivation_anneal = random.choice(passivation_anneal_segments).format(
                anneal_temp_passivator=features['Annealed Temperature Passivator'],
                anneal_time_passivator=features['Annealed Time Passivator']
            )
        elif pass3 in ['']:
            passivation_formula = random.choice(passivation_material_segments_dual).format(
                formula_passivator1=features['Formula Passivator 1'],
                concentration_passivator1=features['Concentration Passivator 1'],
                formula_passivator2=features['Formula Passivator 2'],
                concentration_passivator2=features['Concentration Passivator 2']
            )
            passivation_spin = random.choice(passivation_spin_segments).format(
                spin_speed_passivator=features['Spin Coating Speed Passivator'],
                spin_time_passivator=features['Spin Coating Time Passivator']
            )
            passivation_drop = random.choice(passivation_drop_segments).format(
                passivator_timing=features['Passivator Dropping Timing'],
                passivator_volume=features['Passivator Volume']
            )
            passivation_anneal = random.choice(passivation_anneal_segments).format(
                anneal_temp_passivator=features['Annealed Temperature Passivator'],
                anneal_time_passivator=features['Annealed Time Passivator']
            )
        else:
            passivation_formula = random.choice(passivation_material_segments_triple).format(
                formula_passivator1=features['Formula Passivator 1'],
                concentration_passivator1=features['Concentration Passivator 1'],
                formula_passivator2=features['Formula Passivator 2'],
                concentration_passivator2=features['Concentration Passivator 2'],
                formula_passivator3=features['Formula Passivator 3'],
                concentration_passivator3=features['Concentration Passivator 3']
            )
            passivation_spin = random.choice(passivation_spin_segments).format(
                spin_speed_passivator=features['Spin Coating Speed Passivator'],
                spin_time_passivator=features['Spin Coating Time Passivator']
            )
            passivation_drop = random.choice(passivation_drop_segments).format(
                passivator_timing=features['Passivator Dropping Timing'],
                passivator_volume=features['Passivator Volume']
            )
            passivation_anneal = random.choice(passivation_anneal_segments).format(
                anneal_temp_passivator=features['Annealed Temperature Passivator'],
                anneal_time_passivator=features['Annealed Time Passivator']
            )
    parts.append(passivation_formula)
    parts.append(passivation_spin)
    parts.append(passivation_drop)
    parts.append(passivation_anneal)

    if 'Spin Coating Speed SAM' not in features or features['Spin Coating Speed SAM'] == '':
        return " ".join(parts)

    single_coating = random.choice(sam_spin_anneal_segments).format(
        spin_speed_sam=features['Spin Coating Speed SAM'],
        spin_time_sam=features['Spin Coating Time SAM'],
        anneal_temp_sam=features['Annealed Temperature SAM'],
        anneal_time_sam=features['Annealed Time SAM']
    )

    parts.append(single_coating)

    return " ".join(parts)

def generate_singla_var_pair_metrics_text(high_pce_metrics_features: dict, low_pce_metrics_features: dict):
    prepared = random.choice(prepared_phrases)

    high_pce_intro = random.choice(intro_segments).format(
        prepared_term=prepared,
        pce=high_pce_metrics_features.get('PCE'),
        ff=high_pce_metrics_features.get('FF'),
        voc=high_pce_metrics_features.get('Voc'),
        jsc=high_pce_metrics_features.get('Jsc')
    )

    low_pce_intro = random.choice(intro_segments).format(
        prepared_term=prepared,
        pce=low_pce_metrics_features.get('PCE'),
        ff=low_pce_metrics_features.get('FF'),
        voc=low_pce_metrics_features.get('Voc'),
        jsc=low_pce_metrics_features.get('Jsc')
    )

    return high_pce_intro, low_pce_intro


def generate_segmented_text(features: dict) -> str:
    """
    features: dict 包含键值对，如 'PCE', 'FF', 'Voc', 'Jsc',
    'Formula_PVK', 'Concentration_PVK',
    'Formula_SAM', 'Concentration_SAM',
    'Formula_Additive', 'Concentration_Additive',
    'Spin1_Speed', 'Spin1_Time', 'Spin2_Speed', 'Spin2_Time',
    'Antisolvent_Volume', 'Antisolvent_Timing',
    'Anneal_Temp', 'Anneal_Time',
    'Formula_Passivator', 'Concentration_Passivator',
    'Spin_Passivator_Speed', 'Spin_Passivator_Time',
    'Passivator_Volume', 'Passivator_Timing',
    'Anneal_Temp_Passivator', 'Anneal_Time_Passivator'.
    返回组装好的描述文本。
    """

    parts = {
        "Metrics": None,
        "PVK": [],
        "SAM": [],
        "Additive": [],
        "Passivator": [],
        "Single_Coating": []
    }

    prepared = random.choice(prepared_phrases)

    metrics_intro = random.choice(intro_segments).format(
        prepared_term=prepared,
        pce=features.get('PCE'),
        ff=features.get('FF'),
        voc=features.get('Voc'),
        jsc=features.get('Jsc')
    )

    parts["Metrics"] = metrics_intro

    # 1. 钙钛矿配方
    if features.get('Formula PVK') and features.get('Concentration PVK'):
        pvk = random.choice(perovskite_formula_segments).format(
            formula_pvk=features['Formula PVK'],
            concentration_pvk=features['Concentration PVK']
        )
        parts["PVK"].append(pvk)

    # 2. 旋涂工艺
    spin_process = random.choice(process_segments).format(
            spin1_speed=features['Spin Coating Speed PVK 1'],
            spin1_time=features['Spin Coating Time PVK 1'],
            spin2_speed=features['Spin Coating Speed PVK 2'],
            spin2_time=features['Spin Coating Time PVK 2']
        )
    parts["PVK"].append(spin_process)

    # 3. 抗溶剂
    antisolvent_process = random.choice(antisolvent_segments).format(
            antisolvent_volume=features['Antisolvent Volume'],
            antisolvent_timing=features['Antisolvent Dropping Timing']
        )
    parts["PVK"].append(antisolvent_process)

    # 4. 退火
    anneal_process = random.choice(anneal_segments).format(
            anneal_temp=features['Annealed Temperature PVK'],
            anneal_time=features['Annealed Time PVK']
        )
    parts["PVK"].append(anneal_process)

    parts["PVK"] = " ".join(parts["PVK"])

    # 5. SAM（若提供）
    sam1 = features.get('Formula SAM 1')
    sam2 = features.get('Formula SAM 2')
    sam3 = features.get('Formula SAM 3')

    # TODO: 选择单/双/三SAM模板并格式化
    if sam1 in [''] and sam2 in [''] and sam3 in ['']:
        # 如果全部为空，则不使用任何 SAM 片段
        sam_formula = ""
    elif sam1 not in [''] and sam2 in [''] and sam3 in ['']:
        # 仅第一项有效 → 单 SAM
        sam_formula = random.choice(sam_formula_segments_single).format(
            formula_sam1=features['Formula SAM 1'],
            concentration_sam1=features['Concentration SAM 1']
        )
    elif sam1 not in ['N/A', ''] and sam2 not in ['N/A', ''] and sam3 in ['N/A', '']:
        # 前两项有效 → 双 SAM
        sam_formula = random.choice(sam_formula_segments_dual).format(
            formula_sam1=features['Formula SAM 1'],
            concentration_sam1=features['Concentration SAM 1'],
            formula_sam2=features.get('Formula SAM 2'),
            concentration_sam2=features.get('Concentration SAM 2')
        )
    else:
        # 三项或更多有效 → 三 SAM
        sam_formula = random.choice(sam_formula_segments_triple).format(
            formula_sam1=features['Formula SAM 1'],
            concentration_sam1=features['Concentration SAM 1'],
            formula_sam2=features.get('Formula SAM 2'),
            concentration_sam2=features.get('Concentration SAM 2'),
            formula_sam3=features.get('Formula SAM 3'),
            concentration_sam3=features.get('Concentration SAM 3')
        )

    parts["SAM"].append(sam_formula)
    parts["SAM"] = " ".join(parts["SAM"])

    # 6. 添加剂（若提供）
    add1, add2, add3 = features.get('Formula Additive 1'), features.get('Formula Additive 2'), features.get('Formula Additive 3')
    if add1 in ['']:
        additive_formula = ""
    else:
        if add2 in [''] and add3 in ['']:
            additive_formula = random.choice(additive_formula_segments_single).format(
                formula_add1=features['Formula Additive 1'],
                concentration_add1=features['Concentration Additive 1'],
        )
        elif add3 in ['']:
            additive_formula = random.choice(additive_formula_segments_dual).format(
                formula_add1=features['Formula Additive 1'],
                concentration_add1=features['Concentration Additive 1'],
                formula_add2=features['Formula Additive 2'],
                concentration_add2=features['Concentration Additive 2'],
        )
        else:
            additive_formula = random.choice(additive_formula_segments_triple).format(
                formula_add1=features['Formula Additive 1'],
                concentration_add1=features['Concentration Additive 1'],
                formula_add2=features['Formula Additive 2'],
                concentration_add2=features['Concentration Additive 2'],
                formula_add3=features['Formula Additive 3'],
                concentration_add3=features['Concentration Additive 3']
        )

    parts["Additive"].append(additive_formula)
    parts["Additive"] = " ".join(parts["Additive"])

    

    # 7. 钝化（若提供 材料 + 工艺）
    pass1, pass2, pass3 = features.get('Formula Passivator 1'), features.get('Formula Passivator 2'), features.get('Formula Passivator 3')
    if pass1 in ['']:
        passivation_formula = ""
        passivation_spin = ""
        passivation_drop = ""
        passivation_anneal = ""
    else:
        if pass2 in [''] and pass3 in ['']:
            passivation_formula = random.choice(passivation_material_segments_single).format(
                formula_passivator1=features['Formula Passivator 1'],
                concentration_passivator1=features['Concentration Passivator 1']
            )
            passivation_spin = random.choice(passivation_spin_segments).format(
                spin_speed_passivator=features['Spin Coating Speed Passivator'],
                spin_time_passivator=features['Spin Coating Time Passivator']
            )
            passivation_drop = random.choice(passivation_drop_segments).format(
                passivator_timing=features['Passivator Dropping Timing'],
                passivator_volume=features['Passivator Volume']
            )
            passivation_anneal = random.choice(passivation_anneal_segments).format(
                anneal_temp_passivator=features['Annealed Temperature Passivator'],
                anneal_time_passivator=features['Annealed Time Passivator']
            )
        elif pass3 in ['']:
            passivation_formula = random.choice(passivation_material_segments_dual).format(
                formula_passivator1=features['Formula Passivator 1'],
                concentration_passivator1=features['Concentration Passivator 1'],
                formula_passivator2=features['Formula Passivator 2'],
                concentration_passivator2=features['Concentration Passivator 2']
            )
            passivation_spin = random.choice(passivation_spin_segments).format(
                spin_speed_passivator=features['Spin Coating Speed Passivator'],
                spin_time_passivator=features['Spin Coating Time Passivator']
            )
            passivation_drop = random.choice(passivation_drop_segments).format(
                passivator_timing=features['Passivator Dropping Timing'],
                passivator_volume=features['Passivator Volume']
            )
            passivation_anneal = random.choice(passivation_anneal_segments).format(
                anneal_temp_passivator=features['Annealed Temperature Passivator'],
                anneal_time_passivator=features['Annealed Time Passivator']
            )
        else:
            passivation_formula = random.choice(passivation_material_segments_triple).format(
                formula_passivator1=features['Formula Passivator 1'],
                concentration_passivator1=features['Concentration Passivator 1'],
                formula_passivator2=features['Formula Passivator 2'],
                concentration_passivator2=features['Concentration Passivator 2'],
                formula_passivator3=features['Formula Passivator 3'],
                concentration_passivator3=features['Concentration Passivator 3']
            )
            passivation_spin = random.choice(passivation_spin_segments).format(
                spin_speed_passivator=features['Spin Coating Speed Passivator'],
                spin_time_passivator=features['Spin Coating Time Passivator']
            )
            passivation_drop = random.choice(passivation_drop_segments).format(
                passivator_timing=features['Passivator Dropping Timing'],
                passivator_volume=features['Passivator Volume']
            )
            passivation_anneal = random.choice(passivation_anneal_segments).format(
                anneal_temp_passivator=features['Annealed Temperature Passivator'],
                anneal_time_passivator=features['Annealed Time Passivator']
            )
    parts["Passivator"].append(passivation_formula)
    parts["Passivator"].append(passivation_spin)
    parts["Passivator"].append(passivation_drop)
    parts["Passivator"].append(passivation_anneal)

    parts["Passivator"] = " ".join(parts["Passivator"])

    if features['Spin Coating Speed Passivator'] == "":
        return parts

    single_coating = random.choice(sam_spin_anneal_segments).format(
        spin_speed_sam=features['Spin Coating Speed Passivator'],
        spin_time_sam=features['Spin Coating Time Passivator'],
        anneal_temp_sam=features['Annealed Temperature Passivator'],
        anneal_time_sam=features['Annealed Time Passivator']
    )
    parts["Single_Coating"].append(single_coating)
    parts["Single_Coating"] = " ".join(parts["Single_Coating"])

    return parts

if __name__ == '__main__':
    """
    from perovskite_text_generator import generate_text
    sample_features = {....}
    text = generate_text(sample_features)
    """
    sample_features = {
        'PCE': 23.1, 'FF': 77.4, 'Voc': 1.06, 'Jsc': 25.0,
        'Formula PVK': 'FA0.9MA0.1PbI3', 'Concentration PVK': 1.2,
        'Formula SAM 1': 'PTAA', 'Concentration SAM 1': 0.5,
        'Formula SAM 2': '', 'Concentration SAM 2': '',
        'Formula SAM 3': '', 'Concentration SAM 3': '',
        'Formula Additive 1': 'MACl', 'Concentration Additive 1': 1.0,
        'Formula Additive 2': '', 'Concentration Additive 2': '',
        'Formula Additive 3': '', 'Concentration Additive 3': '',
        'Spin Coating Speed PVK 1': 1000, 'Spin Coating Time PVK 1': 10,
        'Spin Coating Speed PVK 2': 4000, 'Spin Coating Time PVK 2': 30,
        'Antisolvent Volume': 200, 'Antisolvent Dropping Timing': 10,
        'Annealed Temperature PVK': 100, 'Annealed Time PVK': 10,
        'Formula Passivator 1': 'PCBM', 'Concentration Passivator 1': 10,
        'Formula Passivator 2': '', 'Concentration Passivator 2': '',
        'Formula Passivator 3': '', 'Concentration Passivator 3': '',
        'Spin Coating Speed Passivator': 3000, 'Spin Coating Time Passivator': 20,
        'Passivator Dropping Timing': 100, 'Passivator Volume': 5,
        'Annealed Temperature Passivator': 80, 'Annealed Time Passivator': 5
    }
    print(generate_text(sample_features))
