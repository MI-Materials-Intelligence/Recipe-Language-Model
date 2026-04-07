import random

metric_full_map = {
    "PCE": "power conversion efficiency (PCE)",
    "Voc": "open-circuit voltage (VOC)",
    "Jsc": "short-circuit current density (JSC)",
    "FF": "fill factor (FF)"
}

Q_passivator_combination_templates = [
    "What effect do surface passivators have on the {metrics} of perovskite solar cells?",
    "How do surface passivators influence the {metrics} in perovskite solar cell performance?",
    "Which surface passivators are known to improve the {metrics} during the fabrication of perovskite devices?",
    "What role do surface passivation materials play in optimizing the {metrics} of perovskite solar cells?",
    "How can surface passivators simultaneously enhance the {metrics} in perovskite solar cells?",
    "Which classes of surface passivators are effective in improving the {metrics} through defect passivation or interface engineering?",
    "In what ways do surface passivators contribute to enhancing the {metrics} of perovskite photovoltaic devices?",
    "What is the role of surface passivator chemical structure in boosting the {metrics} of perovskite solar cells?",
    "Which types of surface passivators play a critical role in raising the {metrics} of perovskite solar devices?",
    "What mechanisms underlie the improvements of {metrics} induced by surface passivator treatments in perovskite cells?",
]

Q_SAM_combination_templates = [
    "What effect do SAMs have on the {metrics} of perovskite solar cells?",
    "How do SAMs influence the {metrics} in perovskite solar cell performance?",
    "Which SAMs are known to improve the {metrics} during the fabrication of perovskite devices?",
    "What role do self-assembled monolayers play in optimizing the {metrics} of perovskite solar cells?",
    "How can SAM treatments simultaneously enhance the {metrics} in perovskite solar cells?",
    "Which classes of SAMs are effective in improving the {metrics} through interface modification?",
    "In what ways do SAMs contribute to enhancing the {metrics} of perovskite photovoltaic devices?",
    "What is the role of SAM molecular design in boosting the {metrics} of perovskite solar cells?",
    "Which types of SAMs play a critical role in raising the {metrics} of perovskite solar devices?",
    "What mechanisms underlie the improvements of {metrics} induced by SAM treatments in perovskite cells?",
]

Q_Additive_combination_templates = [
    "What effect do precursor additives have on the {metrics} of perovskite solar cells?",
    "How do precursor additives influence the {metrics} in perovskite solar cell performance?",
    "Which precursor additives are known to improve the {metrics} during the fabrication of perovskite devices?",
    "What role do precursor additive materials play in optimizing the {metrics} of perovskite solar cells?",
    "How can precursor additives simultaneously enhance the {metrics} in perovskite solar cells?",
    "Which types of precursor additives are effective in improving the {metrics} through crystallization regulation or defect suppression?",
    "In what ways do precursor additives contribute to enhancing the {metrics} of perovskite photovoltaic devices?",
    "What is the role of precursor additive molecular structure in boosting the {metrics} of perovskite solar cells?",
    "Which categories of precursor additives play a critical role in raising the {metrics} of perovskite solar devices?",
    "What mechanisms underlie the improvements of {metrics} induced by precursor additive treatments in perovskite cells?",
]

def get_intro_segment(pce, ff, voc, jsc, prepared_term="was fabricated"):
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
        "The combined treatment featured a PCE of {pce}%, FF of {ff}%, Voc of {voc} V, and Jsc of {jsc} mA/cm².", 
        "Consequently, the device resulted in device efficiency of {pce}%, together with an enhanced fill factor (FF) of {ff}%, short-circuit current density of {jsc} mA/cm²and open circuit voltage (VOC) of {voc} V.",
        "The PCE reached for the device was {pce}%, with a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}%." , 
        "With this engineering, the resulting PSCs obtained a PCE of {pce}%, a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm²." , 
        "The control device displays a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}%, turning out a moderate PCE of {pce}%." , # 
        "The device shows the highest PCE of {pce}% with negligible hysteresis, a VOC of {voc} V, a JSC of {jsc} mA/cm² and a FF of {ff}%." , 
        " The device achieves a notably enhanced PCE of {pce}%, corresponding to a JSC of {jsc} mA/cm², a VOC of {voc} V, and an FF of {ff}%. " , 
        "The PSCs exhibited a superior PCE of {pce}% (JSC: {jsc} mA/cm², VOC: {voc} V, FF: {ff}%).",  
        "The target device achieved a champion PCE of {pce}% (VOC: {voc} V, JSC: {jsc} mA/cm², FF: {ff}%)."  
        "The target PSCs achieved an average power conversion efficiency (PCE) of {pce}% with a short-circuit current density (JSC) of {jsc} mA/cm², an open-circuit voltage (VOC) of {voc} V and a fill factor (FF) of {ff}%." , 
        "The best performance, which showed {pce}% certificated efficiency with a VOC of {voc} V, a JSC of {jsc} mA/cm², and a FF of {ff}%." , 
        "The PSCs achieved a champion power conversion efficiency (PCE) of {pce}% under an active area of 0.09 cm², with a VOC value of {voc} V, an FF value of {ff}%, and a current density (JSC) of {jsc} mA/cm².", 
        "The PCE devices reached {pce}% and featured a VOC of {voc} V, FF of {ff}%, and short-circuit current density (JSC) of {jsc} mA/cm².",  
        "The inverted devices achieved optimal PCEs of {pce}%, a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  
        "The resulting hybrid SAMs-modified PSC achieve a champion PCE of {pce}%, with VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm²." , 
        "PSCs based on additives achieved a PCE of {pce}%, with a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  
        "A higher PCE of {pce}% of the target device is achieved, where JSC, VOC and FF are {jsc} mA/cm², {voc} V and {ff}%, respectively.",  
        "The champion device fabricated by perovskite film showed a PCE of {pce}% with open-circuit voltage (VOC) of {voc} V, short current density (JSC) of {jsc} mA/cm², and a fill factor (FF) of {ff}%.", 
        "Remarkably, it achieved an impressive PCE of {pce}% with a high VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",  
        "The performance parameters (PCE, open-circuit voltage (VOC), short-circuit current density (JSC) and fill factor (FF)) of the control PSCs are significantly improved ({pce}%, {voc} V, {jsc} mA/cm², and {ff}%)." , 
        "The device achieved a remarkable PCE of {pce}%, with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",  
        "The device demonstrated a champion efficiency of {pce}%, with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%."  
        "The device achieved a champion PCE of {pce}% with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",  
        "The solar cells showed a champion PCE of {pce}% with a VOC of {voc} V, a JSC of {jsc} mA/cm², and a FF of {ff}%." , 
        "A champion PCE of {pce}% with a JSC of {jsc} mA/cm², a VOC of {voc} V, and a FF of {ff}% was achieved with optimized perovskite layer prepared with non-stoichiometric precursor solution (NSPS)." , 
        "The device exhibited a PCE of {pce}%, with VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm²." , 
        "The champion device showed a PCE of {pce}%, with JSC of {jsc} mA/cm², FF of {ff}%, and VOC of {voc} V." , 
        "The resulting hybrid SAMs-modified PSC achieve a champion PCE of {pce}%, with VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm²." , 
        "PSCs based on additives achieved a PCE of {pce}%, with a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  
        "With the improved uniformity of SAM, the SAM-based devices showed a maximum PCE of {pce}%, with a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  
        "The inverted devices based on perovskite achieved optimal PCEs of {pce}%, a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  
        "The control device displays a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}%, tuning out a PCE of {pce}%.",  
        "The PSCs achieved a quasi-steady-state PCE of {pce}% (VOC: {voc} V, JSC: {jsc} mA/cm², FF: {ff}%).",  
        "The inverted PSCs achieved a champion PCE of {pce}% with an open-circuit voltage (VOC) of {voc} V, short-circuit current density (JSC) of {jsc} mA/cm², and fill factor (FF) of {ff}%.",  
        "The champion device showed a JSC of {jsc} mA/cm², a VOC of {voc} V, and a FF of {ff}%, resulting in a PCE of {pce}%.",  
        "The champion target devices showed a JSC of {jsc} mA/cm², a VOC of {voc} V, and a FF of {ff}%, resulting in a PCE of {pce}%.", 
        "The device showed the highest certified PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%."  
        "The device shows a maximum PCE of {pce}%, with an open-circuit voltage (VOC) of {voc} V, a short-circuit current density (JSC) of {jsc} mA/cm², and a fill factor (FF) of {ff}%.",
        "PSCs with (111)-preferred crystallographic orientation displayed a remarkable PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",
        "The target PSCs achieved an average power conversion efficiency (PCE) of {pce}% with a short-circuit current density (JSC) of {jsc} mA/cm², an open-circuit voltage (VOC) of {voc} V, and a fill factor (FF) of {ff}%.",
        "The best performance device showed a {pce}% certificated efficiency with a VOC of {voc} V, a JSC of {jsc} mA/cm², and a FF of {ff}%.",
        "The PSCs achieved a champion power conversion efficiency (PCE) of {pce}%, with VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².", 
        "The PCE of devices reached {pce}%, featuring VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",  
        "The devices exhibited an increased PCE from {pce}% to {pce}%, with a VOC of {voc} V, FF of {ff}%, and JSC of {jsc} mA/cm².",
        "The champion device offers a high PCE of {pce}% for the reverse scan (JSC of {jsc} mA/cm², VOC of {voc} V, and FF of {ff}%).",
        "A higher PCE of {pce}% is achieved with JSC of {jsc} mA/cm², VOC of {voc} V, and FF of {ff}%.",  
        "The PCE for the device reached {pce}%, with a JSC of {jsc} mA/cm², a VOC of {voc} V and a FF of {ff}%.",  
        "PSC with device efficiency (PCE) of {pce}%, VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}% was obtained.",
        "This resulted in improved performance with a PCE beyond {pce}%, a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}%.",
        "The fabricated device resulted in a PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.", 
        "The certified PCE was determined to be {pce}% with JSC of {jsc} mA/cm², VOC of {voc} V, and FF of {ff}%.",
        "A PCE of {pce}% with a VOC of {voc} V, a JSC of {jsc} mA/cm², and an FF of {ff}% was obtained.",  
        "The PSCs demonstrated improved PCE of {pce}% (with FF of {ff}%, VOC of {voc} V, and JSC of {jsc} mA/cm²).", 
        "The PSCs demonstrated a champion PCE of {pce}%, with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.", 
        "The PCE of the device was increased to {pce}% with an FF of {ff}%, VOC of {voc} V and JSC of {jsc} mA/cm².",
        "The champion PCE of the device can be further improved to {pce}% (VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%).",
        "PSCs with a PCE of {pce}%, a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}% are demonstrated.",
        "A significantly higher JSC of {jsc} mA/cm² is obtained while preserving VOC of {voc} V and FF of {ff}%, resulting in the highest PCE of {pce}% at reverse scan.",
        "The current density-voltage (J-V) characteristics show that the target PSCs delivered a PCE of {pce}%, with an elevated VOC of {voc} V, a JSC of {jsc} mA/cm², and an FF of {ff}%.",
        "The cells showed an increase in VOC to {voc} V, accompanied by a slight increase in FF to {ff}% and JSC to {jsc} mA/cm², resulting in a peak PCE of {pce}%.",
        "The device shows the highest PCE of {pce}% with a VOC of {voc} V, a JSC of {jsc} mA/cm², and an FF of {ff}%.",
        "In contrast, the device achieves a notably enhanced PCE of {pce}%, with a JSC of {jsc} mA/cm², VOC of {voc} V, and FF of {ff}%.", 
        "The PSCs exhibited a superior PCE of {pce}% (JSC: {jsc} mA/cm², VOC: {voc} V, FF: {ff}%).",  
        "The PSC device gives the highest PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.", 
        "The device achieved an impressive PCE of {pce}% with an open-circuit voltage of {voc} V, short-circuit current density of {jsc} mA/cm², and fill factor of {ff}%.", 
        "The champion device achieved a remarkable power conversion efficiency (PCE) of {pce}%, with a VOC of {voc} V, a JSC of {jsc} mA/cm², and a FF of {ff}%, outperforming devices modified with other SAMs.",
        "The PSCs show a champion PCE of {pce}% with VOC of {voc} V, JSC of {jsc} mA/cm² and FF of {ff}%.",  
        "The solar cells showed a drastically enhanced VOC, which led to a maximum efficiency of {pce}% (with FF of {ff}%, JSC of {jsc} mA/cm², and VOC of {voc} V).",
        "The champion device achieves an outstanding PCE of {pce}%, with a VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%, marking a significant improvement over the control device.",
        "The device achieves a champion PCE of {pce}% with an open-circuit voltage (VOC) of {voc} V, a short-circuit current (JSC) of {jsc} mA/cm², and a fill factor (FF) of {ff}%.",
        "The device displayed a champion PCE of {pce}%, with a VOC of {voc} V, a JSC of {jsc} mA/cm², and an FF of {ff}%.",
        "The PSCs displayed a significantly enhanced PCE of {pce}%, with VOC of {voc} V, JSC of {jsc} mA/cm², and FF of {ff}%.",

    ]
    template = random.choice(intro_segments)
    return template.format(prepared_term=prepared_term, pce=pce, ff=ff, voc=voc, jsc=jsc)


# Perovskite Formula Segments
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
    "The composition of perovskite is {concentration_pvk} mol/L {formula_pvk}.", 
    "The {formula_pvk} ({concentration_pvk} mol/L) perovskite precursor solution was prepared.", 
    "The perovskite composition is {formula_pvk}, and the initial stock perovskite solution is {concentration_pvk} mol/L.", 
    "The perovskite precursor is {formula_pvk}.", 
    "The {concentration_pvk} mol/L perovskite precursor solution with a chemical formula of {formula_pvk}.", 
    "The perovskite precursor solutions were prepared by dissolving {concentration_pvk} mol/L {formula_pvk}.", 
    "{concentration_pvk} mol/L {formula_pvk} perovskite precursors were prepared.", 
    "For the perovskite composition {formula_pvk}, {concentration_pvk} mol/L perovskite precursor solution was prepared.", 
    "The {concentration_pvk} mol/L perovskite solution ({formula_pvk}) was prepared, shaken overnight to fully dissolve, and then used to prepare perovskite films.", 
    "The perovskite precursor solution ({formula_pvk}) was prepared with a concentration of {concentration_pvk} mol/L in a mixed anhydrous solvent of DMF/DMSO (4/1, v/v).", 
    "The perovskite ({formula_pvk}) solution was prepared with a concentration of {concentration_pvk} mol/L in mixed solvent of DMF and DMSO.", 
    "Then, perovskite precursor solution ({concentration_pvk} mol/L) was prepared at the stoichiometric ratio of {formula_pvk}.", 
    "A {concentration_pvk} mol/L perovskite precursor solution was constructed by mixing FAI, PbI2, methylammonium iodide and caesium iodide in DMF: DMSO mixed solvent with the chemical formula of {formula_pvk}.",  
    "For the inorganic perovskite layers, {concentration_pvk} mol/L {formula_pvk} inorganic perovskite precursor solution was prepared in DMF/DMSO solvent.",  
    "The perovskite precursor solution was prepared with a concentration of {concentration_pvk} mol/L using PbI2 and MAI dissolved in a mixed DMF/DMSO solvent.",  
    "The perovskite ({formula_pvk}) precursor solution was prepared with a concentration of {concentration_pvk} mol/L in a mixed solvent of DMF and DMSO.",  
    "The mixed perovskite ({formula_pvk}) precursor solution was prepared with a total concentration of {concentration_pvk} mol/L in DMF/DMSO co-solvent.",  
    "The perovskite precursor solution was prepared based on the perovskite composition of {formula_pvk} in DMF/DMSO solvent (total concentration of {concentration_pvk} mol/L).",  
    "The perovskite precursor solution ({concentration_pvk} mol/L) was prepared in a solvent mixture of DMF and DMSO according to the formula of {formula_pvk}.",  
    "The perovskite solution ({concentration_pvk} mol/L) was made according to the composition of {formula_pvk} in a mixed solvent of DMF/DMSO.",  
    "The perovskite precursor solution ({formula_pvk}) was prepared with a concentration of {concentration_pvk} mol/L in a mixed anhydrous solvent of DMF/DMSO.",  
    "The perovskite ({formula_pvk}) solution was prepared with a concentration of {concentration_pvk} mol/L in mixed solvent of DMF and DMSO.",  
    "The {concentration_pvk} mol/L perovskite solution ({formula_pvk}) was prepared, shaken overnight to fully dissolve, and then used to prepare perovskite films.",  
    "For the perovskite composition {formula_pvk}, {concentration_pvk} mol/L perovskite precursor solution was prepared.",  
    "The precursor solutions for all {formula_pvk} films were prepared by dissolving equimolar concentrations ({concentration_pvk} mol/L).",  
    "The perovskite precursor solution ({concentration_pvk} mol/L, {formula_pvk}) was prepared.",  
    "{concentration_pvk} mol/L perovskite precursor solutions were prepared with the chemical formula of {formula_pvk}.",  
    "For the perovskite film, {concentration_pvk} mol/L precursor solution was prepared according to the chemical formula of {formula_pvk}.",  
    "The {formula_pvk} precursor solution ({concentration_pvk} mol/L) was prepared in the mixed solvent of DMF and DMSO.",  
    "The perovskite precursor solution ({concentration_pvk} mol/L) was prepared in mixed solvents of DMF and DMSO according to chemical formula of {formula_pvk}.",  
    "The perovskite precursor solution ({concentration_pvk} mol/L) composed of a formula of {formula_pvk}.",  
    "The perovskite solution ({concentration_pvk} mol/L) was prepared according to chemical formula of {formula_pvk}.",  
    "The {formula_pvk} perovskite film was prepared with a concentration of {concentration_pvk} mol/L.",  
    "The {concentration_pvk} mol/L perovskite precursor solution with a chemical formula of {formula_pvk} was prepared.",  
    "The perovskite precursor solutions were prepared using {concentration_pvk} mol/L {formula_pvk}.",  
    "{concentration_pvk} mol/L {formula_pvk} perovskite precursors were prepared.",  
    "For the preparation of perovskite precursor solution, {concentration_pvk} mol/L {formula_pvk} perovskite precursor was prepared in DMF:DMSO (4:1 volume ratio, v:v) mixed solvent.",  
    "Perovskite precursor solution ({concentration_pvk} mol/L) was prepared based on the stoichiometric ratio of {formula_pvk}.",  
    "The {formula_pvk} perovskite precursor ({concentration_pvk} mol/L) was spin-coated onto the substrate.",  
    "The {formula_pvk} ({concentration_pvk} mol/L) perovskite precursor solution was prepared.",  
    "{formula_pvk} was prepared at a concentration of {concentration_pvk} mol/L.",  
    "The perovskite composition was {formula_pvk}, and the initial stock perovskite solution was {concentration_pvk} mol/L.",  
    "The composition of perovskite is {concentration_pvk} mol/L {formula_pvk}.",  
    "The perovskite solution, {concentration_pvk} mol/L {formula_pvk} was prepared.",  
    "The composition of the {concentration_pvk} mol/L perovskite film is {formula_pvk}.",  
    "The perovskite composition of {formula_pvk} was prepared with a concentration of {concentration_pvk} mol/L.",  
    "The perovskite precursor solution with a molar concentration of {concentration_pvk} mol/L was prepared according to the formula of {formula_pvk}.",  
    "The composition of the {concentration_pvk} mol/L perovskite film is {formula_pvk}.",  
    "A {concentration_pvk} mol/L {formula_pvk} precursor solution was similarly prepared using a mixture of DMF and DMSO.",  
    "{concentration_pvk} mol/L perovskite precursor solution with the composition of {formula_pvk} was prepared.",  
    "For the {formula_pvk}, {concentration_pvk} mol/L perovskite precursor solution was prepared.",  
    "For perovskite film, the solution concentration of {formula_pvk} was {concentration_pvk} mol/L.",  

]

# SAM Formula Segments
sam_formula_segments_single = [
    "The SAM material {formula_sam1} ({concentration_sam1} mg/mL) was subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.", # 1
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM was carried out to improve layer formation and refine the film’s interfacial structure.",  # 2
    "SAM material {formula_sam1} ({concentration_sam1} mg/mL) was added to the perovskite solution to fine-tune the interface and stabilize the perovskite layer.",  # 3
    "The SAM material {formula_sam1} ({concentration_sam1} mg/mL) was introduced to enhance interfacial properties and improve device performance.",  # 4
    "Controlled addition of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM was performed to stabilize the perovskite layer and engineer a more robust interface.",  # 5
    "SAM material {formula_sam1} ({concentration_sam1} mg/mL) was added to influence crystal growth at the interface and optimize surface passivation.",  # 6
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM improved morphological and electronic interfaces.", # 7
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM was performed to optimize surface passivation and ensure improved interface quality.",  # 8
    "Careful addition of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM ensured improved interface quality.",  # 9
    "Incorporating {formula_sam1} ({concentration_sam1} mg/mL) as a SAM was critical to adjust interfacial energy levels and refine the perovskite interface.",  # 10
    "Adding {formula_sam1} ({concentration_sam1} mg/mL) as a SAM improved the charge extraction at the interface.",  # 11
    "A SAM solution, consisting of {formula_sam1} ({concentration_sam1} mg/mL), was added to facilitate a stable perovskite interface.",  # 12
    "Integrating {formula_sam1} ({concentration_sam1} mg/mL) as a SAM tailored the interfacial environment, contributing to a more uniform and well-ordered perovskite interface.",  # 13
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM improved interface quality and subsequently device performance.",  # 14
    "A SAM consisting of {formula_sam1} ({concentration_sam1} mg/mL) was incorporated to achieve a more uniform and well-ordered perovskite interface.",  # 15
    "The SAM consisting of {formula_sam1} ({concentration_sam1} mg/mL) was subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",  # 16
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) as a SAM enhanced interface layer formation and refined the film’s interfacial structure.",  # 17
    "For the SAM solution, {formula_sam1} ({concentration_sam1} mg/mL) was added to the previous solution.",  # 18  
    "The {formula_sam1} solution was prepared with a concentration of {concentration_sam1} mg/mL.",  # 19 
    "{concentration_sam1} mg/mL of {formula_sam1} was added.",  # 20 
    "A SAM solution consisting of {formula_sam1} ({concentration_sam1} mg/mL) in solvent was prepared.",  # 21 
    "The optimal SAM was prepared by using {formula_sam1} ({concentration_sam1} mg/mL).",  # 22 
    "The sample of {formula_sam1} was fabricated with a concentration of {concentration_sam1} mg/mL.",  # 23  
    "Different concentrations of {formula_sam1} were added into the perovskite precursor solution for modification.",  # 24  
    "The {formula_sam1} solution was prepared with a concentration of {concentration_sam1} mg/mL.",  # 25  
]

sam_formula_segments_dual = [
    "Two SAM materials of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",  # 1
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were carried out to improve layer formation and refine the film’s interfacial structure.",  # 2
    "SAM materials of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were added to the perovskite solution to fine-tune the interface and stabilize the perovskite layer.",  # 3
    "A combination of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were introduced to enhance interfacial properties and improve device performance.",  # 4
    "Controlled addition of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were performed to stabilize the perovskite layer and engineer a more robust interface.",  # 5
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were added to influence crystal growth at the interface and optimize surface passivation.",  # 6
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs improved morphological and electronic interfaces.",  # 7
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were performed to optimize surface passivation and ensure improved interface quality.",  # 8
    "Careful addition of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs ensured an improved interface quality.",  # 9
    "Incorporating {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs were critical to adjust interfacial energy levels and refine perovskite interface.",  # 10
    "Adding {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs improved the charge extraction at the interface.",  # 11
    "SAMs mixture, consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL), were added to facilitate stable perovskite interface.",  # 12
    "Integrating {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs tailored the interfacial environment, contributing to a more uniform and well-ordered perovskite interface.",  # 13
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs enabled the improvement in interface quality, and subsequently device performance.",  # 14
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were incorporated to achieve a more uniform and well-ordered perovskite interface.",  # 15
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",  # 16
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) as SAMs enabled the improvement in interface layer formation, further refining the film’s interfacial structure.",  # 17
    "For the SAM solution, {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were added to the previous solution.",  # 18  
    "The {formula_sam1} and {formula_sam2} solution were prepared with a concentration of {concentration_sam1} mg/mL and {concentration_sam2} mg/mL.",  # 19 
    "{concentration_sam1} mg/mL of {formula_sam1} and {concentration_sam2} mg/mL of {formula_sam2} were added.",  # 20 
    "Mixed SAMs solution, consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) in ethanol were prepared.",  # 21 
    "The optimal hybrid SAMs were prepared by mixing {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL).",  # 22 
    "The {formula_sam1} concentration is {concentration_sam1} mg/mL and {formula_sam2} concentration is {concentration_sam2} mg/mL.",  # 23  
    "The {formula_sam1} concentration is {concentration_sam1} mg/mL and {formula_sam2} concentration is {concentration_sam2} mg/mL.",  # 24  
]

sam_formula_segments_triple = [
    "Three SAM materials of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",  # 1
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were carried out to improve layer formation and refine the film’s interfacial structure.",  # 2
    "SAM materials of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were added to the perovskite solution to fine-tune the interface and stabilize the perovskite layer.",  # 3
    "A combination of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were introduced to enhance interfacial properties and improve device performance.",  # 4
    "Controlled addition of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were performed to stabilize the perovskite layer and engineer a more robust interface.",  # 5
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were added to influence crystal growth at the interface and optimize surface passivation.",  # 6
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs improved morphological and electronic interfaces.",  # 7
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were performed to optimize surface passivation and ensure improved interface quality.",  # 8
    "Careful addition of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs ensured an improved interface quality.",  # 9
    "Incorporating {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs were critical to adjust interfacial energy levels and refine perovskite interface.",  # 10
    "Adding {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs improved the charge extraction at the interface.",  # 11
    "SAMs mixture, consisting of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL), were added to facilitate stable perovskite interface.",  # 12
    "Integrating {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs tailored the interfacial environment, contributing to a more uniform and well-ordered perovskite interface.",  # 13
    "The addition of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs enabled the improvement in interface quality, and subsequently device performance.",  # 14
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were incorporated to achieve a more uniform and well-ordered perovskite interface.",  # 15
    "SAMs consisting of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were subsequently added into the perovskite solution to enhance interfacial properties and optimize device performance.",  # 16
    "The incorporation of {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) as SAMs enabled the improvement in interface layer formation, further refining the film’s interfacial structure.",  # 17
    "For the SAM solution, {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL) and {formula_sam3} ({concentration_sam3} mg/mL) were added to the previous solution.",  # 18
]

sam_formula_spin_segments_single = [
    "The sample of {formula_sam1} was fabricated by spin coating the {formula_sam1} solution with a concentration of {concentration_sam1} mg/mL.", # 1  
    "The hole transport layer (HTL) was fabricated using the SAM solution of {formula_sam1}. The {formula_sam1} concentration is {concentration_sam1} mg/mL.",  # 2  
    "A SAM solution ({concentration_sam1} mg/mL {formula_sam1}) was applied to the FTO glass substrates by spin-coating.",  # 3  
]

sam_formula_spin_segments_dual = [
    "While the sample of {formula_sam1} and {formula_sam2} were fabricated by spin coating {formula_sam1} and {formula_sam2} solution with concentration of {concentration_sam1} mg/mL and {concentration_sam2} mg/mL.",  # 1  
    "The hole transport layer (HTL) was fabricated by using the mixed SAM solution of {formula_sam1} and {formula_sam2}. The {formula_sam1} concentration is {concentration_sam1} mg/mL and {formula_sam2} concentration is {concentration_sam2} mg/mL.",  # 2 
    "A mixed SAMs solution ({concentration_sam1} mg/mL {formula_sam2} and {concentration_sam2} mg/mL) were applied to the FTO glass substrates by spin-coating.",  # 3  
]

sam_formula_spin_segments_triple = [
"The sample was fabricated by spin-coating a mixed SAM solution containing {formula_sam1} ({concentration_sam1} mg/mL), {formula_sam2} ({concentration_sam2} mg/mL), and {formula_sam3} ({concentration_sam3} mg/mL).",

]

sam_spin_anneal_segments = [
    "In details, SAM solution was spin-coated on the substrate at {spin_speed_sam} rpm for {spin_time_sam} s, and annealed at {anneal_temp_sam} °C for {anneal_time_sam} min.",
]


additive_formula_segments_single = [
    "{formula_add1} ({concentration_add1} mg/mL) was incorporated as an additive.",
    "To enhance device performance, {formula_add1} ({concentration_add1} mg/mL) was added to the perovskite solution as an additive.",
    "We add {formula_add1} ({concentration_add1} mg/mL) as an additive.",
    "{formula_add1} ({concentration_add1} mg/mL) additive was incorporated.",
    "We then add {formula_add1} ({concentration_add1} mg/mL) as an additive.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) was then completed.",
    "The controlled addition of {formula_add1} ({concentration_add1} mg/mL) additive was implemented.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) as an additive was carefully prepared.",
    "The incorporation of {formula_add1} ({concentration_add1} mg/mL) additive was ensured.",
    "Adding {formula_add1} ({concentration_add1} mg/mL) as an additive was essential for stabilizing the perovskite structure.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) enabled the achievement of smoother film surfaces.",
    "To enhance the mechanical properties of the perovskite layer, {formula_add1} ({concentration_add1} mg/mL) was utilized as an additive.",
    "The inclusion of {formula_add1} ({concentration_add1} mg/mL) additive enhanced device longevity.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) was instrumental in fine-tuning the perovskite film's optical properties.",
    "{formula_add1} was incorporated into the solution as an additive at a molar percentage of {concentration_add1} mg/mL.",
    "During solar cell device fabrication, {formula_add1} ({concentration_add1} mg/mL) was added to the precursor solution.",
    "The corresponding additive {formula_add1} was added to the precursor at a molar concentration of {concentration_add1} mg/mL.",
    "The perovskite precursor solution was prepared by mixing {concentration_add1} mg/mL of {formula_add1} additive in the solvent.",
    "To fabricate high-quality perovskite films, {formula_add1} ({concentration_add1} mg/mL) was added to the perovskite precursor solution.",
    "{formula_add1} ({concentration_add1} mg/mL) was added into the precursor solution as an additive.",
    "The perovskite solution was prepared with {formula_add1} in the molar ratio of {concentration_add1} mg/mL, dissolved in the prepared solution.",
    "An equal amount of {formula_add1} ({concentration_add1} mg/mL) was dissolved in dimethylformamide (DMF) and dimethyl sulfoxide (DMSO) with a 4:1 volume ratio.",
    "An equal amount of {formula_add1} ({concentration_add1} mg/mL) was dissolved in DMF and DMSO with an 4:1 volume ratio.",
    "For the modified solution, {formula_add1} ({concentration_add1} mg/mL) was added to the previous solution.",  
    "To prepare the precursor solution with {formula_add1} ({concentration_add1} mg/mL), the additive was added to the precursor solution.",  
    "For the additive-treated cells, {formula_add1} ({concentration_add1} mg/mL) was added into the perovskite precursor solution.",  
    "{concentration_add1} mg/mL {formula_add1} was then added as additive into the precursor solution.",  
    "{formula_add1} additive was added into the precursor solution at a concentration of {concentration_add1} mg/mL.",  
    "{formula_add1} was added into the perovskite solution as additive with a concentration of {concentration_add1} mg/mL.",  
    "The optimum amount of {formula_add1} added into the precursor solution was {concentration_add1} mg/mL.",  
    "{formula_add1} with concentration {concentration_add1} mg/mL was added into the perovskite solution.",  
    "Then {concentration_add1} mg/mL {formula_add1} was added to the perovskite precursor solution and stirred for 2 h.",  
    "For the target perovskite, {concentration_add1} mg/mL {formula_add1} was added to the precursor solution, and it was ensured that it's well mixed with the precursor.",  
    "{concentration_add1} mg/mL {formula_add1} was added in the solution to improve the film morphology.",  
    "The {formula_add1} was dissolved in the perovskite solution obtained with the molar ratio {concentration_add1} mg/mL.",  
    "{concentration_add1} mg/mL {formula_add1} was added to the perovskite precursor solution and stirred for 2 h.",  
    "{concentration_add1} mg/mL {formula_add1} was added into the mixed perovskite solution.",  
    "For the modified solution, {concentration_add1} mg/mL {formula_add1} was added to the precursor solution.",  
    "{concentration_add1} mg/mL of {formula_add1} was added.",  
    "{formula_add1} ({concentration_add1} mg/mL) was added into the perovskite precursor solution.",  
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL), the additive was added to the precursor solution." , 
]

additive_formula_segments_dual = [
    "{formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were incorporated as additives.",
    "To enhance device performance, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added to the perovskite solution as additives.",
    "We add {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL).",
    "{formula_add1} ({concentration_add1} mg/mL) and {formula_add2} {concentration_add2} mg/mL) additives were incorporated.",
    "We then add {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) as additives.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) was then completed.",
    "The controlled addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) additives was implemented.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) as additives was carefully prepared.",
    "The incorporation of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) additives was ensured.",
    "Adding {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) as additives was essential for stabilizing the perovskite structure.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) enabled the achievement of smoother film surfaces.",
    "To enhance the mechanical properties of the perovskite layer, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were utilized as additives.",
    "The inclusion of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) additives enhanced device longevity.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) was instrumental in fine-tuning the perovskite film's optical properties.",
    "{formula_add1} and {formula_add2} were incorporated into the solution as additives at molar percentages of {concentration_add1} mg/mL and {concentration_add2} mg/mL, respectively.",
    "During solar cell device fabrication, {formula_add1} ({concentration_add1} mg/mL), and {formula_add2} ({concentration_add2} mg/mL) were added to the precursor solution.",
    "The corresponding additives ({formula_add1}, {formula_add2}) were added to the precursors at molar concentration of {concentration_add1} mg/mL and {concentration_add2} mg/mL, respectively.",
    "The perovskite precursor solution was prepared by mixing {concentration_add1} mg/mL of {formula_add1}, and {concentration_add2} mg/mL of {formula_add2} additive in the solvent.",
    "To achieve the desired secondary growth solution, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were dissolved in solvent.",
    "To fabricate high-quality perovskite films, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added to the perovskite precursor solution.",
    "{formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added into both precursor solutions as additives.",
    "The perovskite solution was a mixture of {formula_add1} and {formula_add2} in the molar ratio of {concentration_add1} mg/mL and {concentration_add2} mg/mL, respectively, dissolved in the prepared solution.",
    "For the modified solution, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added to the previous solution.",  
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL), the additives were added to the precursor solution.",  
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL), the additives were added to the precursor solution.", 
    "For the additives treated cells, the {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added into the perovskite precursor solution.", 
    "Then, around {concentration_add1} mg/mL of {formula_add1} and {concentration_add2} mg/mL of {formula_add2} were also added into the mixed perovskite solution.",  
    "For the additives treated cells, the {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added into the perovskite precursor solution.",  
]

additive_formula_segments_triple = [
    "{formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were incorporated as additives.",
    "To enhance device performance, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added to the perovskite solution as additives.",
    "We add {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL).",
    "{formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) additives were incorporated.",
    "We then add {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) as additives.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) was then completed.",
    "The controlled addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) additives was implemented.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) as additives was carefully prepared.",
    "The incorporation of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) additives was ensured.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) enabled the achievement of smoother film surfaces.",
    "To enhance the mechanical properties of the perovskite layer, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were utilized as additives.",
    "The addition of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) was instrumental in fine-tuning the perovskite film's optical properties.",
    "{formula_add1}, {formula_add2} and {formula_add3} were incorporated into the solution as additives at molar percentages of {concentration_add1} mg/mL, {concentration_add2} mg/mL and {concentration_add3} mg/mL, respectively.",
    "During solar cell device fabrication, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added to the precursor solution.",
    "The corresponding additives ({formula_add1}, {formula_add2}, {formula_add3}) were added to the precursors at a concentration of {concentration_add1} mg/mL, {concentration_add2} mg/mL and {concentration_add3} mg/mL, respectively.",
    "The perovskite precursor solution is prepared by mixing {concentration_add1} mg/mL of {formula_add1}, {concentration_add2} mg/mL of {formula_add2}, and {concentration_add3} mg/mL of {formula_add3} additives in the solvent.",
    "To fabricate high-quality perovskite films, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added to the perovskite precursor solution.",
    "{formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added into both precursor solutions as additives.",
    "For the modified solution, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added to the previous solution.",  
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL), the additives were added to the precursor solution.",  
]

# Passivation Segments
passivation_material_segments_single = [
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was incorporated as passivator.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) was spin-coated onto the sample surface as a passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was added as a passivator.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was used as a passivator in the formulation.",
    "A passivation layer, {formula_passivator1} ({concentration_passivator1} mg/mL), was incorporated into the system.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) served as the passivator in this study.",
    "The passivation process involved the use of {formula_passivator1} ({concentration_passivator1} mg/mL).",
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
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was coated onto the perovskite surface.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was deposited onto the perovskite film.",
    "For the surface passivation layer, {formula_passivator1} was dissolved in IPA at a concentration of {concentration_passivator1} mg/mL.",  
    "{concentration_passivator1} mg/mL {formula_passivator1} was spin-coated onto the perovskite film.",  
    "{formula_passivator1} as passivation layer was prepared at a concentration of {concentration_passivator1} mg/mL in IPA solution.",  
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was introduced as a passivation layer prepared in an IPA mixed solution.",  
    "{concentration_passivator1} mg/mL {formula_passivator1} in isopropyl alcohol was prepared as a passivating layer.",  
    "For the interfacial passivation layer, {formula_passivator1} with the concentration of {concentration_passivator1} mg/mL in IPA was used.",  
    "{concentration_passivator1} {formula_passivator1} mg/mL was spin-coated onto the perovskite film.",  
    "Later, the {concentration_passivator1} mg/mL {formula_passivator1} (in IPA) was evenly spread on the surface of the perovskite film.",  
    "For the surface passivation layer, {formula_passivator1} was dissolved in IPA at a concentration of {concentration_passivator1} mg/mL.",  

    ]

passivation_material_segments_dual = [
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were incorporated as passivators.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spin-coated onto the sample surface as a passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were added as passivators.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were used as passivators in the formulation.",
    "A passivation layer composed of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) was incorporated into the system.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) served as passivators in this study.",
    "The passivation process involved the use of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL).",
    "To improve device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were applied as a passivation layer via spin-coating onto the sample surface.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were co-deposited as a passivation layer on the sample surface using spin-coating.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spin-coated onto the sample surface to serve as a passivation layer, thereby improving device performance.",
    "In order to boost device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were deposited onto the sample surface as a passivation layer through spin-coating.",
    "A passivation layer composed of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) was applied to the sample surface by spin-coating to enhance device performance.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were utilized as passivation materials through spin-coating to enhance device performance.",
    "Spin-coating of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) onto the sample surface was performed to improve device performance.",
    "To achieve better device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spin-coated onto the sample surface as a passivation layer.",
    "The application of a combined passivation layer composed of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) via spin-coating significantly boosted device performance.",
    "The passivators {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were introduced into the system to improve material properties.",
    "For better device performance, a passivation layer composed of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) was deposited through spin-coating.",
    "To enhance passivation performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were incorporated into the fabrication process.",
    "The passivation solution was prepared using {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL).",
    "To improve the stability of the material, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were applied onto the substrate surface as a passivation coating.",
    "To optimize device performance, {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were uniformly spin-coated onto the perovskite surface to form an effective passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spin-coated onto the perovskite film to act as an efficient passivation layer.",
    "A passivation layer composed of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) was deposited by spin-coating to improve surface quality.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were coated onto the perovskite surface.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were deposited onto the perovskite film.",
    "For the surface treatment of perovskite films, chalcogen-concave molecular stock solutions of {formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were spin-coated on the perovskite film",  
    "For the surface passivation layer, {formula_passivator1} and {formula_passivator2} were dissolved in IPA at a concentration of {concentration_passivator1} mg/mL and {concentration_passivator2} mg/mL.",  
    "For the interfacial passivation layer, {formula_passivator1} and {formula_passivator2} with the concentration of {concentration_passivator1} mg/mL and {concentration_passivator2} mg/mL were used.", 
    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were introduced as a passivation layer.", 
    ]

passivation_material_segments_triple = [
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were incorporated as passivators.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL)  were spin-coated onto the sample surface as a passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were added as passivators.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were used as passivators in the formulation.",
    "A passivation layer composed of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL), was incorporated into the system.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) served as the passivator in this study.",
    "The passivation process involved the use of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL).",
    "The incorporation of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) was used as a passivator to enhance stability.",
    "To improve device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were applied as a passivation layer via spin-coating onto the sample surface.",
    "To enhance device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were deposited as a passivation layer on the sample surface using spin-coating.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were spin-coated onto the sample surface to serve as a passivation layer, thereby improving device performance.",
    "In order to boost device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were deposited onto the sample surface as a passivation layer through spin-coating.",
    "A passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) was applied to the sample surface by spin-coating to enhance device performance.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were utilized as a passivation layer through spin-coating to enhance device performance.",
    "Spin-coating of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) onto the sample surface was performed to improve device performance.",
    "To achieve better device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were spin-coated onto the sample surface as a passivation layer.",
    "The application of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) as a passivation layer via spin-coating significantly boosted device performance.",
    "The passivators {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were introduced into the system to improve material properties.",
    "For better device performance, a passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) was deposited through spin-coating.",
    "To enhance passivation, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were incorporated into the fabrication process.",
    "The passivation solution was prepared using {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL).",
    "To improve the stability of the material, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were applied onto the substrate surface as a protective coating.",
    "To optimize the reaction efficiency, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were deposited onto the catalyst surface as a modifying layer.",
    "To optimize device performance, {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were uniformly spin-coated onto the perovskite surface to form an effective passivation layer.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were spin-coated onto the perovskite film to act as an efficient passivation layer.",
    "A passivation layer of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) was deposited by spin-coating to improve surface quality.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were coated onto the perovskite surface.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were deposited onto the perovskite film.",
    "For the surface treatment of perovskite films, chalcogen-concave molecular stock solutions of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were spin-coated onto the perovskite film.",  
]



# Process Segments
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
    "To establish a stable perovskite film, the substrate was spun at {spin1_speed} rpm for {spin1_time} s, then at {spin2_speed} rpm for {spin2_time} s, ensuring even layer formation.",
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  
    "The perovskite precursor was spin-coated onto the substrates with a two-stage program at {spin1_speed} rpm for {spin1_time} s, and {spin2_speed} rpm for {spin2_time} s, respectively.", 
    "Specifically, the perovskite precursor solution was first spun at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.", 
    "The perovskite precursor was spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", 
    "For perovskite film fabrication, the perovskite precursor was spin-coated on the as-prepared substrates at {spin1_speed} rpm for {spin1_time} s, subsequently at {spin2_speed} rpm for {spin2_time} s.", 
    "The perovskite precursor solutions were spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", 
    "Then the filtered perovskite precursor was spin-coated on the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", 
    "The perovskite film was deposited by spin-coating with {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", 
    "The perovskite solution was spin-coated in two steps, namely {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", 
    "The perovskite precursor solution was deposited on the substrate via a two-step spin coating process; first, the solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.", 
    "The precursor solution was spin-coated onto the substrate surface at {spin1_speed} rpm for {spin1_time} s, then accelerated to {spin2_speed} rpm and maintained at this speed for {spin2_time} s.", 
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", 
    "For the perovskite deposition process, the perovskite films were deposited using a two-step spin-coating process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.", 
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.", 
    "The perovskite solution was spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s, respectively.", 
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.", 
    "The precursor solution was spin-coated in a two-step process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.", 
    "The perovskite precursor solutions were spin-coated on the substrate at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.", 
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and then {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite precursor solution was then spin-coated at {spin1_speed} rpm for {spin1_time} s followed by an additional spin at {spin2_speed} rpm for {spin2_time} s.",  
    "The prepared precursor solution was spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The precursor solution was spin-coated on the substrate at {spin1_speed} rpm for {spin1_time} s and then {spin2_speed} rpm for {spin2_time} s.",  
    "The precursor solution was deposited on the substrate and spin-coated with a two-step spin-coating procedure: {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite layer was deposited via a two-step spin-coating procedure with {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite solution was spin-coated on the substrate at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s, respectively.",  
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  
    "For the perovskite films, the spin-coating process was divided into a consecutive two-step procedure: the spin rate of the first step was {spin1_speed} rpm for {spin1_time} s, and that of the second step was {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite layer was spin-coated with a two-step recipe, first at {spin1_speed} rpm for {spin1_time} s followed by {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite solution was deposited on the substrate by two consecutive spin-coating steps of {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s, subsequently at {spin2_speed} rpm for {spin2_time} s.",  
    "The spin coating procedure was done in ambient air by a consecutive two-step spin-coating process, with the first step at {spin1_speed} rpm for {spin1_time} s and the second step at {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite solution was deposited on the substrate and spun cast at {spin1_speed} rpm for {spin1_time} s followed by {spin2_speed} rpm for {spin2_time} s.",  
    "For the perovskite film fabrication, the substrate was spun at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",  
    "Then, the prepared precursor solution was spin-coated onto the ITO substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite film was deposited by spin-coating onto the substrate using a two-step spin-coating process, first at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  
    "The precursor solution was deposited on the substrate and spun cast at {spin1_speed} rpm for {spin1_time} s, followed by {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite was deposited via a two-step spin-coating procedure with {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite precursor solution was then spin-coated onto a substrate at {spin1_speed} rpm for {spin1_time} s followed by an additional spin at {spin2_speed} rpm for {spin2_time} s.",  
    "Afterwards, the perovskite precursor solution was deposited on the substrate via a two-step spin coating process; first, the solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  
    "The precursor solution was spin-coated onto the substrate surface at {spin1_speed} rpm for {spin1_time} s, then accelerated to {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "For the perovskite deposition process, the perovskite solutions were deposited using a two-step spin-coating process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s (acceleration rate 500 rpm/s) and {spin2_speed} rpm for {spin2_time} s (acceleration rate 1000 rpm/s), respectively.",  
    "The as-prepared perovskite precursor was spin-coated onto the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  
    "The precursor solution was spin-coated in a two-step process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  
    "The perovskite precursor solutions were spin-coated on the substrate at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  
    "Specifically, the perovskite precursor solution was first deposited at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  
    "The perovskite precursor solution was dripped onto the substrate, and a two-step spin-coating procedure was applied. The first step was carried out at {spin1_speed} rpm, followed by {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite was deposited via a two-step spin-coating procedure, first at {spin1_speed} rpm for {spin1_time} s and finally at {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite precursor was spin-coated onto the substrates with a two-stage program at {spin1_speed} rpm for {spin1_time} s, and {spin2_speed} rpm for {spin2_time} s, respectively.",  
    "The precursor solution was spin-coated on the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The prepared precursor solution was spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",  
    "For perovskite film fabrication, the perovskite precursor was spin-coated on the as-prepared substrates at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite precursor solutions were spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite film was deposited by spin-coating at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite solution was deposited in two steps, first at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",  
    "For the perovskite layer, the prepared perovskite solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite film was deposited by spin-coating at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
    "The perovskite precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",  
    "For the fabrication of perovskite films, the perovskite solutions were spin-coated onto the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",  
]

# Antisolvent Segments
antisolvent_segments = [
    "During the second spin-coating step, {antisolvent_volume} µL of antisolvent was introduced at last {antisolvent_timing} s.",
    "To promote better film morphology, {antisolvent_volume} µL of antisolvent was added at last {antisolvent_timing} s in the latter spin-coating step.",
    "A timed antisolvent drop ({antisolvent_volume} µL at last {antisolvent_timing} s) enhanced the perovskite crystallization kinetics.",
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
    "During the second step, antisolvent CB ({antisolvent_volume} µL) was dropped at the middle of the spinning substrate {antisolvent_timing} s prior to the end of the spinning.", 
    "During the spin-coating process, {antisolvent_volume} µL of CB was dropped on the perovskite at {antisolvent_timing} s, prior to the end of the second procedure.", 
    "{antisolvent_volume} µL CB was dropped on the perovskite film at {antisolvent_timing} s before the end of the program.", 
    "{antisolvent_volume} µL of CB as antisolvent was dripped onto the substrate quickly at the last {antisolvent_timing} s during the second spinning step.", 
    "At the last {antisolvent_timing} s, {antisolvent_volume} µL of chlorobenzene solution was dropped on the perovskite.", 
    "Then, with {antisolvent_timing} s of spin time remaining, chlorobenzene ({antisolvent_volume} µL) was dispensed onto the middle of the substrate.", 
    "At {antisolvent_timing} s before the end of the spin-coating procedure, {antisolvent_volume} µL CB was dropped onto the substrates.", 
    "During the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL of chlorobenzene (CB) was added as the antisolvent.", 
    "CB ({antisolvent_volume} µL) was dropped on the film at {antisolvent_timing} s before the end of the spinning.", 
    "A total of {antisolvent_volume} µL of CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.", 
    "{antisolvent_volume} µL chlorobenzene as antisolvent was dropped {antisolvent_timing} s before the end of the spin-coating procedure.", 
    "During the last {antisolvent_timing} s of the second step, the anti-solvent ({antisolvent_volume} µL of chlorobenzene) was dropped in the center at a constant rate", 
    "During the second step, {antisolvent_volume} µL of chlorobenzene was dropped on the spinning substrate {antisolvent_timing} s before the end of the process.", 
    "During the second spin coating step, {antisolvent_volume} µL CB was dripped onto the perovskite film at {antisolvent_timing} s before ending the program.", 
    "During the last {antisolvent_timing} s of the second step, the anti-solvent ({antisolvent_volume} µL of CB) was dropped in the center of the substrate.",  
    "{antisolvent_volume} µL CB was dripped onto the center of film at {antisolvent_timing} s before the end of the spin-coating procedure.",  
    "During the second spin coating step, {antisolvent_volume} µL of CB was deposited onto the perovskite film {antisolvent_timing} seconds before the program ended.",  
    "{antisolvent_volume} µL CB as the antisolvent was dripped on the film at {antisolvent_timing} s before the end of the last procedure.",  
    "{antisolvent_volume} µL CB was dropped onto the substrate at the last {antisolvent_timing} s of the spin-coating, resulting in the formation of dark brown films.",  
    "Then, {antisolvent_volume} µL CB was dropped onto the substrate during the second spin-coating step at the last {antisolvent_timing} s of the spin-coating.",  
    "During the spin-coating process, {antisolvent_volume} µL of CB as anti-solvent was quickly dropped onto the samples at the last time of {antisolvent_timing} s.",  
    "{antisolvent_volume} µL of antisolvent was dripped on the spinning substrate at the last {antisolvent_timing} s of the second spin-coating step.",  
    "{antisolvent_volume} µL chlorobenzene as antisolvent was dropped {antisolvent_timing} s before the end of the spin-coating procedure.",  
    "During the last {antisolvent_timing} s of the second step, the anti-solvent ({antisolvent_volume} µL of chlorobenzene) was dropped in the center.",  
    "Anti-solvent ({antisolvent_volume} µL) was dropped on the film at {antisolvent_timing} s before the end of the spinning.",  
    "At {antisolvent_timing} s before the end of the second step, {antisolvent_volume} µL of CB was drop-coated to treat the perovskite films.",  
    "At the last {antisolvent_timing} s, {antisolvent_volume} µL of anti-solvent was rapidly dropped on top of the spinning substrate.",  
    "During the second spin-coating step, {antisolvent_volume} µL of CB was quickly poured onto the substrate at the last {antisolvent_timing}.",  
    "{antisolvent_volume} µL CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",  
    "During the last step, {antisolvent_volume} µL of chlorobenzene was dropped on the film at last {antisolvent_timing} s.",  
    "In the second step, {antisolvent_volume} µL CB was dropped onto the substrate during the last {antisolvent_timing} s of the spinning.",  
    "{antisolvent_volume} µL CB was dropped onto the substrate during the last {antisolvent_timing} s of the spinning, resulting in the formation of dark brown films.",  
    "{antisolvent_volume} µL CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",  
    "During the second spin coating step, {antisolvent_volume} µL of CB was deposited onto the perovskite film {antisolvent_timing} s before the program ended.",  
    "A total of {antisolvent_volume} µL of CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",  
    "At {antisolvent_timing} s before the end of the spin-coating procedure, {antisolvent_volume} µL CB was dropped onto the substrates.",  
    "During the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL CB was dropped as antisolvent.",  
    "At {antisolvent_timing} s before the end of the spinning program, {antisolvent_volume} µL of antisolvent was dripped onto the center of the film during the second step.",  
    "During the second step, {antisolvent_volume} µL of chlorobenzene was dropped on the spinning substrate {antisolvent_timing} s before the end of the process.",  
    "{antisolvent_volume} µL of chlorobenzene was quickly poured to extract the mixed solvents at the last of {antisolvent_timing} s.",  
    "During the second spin coating step, {antisolvent_volume} µL CB was dripped onto the perovskite film at {antisolvent_timing} s before ending the program.",  
    "During the second step, antisolvent CB ({antisolvent_volume} µL) was dropped at the middle of the spinning substrate {antisolvent_timing} s prior to the end of the spinning.",  
    "During the spin-coating process, {antisolvent_volume} µL of CB was dropped on the perovskite {antisolvent_timing} s prior to the end of the second procedure.",  
    "{antisolvent_volume} µL anti-solvent was quickly dripped at the {antisolvent_timing} s before the end of spin coating step.",  
    "During the second spin coating step, {antisolvent_volume} µL of CB was deposited onto the perovskite film {antisolvent_timing} s before the program ended.",  
    "During the second step, CB as antisolvent ({antisolvent_volume} µL) was dropped at the middle of the spinning substrate {antisolvent_timing} s prior to the end of the spinning.",  
    "During the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL CB was dropped as antisolvent.",  
    "Antisolvent ({antisolvent_volume} µL) was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",  
    "{antisolvent_volume} µL CB was dropped on the perovskite film at {antisolvent_timing} s before the end of the program.",  
    "At the last {antisolvent_timing} s, {antisolvent_volume} µL of CB solution was dropped on the perovskite.",  
    "With {antisolvent_timing} s of spin time remaining, CB ({antisolvent_volume} µL) was dispensed onto the middle of the substrate.",  
    "When the countdown was {antisolvent_timing} s, {antisolvent_volume} µL CB serving as antisolvent was dropped onto the substrates.",  
    "{antisolvent_volume} µL CB was dropped {antisolvent_timing} s before the end of the procedure.",  
    "According to the antisolvent method, {antisolvent_volume} µL of antisolvent was dropped on the film {antisolvent_timing} s before the end of the program.",  
    "During the spin-coating, {antisolvent_volume} µL CB solution was dripped at {antisolvent_timing} s before the end of the spin-coating process.",  
    "{antisolvent_volume} µL of antisolvent was dropped on the film {antisolvent_timing} s before the end of the program.",  
    "CB ({antisolvent_volume} µL) was dropped at the center of the spinning substrate approximately {antisolvent_timing} s before the end of the spin coating procedure.",  
    "During the spin-coating process, {antisolvent_volume} µL of CB antisolvent was quickly dripped onto the centre of the perovskite film {antisolvent_timing} s before the end of the process.",  
    "During the second step, {antisolvent_volume} µL of CB as anti-solvent was quickly dripped onto the centre of the perovskite film {antisolvent_timing} s before the end of the spin-coating process.",  
]

# Anneal Segments
anneal_segments = [
    "The resulting films were then annealed at {anneal_temp} °C for {anneal_time} min.",
    "Subsequent thermal treatment was carried out at {anneal_temp} °C for {anneal_time} min to finalize the perovskite crystal structure.",
    "An annealing process at {anneal_temp} °C for {anneal_time} min allowed the perovskite grains to fully mature.",
    "The sample underwent a controlled anneal at {anneal_temp} °C for {anneal_time} min, optimizing the film’s morphological and crystalline properties.",
    "Thermal annealing at {anneal_temp} °C for {anneal_time} min improved crystal ordering and reduced defect density.",
    "A post-deposition anneal at {anneal_temp} °C for {anneal_time} min stabilized the absorber layer and enhanced device performance.",
    "To lock in the desired crystal phase, the film was heated at {anneal_temp} °C for {anneal_time} min.",
    "The device architecture benefited from a final anneal at {anneal_temp} °C for {anneal_time} min, ensuring robust crystallinity.",
    "Post-synthesis annealing at {anneal_temp} °C for {anneal_time} min promoted uniform grain growth and optimal device characteristics.",
    "By subjecting the film to {anneal_temp} °C for {anneal_time} min, the perovskite lattice attained its ideal orientation.",
    "The perovskite layer was thermally conditioned at {anneal_temp} °C for {anneal_time} min, consolidating its morphology.",
    "The films were then annealed at {anneal_temp} °C for {anneal_time} min.",
    "The perovskite sample was subsequently annealed at {anneal_temp} °C for {anneal_time} min.", 
    "The sample was then annealed at {anneal_temp} °C for {anneal_time} min.", 
    "The substrates were immediately transferred to the hotplate and annealed at {anneal_temp} °C for {anneal_time} min.", 
    "Afterwards, the perovskite film was annealed at {anneal_temp} °C for {anneal_time} min.", 
    "Then the film was annealed at {anneal_temp} °C for {anneal_time} min.", 
    "Heat-treatment was implemented with the substrates for {anneal_time} min at {anneal_temp} °C.", 
    "Then, the film was annealed at {anneal_temp} °C for {anneal_time} min.", 
    "The as-coated film was then annealed at {anneal_temp} °C for {anneal_time} min.", 
    "The films were then annealed at {anneal_temp} °C for {anneal_time} min.",
    "The film was immediately annealed at {anneal_temp} °C for {anneal_time} min.", 
    "After the spin coating was completed, it was annealed on a hot stage at {anneal_temp} °C for {anneal_time} min.", 
    "The substrates were sequentially heated at {anneal_temp} °C for {anneal_time} min for perovskite crystal formation.", 
    "The perovskite film was annealed at {anneal_temp} °C for {anneal_time} min.", 
    "The wet film was annealed at {anneal_temp} °C for {anneal_time} min.", 
    "Then, the precursor films were placed on a {anneal_temp} °C hotplate for {anneal_time} min.",  
    "The deposited perovskite films were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",  
    "The resulting wet perovskite films were annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The film was subsequently annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The film was then annealed at {anneal_temp} °C for {anneal_time} min.",  
    "After spin-coating, the films were annealed on the hot plate at {anneal_temp} °C for {anneal_time} min.",  
    "After the whole spin-coating process, the substrate was annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The samples were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",  
    "Subsequently, the samples were annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The perovskite was annealed at {anneal_temp} °C for {anneal_time} min.",  
    "After the spin coating was completed, it was annealed on a hot stage at {anneal_temp} °C for {anneal_time} min.",  
    "The film was immediately annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The deposited perovskite films were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",  
    "Then the films were annealed at {anneal_temp} °C for {anneal_time} min to form the perovskite layer.",  
    "Then, the as-prepared perovskite films were transferred onto a hotplate and annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The films were dried inside an N2 environment on a hot plate at a temperature of {anneal_temp} °C for {anneal_time} min.",  
    "Subsequently, the as-deposited films were annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The films were then dried on a hot plate at {anneal_temp} °C for {anneal_time} min.",  
    "Next, the substrates were quickly transferred for annealing at {anneal_temp} °C for {anneal_time} min.",  
    "The substrate was immediately placed on a hotplate and annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The wet perovskite films were then transferred onto a hot plate and annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The films were then annealed on a hot plate at {anneal_temp} °C for {anneal_time} min.",  
    "The deposited perovskite films were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",  
    "The resulting wet perovskite films were annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The as-coated film was then annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The perovskite film was obtained by annealing at {anneal_temp} °C for {anneal_time} min.",  
    "The substrates were sequentially heated at {anneal_temp} °C for {anneal_time} min for perovskite crystal formation.",  
    "After the spin coating was completed, it was annealed at {anneal_temp} °C for {anneal_time} min.",  
    "Subsequently, the sample was annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The resulting wet perovskite films were annealed at {anneal_temp} °C for {anneal_time} min.",  
    "It was then heated at {anneal_temp} °C for {anneal_time} min, resulting in the formation of the perovskite thin films.",  
    "The substrates were immediately transferred to the hotplate and annealed at {anneal_temp} °C for {anneal_time} min.",  
    "The substrate was then transferred to a thermostatic heater and annealed at {anneal_temp} °C for {anneal_time} min.",  
    "Then the substrate was annealed at {anneal_temp} °C for {anneal_time} min to form the perovskite layer.",  
    "The resulting perovskite film was then annealed at {anneal_temp} °C for {anneal_time} min.",  
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
    "The spin coating was performed at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "For the surface treatment of perovskite films, the passivators were spin-coated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "Then passivators were spin-coated onto the as-prepared perovskite films at a speed of {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "For passivator treatment, the passivators were spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "Then it was spin-coated on the cooled perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "For the surface passivation, passivators were spin-coated on perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "Then, the passivation solution was spin-coated on top of the as-prepared perovskite at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "After cooling to room temperature, passivators were deposited by spin-coating with {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "For the passivation treatment, passivators were spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "Afterwards, passivators were deposited on the perovskite film by spin-coating at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "Subsequently, the passivation solution was dropped on the annealed perovskite films during a spin-coating procedure at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "The passivation mixed solution was spin-coated on the perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "It was spin-coated on top of perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "It was then spin-coated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "It was deposited on the surface of the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "A passivation solution was deposited on the perovskite layer by spin coating at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "The passivation solution was dynamically spin-coated on the annealed perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.", 
    "The solution was spin-coated onto the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "The solution was spin-coated onto the perovskite films at a speed of {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "The surface treatment was finished by depositing passivation solution onto the perovskite film surface at a spin rate of {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "Then the passivation solution was spin-coated on the inorganic perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "Afterwards, the passivation solution was deposited on the perovskite film by spin-coating at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "The passivation solution was deposited on the perovskite layer by spin coating at {spin_speed_passivator} rpm for {spin_time_passivator} s without further annealing.",  
    "For the surface treatment of perovskite films, the passivation solution was spin-coated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "Then the passivation solution was spin-coated onto the as-prepared perovskite films at a speed of {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "And then it was spin-coated on the cooled perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "The passivation solution was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "For surface treatment, the passivation solution was spin-coated onto perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "Afterward, the obtained saturated solution, used as the passivating layer, was spin-coated on the film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "Next, the passivation solution was dynamically spin-coated onto the as-formed perovskite at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "The passivation solution was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s on top of the perovskite film to form a passivation layer.",  
    "For the surface passivation, the passivation solution was spin-coated on perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "For the passivation treatment, the passivation solution was spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "The passivation solution was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s onto the perovskite film.",  
    "Then, the surface treatment solution was spin-coated on the film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
    "The passivation layers were sequentially spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.",  
]

passivation_drop_segments = [
    "Subsequently, {passivator_volume} µL of passivator was dropped at {passivator_timing} s during spin-coating.",
    "During spin-coating, {passivator_volume} µL of passivator was introduced at {passivator_timing} s.",
    "At {passivator_timing} s, {passivator_volume} µL of passivator was added to the spinning passivation layer.",
    "The passivator volume of {passivator_volume} µL was dropped at {passivator_timing} s during spin-coating.",
    "{passivator_volume} µL of passivator was introduced at {passivator_timing} s in the spin-coating process.",
    "During the spin-coating of the passivation layer, {passivator_volume} µL of passivator was added at {passivator_timing} s.",
    "At a timing of {passivator_timing} s, {passivator_volume} µL of passivator was introduced into the spinning passivation layer.",
    "The addition of {passivator_volume} µL of passivator occurred at {passivator_timing} s during spin-coating.",
    "To enhance the passivation layer, {passivator_volume} µL of passivator was dropped at {passivator_timing} s during spin-coating.",
    "{passivator_volume} µL of passivator was gently dispensed at {passivator_timing} s during the spin-coating of the passivation layer.",
    "Passivator {passivator_volume} µL was added at {passivator_timing} s during the spin-coating process.",
    "At {passivator_timing} s, a drop of {passivator_volume} µL of passivator was introduced during spin-coating.",
    "The spin-coating process included the addition of {passivator_volume} µL of passivator at {passivator_timing} s.",
    "To improve passivation, {passivator_volume} µL of passivator was dropped at {passivator_timing} s during spin-coating.",
    "During spin-coating, {passivator_volume} µL of passivator was drop-casted onto the sample at {passivator_timing} s.", 

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
    "Thermal treatment involved annealing at {anneal_temp_passivator} °C for {anneal_time_passivator} min to facilitate crystallization.", 
    "The film was then annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "The films were subsequently dried at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "And followed by annealing at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "Then annealing at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "And then annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "And then transferred to the hotplate and annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "And heated at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "Subsequently, the sample was annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "Followed by annealing at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "Then, it was annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "Subsequently, the film was annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.", 
    "It was then annealed on a hotplate at {anneal_temp_passivator} °C for {anneal_time_passivator} min to form the perovskite film.",  
    "Passivator solution was spin-coated and annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",  
    "Then, it was annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min.",  
    "It was then annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min to remove the solvent residual.",  
    "Thermal treatment involved annealing at {anneal_temp_passivator} °C for {anneal_time_passivator} min to facilitate crystallization.",  
    "It was then annealed at {anneal_temp_passivator} °C for {anneal_time_passivator} min as a post-treatment for PSCs.",  

]

# Image analysis
image_analysis_segments = [
    "Image analysis shows that the spin-coating coverage reaches {area_px2}%, and the average grayscale value of the film is {gray_mean}."
]

# PL analysis 
pl_analysis_segments = [
    "Spectral analysis indicates that, upon the onset of annealing, the film reaches the explosive nucleation point at {peak_time} seconds, at which the photoluminescence (PL) intensity attains its maximum. Following this peak, the PL intensity decreases to 30% of its maximum value, with an average decay slope of {decay_slope}."
]

# XRD
xrd_analysis_segments_12 = [
    "XRD analysis showed a diffraction peak was identified at around 12.65°, with an intensity of {xrd_intensity_12} cts and a full width at half maximum (FWHM) of {xrd_fhwm_12}, which corresponds to the characteristic peak of PbI₂. The relatively low intensity of this peak suggests a limited presence of residual PbI₂."
]

xrd_analysis_segments_stress = [
    "XRD analysis showed a diffraction peak was identified at 4.00°, with an intensity of {xrd_intensity_4} cts，which corresponds to the formation of a 2D structure within the perovskite lattice. The high intensity implies efficient surface passivation, contributing positively to device performance. GIXRD analysis further revealed a residual tensile stress of {xrd_Stress} MPa in the perovskite film via measurement conducted at an incident angle of 1°."
]


Conclusion_SAM_templates_base = {
    "PCE": "a power conversion efficiency (PCE) of {PCE}%",
    "Voc": "an open-circuit voltage (VOC) of {Voc} V",
    "Jsc": "a short-circuit current density (JSC) of {Jsc} mA/cm²",
    "FF": "a fill factor (FF) of {FF}%"
}


def build_conclusion(metrics: list, values: dict):
    segments = [
        Conclusion_SAM_templates_base[m].format(**values)
        for m in metrics
    ]

    if len(segments) == 1:
        options = [
            f" The device exhibits {segments[0]}.",
            f" A {segments[0]} was achieved.",
            f" The resulting solar cell delivers {segments[0]}.",
            f" An optimized configuration yields {segments[0]}.",
            f" Experimental results confirm {segments[0]}.",
            f" Measurements demonstrate {segments[0]} in the final device."
        ]
    elif len(segments) == 2:
        options = [
            f" The device exhibits {segments[0]} and {segments[1]}.",
            f" Measurements reveal {segments[0]} as well as {segments[1]}.",
            f" Performance includes {segments[0]} and {segments[1]}.",
            f" The cell demonstrates both {segments[0]} and {segments[1]}.",
            f" The optimized sample delivers {segments[0]} with concurrent {segments[1]}.",
            f" Achievements include {segments[0]} and simultaneous {segments[1]}."
        ]
    elif len(segments) == 3:
        joined = ", ".join(segments[:-1]) + f", and {segments[-1]}"
        options = [
            f" The device exhibits {joined}.",
            f" A combination of {joined} was achieved.",
            f" Measurements indicate {joined} in the optimized device.",
            f" The optimized performance includes {joined}.",
            f" The solar cell achieved {joined} as a result of SAM treatment.",
            f" Experimental evaluation reveals {joined} in the final configuration."
        ]
    else:  
        joined = ", ".join(segments[:-1]) + f", and {segments[-1]}"
        options = [
            f" The device exhibits {joined}.",
            f" A combination of {joined} was achieved.",
            f" Measurements indicate {joined} in the optimized device.",
            f" The optimized performance includes {joined}.",
            f" The solar cell achieved {joined} as a result of SAM treatment.",
            f" Experimental evaluation reveals {joined} in the final configuration."
        ]

    return random.choice(options)
