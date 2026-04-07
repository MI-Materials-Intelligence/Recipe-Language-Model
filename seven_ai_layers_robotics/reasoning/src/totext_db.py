"""Database text conversion utilities for perovskite solar cell data.

This module provides functions to convert database records into
descriptive text using template-based generation.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
import random
import json
from pathlib import Path

# ---------------------------
# Template List Definitions
# ---------------------------
# Synonym and Phrase Library Definitions
# --------------------------------------

# Preparation-related phrases (15 items)
PREPARED_PHRASES = [
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

# Introductory Phrases
INTRO_SEGMENTS = [
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
    "The control device displays a JSC of {jsc} mA/cm², a VOC of {voc} V and an FF of {ff}%, turning out a moderate PCE of {pce}%." ,
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

# Perovskite Formula Segments
PEROVSKITE_FORMULA_SEGMENTS = [
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
    "The composition of the {concentration_pvk} mol/L perovskite film with band gap is {formula_pvk}.",
    "The {concentration_pvk} mol/L perovskite precursor solution with a chemical formula of {formula_pvk}.",
    "The perovskite precursor solutions were prepared by dissolving {concentration_pvk} mol/L {formula_pvk}.",
    "{concentration_pvk} mol/L {formula_pvk} perovskite precursors were prepared.",
    "For the perovskite composition {formula_pvk}, {concentration_pvk} mol/L perovskite precursor solution was prepared.",
    "The {concentration_pvk} mol/L perovskite solution ({formula_pvk}) was prepared, shaken overnight to fully dissolve, and then used to prepare perovskite films.",
    "The perovskite precursor solution ({formula_pvk}) was prepared with a concentration of {concentration_pvk} mol/L in a mixed anhydrous solvent of DMF/DMSO (4/1, v/v).",
    "The perovskite ({formula_pvk}) solution was prepared with a concentration of {concentration_pvk} mol/L in mixed solvent of DMF and DMSO.",
    "Then, perovskite precursor solution ({concentration_pvk} mol/L) was prepared at the stoichiometric ratio of {formula_pvk}.",
    "A {concentration_pvk} mol/L perovskite precursor solution was constructed by mixing FAI, PbI2, methylammonium iodide and caesium iodide in DMF: DMSO mixed solvent with the chemical formula of {formula_pvk}.",
    "For the inorganic perovskite layers, {concentration_pvk} mol/L {formula_pvk} inorganic perovskite precursor solution was prepared in DMSO solvent.",
    "The perovskite precursor solution was prepared with a concentration of {concentration_pvk} mol/L using PbI2 and MAI dissolved in a mixed DMF/DMSO solvent.",
    "The perovskite ({formula_pvk}) precursor solution was prepared with a concentration of {concentration_pvk} mol/L in a mixed solvent of DMF and DMSO.",
    "The mixed perovskite ({formula_pvk}) precursor solution was prepared with a total concentration of {concentration_pvk} mol/L in DMF/DMSO co-solvent.",
    "The perovskite precursor solution was prepared based on the perovskite composition of {formula_pvk} in anhydrous DMF solvent (total concentration of {concentration_pvk} mol/L).",
    "The perovskite precursor solution ({concentration_pvk} mol/L) was prepared in a solvent mixture of DMF and DMSO according to the formula of {formula_pvk}.",
    "The perovskite solution ({concentration_pvk} mol/L) was made according to the composition of {formula_pvk} in a mixed solvent of DMF/DMSO.",
    "The perovskite precursor solution ({formula_pvk}) was prepared with a concentration of {concentration_pvk} mol/L in a mixed anhydrous solvent of DMF/DMSO (4/1, v/v).",
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

# SAM Formula Segments - Single
SAM_FORMULA_SEGMENTS_SINGLE = [
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
    "The sample of {formula_sam1} was fabricated by spin coating the {formula_sam1} solution with a concentration of {concentration_sam1} mg/mL.",
    "For the SAM solution, {formula_sam1} ({concentration_sam1} mg/mL) was added to the previous solution.",
    "The hole transport layer (HTL) was fabricated using the SAM solution of {formula_sam1}. The {formula_sam1} concentration is {concentration_sam1} mg/mL.",
    "The {formula_sam1} solution was prepared with a concentration of {concentration_sam1} mg/mL.",
    "A SAM solution ({concentration_sam1} mg/mL {formula_sam1}) was applied to the FTO glass substrates by spin-coating.",
    "{concentration_sam1} mg/mL of {formula_sam1} was added.",
    "A SAM solution consisting of {formula_sam1} ({concentration_sam1} mg/mL) in ethanol was prepared.",
    "The optimal SAM was prepared by using {formula_sam1} ({concentration_sam1} mg/mL)."
    "The sample of {formula_sam1} was fabricated with a concentration of {concentration_sam1} mg/mL.",
    "Different concentrations of {formula_sam1} were added into the perovskite precursor solution for modification.",
    "The {formula_sam1} solution was prepared with a concentration of {concentration_sam1} mg/mL.",
]

# SAM Formula Segments - Dual
SAM_FORMULA_SEGMENTS_DUAL = [
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
    "While the sample of {formula_sam1} and {formula_sam2} were fabricated by spin coating {formula_sam1} and {formula_sam2} solution with concentration of {concentration_sam1} mg/mL and {concentration_sam2} mg/mL.",
    "For the SAM solution, {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) were added to the previous solution."
    "The hole transport layer (HTL) was fabricated by using the mixed SAM solution of {formula_sam1} and {formula_sam2}. The {formula_sam1} concentration is {concentration_sam1} mg/mL and {formula_sam2} concentration is {concentration_sam2} mg/mL.",
    "The {formula_sam1} and {formula_sam2} solution were prepared with a concentration of {concentration_sam1} mg/mL and {concentration_sam2} mg/mL.",
    "A mixed SAMs solution ({concentration_sam1} mg/mL {formula_sam2} and {concentration_sam2} mg/mL) were applied to the FTO glass substrates by spin-coating.",
    "{concentration_sam1} mg/mL of {formula_sam1} and {concentration_sam2} mg/mL of {formula_sam2} were added.",
    "Mixed SAMs solution, consisting of {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL) in ethanol were prepared.",
    "The optimal hybrid SAMs were prepared by mixing {formula_sam1} ({concentration_sam1} mg/mL) and {formula_sam2} ({concentration_sam2} mg/mL).",
    "The {formula_sam1} concentration is {concentration_sam1} mg/mL and {formula_sam2} concentration is {concentration_sam2} mg/mL.",
    "The {formula_sam1} concentration is {concentration_sam1} mg/mL and {formula_sam2} concentration is {concentration_sam2} mg/mL.",
    ]

# SAM Formula Segments - Triple
SAM_FORMULA_SEGMENTS_TRIPLE = [
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

# Additive Formula Segments - Single
ADDITIVE_FORMULA_SEGMENTS_SINGLE = [
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
    "An equal amount of {formula_add1} ({concentration_add1} mg/mL) was dissolved in DMF and DMSO with an 4:1 volume ratio.",
    "For the modified solution, {formula_add1} ({concentration_add1} mg/mL) was added to the previous solution.",
    "To prepare the precursor solution with {formula_add1} ({concentration_add1} mg/mL), the additive was added to the precursor solution.",
    "And chlorinated {formula_add1} under {concentration_add1} mg/mL concentration in the perovskite precursor solution.",
    "To prepare the precursor solution with {formula_add1} ({concentration_add1} mg/mL), the additive was added to the precursor solution.",
    "For the additive-treated cells, {formula_add1} ({concentration_add1} mg/mL) was added into the perovskite precursor solution."
    "{concentration_add1} mg/mL {formula_add1} was then added as additive into the precursor solution.",
    "{formula_add1} additive was added into the precursor solution at a concentration of {concentration_add1} mg/mL.",
    "{formula_add1} was added into the perovskite solution as additive with a concentration of {concentration_add1} mg/mL.",
    "The optimum amount of {formula_add1} added into the precursor solution was {concentration_add1} mg/mL.",
    "{formula_add1} with concentration {concentration_add1} mg/mL were added into the perovskite solution.",
    "For the {formula_add1} additive system, the molar ratios of perovskite to {formula_add1} were 15%, 30%, 60%, and 100%.",
    "Then {concentration_add1} mg/mL {formula_add1} was added to the perovskite precursor solution and stirred for 2 h.",
    "For the target perovskite, {concentration_add1} mg/mL {formula_add1} was added to the precursor solution, and it was ensured that it is well mixed with the precursor.",
    "{concentration_add1} mg/mL {formula_add1} was added in the solution to improve the film morphology.",
    "The piperidinium salt {formula_add1} was dissolved in the perovskite solution obtained with the molar ratio {concentration_add1} mg/mL.",
    "{concentration_add1} mg/mL {formula_add1} was added to the perovskite precursor solution and stirred for 2 h.",
    "{concentration_add1} mg/mL {formula_add1} was added into the mixed perovskite solution.",
    "For the modified solution, {concentration_add1} mg/mL {formula_add1} was added to the precursor solution.",
    "The target precursor solution was prepared with {formula_add1} ({concentration_add1} mg/mL).",
    "{concentration_add1} mg/mL of {formula_add1} was added.",
    "{formula_add1} ({concentration_add1} mg/mL) was added into the perovskite precursor solution.",
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL), the additive was added to the precursor solution." ,

    ]

# Additive Formula Segments - Dual
ADDITIVE_FORMULA_SEGMENTS_DUAL = [
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
    "Equal amounts of {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were dissolved in DMF and DMSO with an 4:1 volume ratio.",
    "For the modified solution, {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added to the previous solution.",
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL), the additive were added to the precursor solution.",
    "And chlorinated {formula_add1} and {formula_add2} under {concentration_add1} mg/mL and {concentration_add2} mg/mL concentrations in perovskite precursor solution.",
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL), the additives were added to the precursor solution.",
    "For the additives treated cells, the {formula_add1} ({concentration_add1} mg/mL) and {formula_add2} ({concentration_add2} mg/mL) were added into the perovskite precursor solution.",
    "In addition, {formula_add1} ({concentration_add1} mg/mL), and {formula_add2} ({concentration_add2} mg/mL, 520 mg mL-1 in acetonitrile) were incorporated to improve its conductivity.",
    "Then, around {concentration_add1} mg/mL of {formula_add1} and {concentration_add2} mg/mL of {formula_add2} were also added into the mixed perovskite solution.",
    "For the additives treated cells, the {formula_add1} ({concentration_add1} mg/mL) or {formula_add2} ({concentration_add2} mg/mL) were added into the perovskite precursor solution.",

    ]

# Additive Formula Segments - Triple
ADDITIVE_FORMULA_SEGMENTS_TRIPLE = [
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
    "Equal amounts of {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were dissolved in DMF and DMSO with an 4:1 volume ratio.",
    "For the modified solution, {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL) were added to the previous solution.",
    "To prepare the precursor solutions with {formula_add1} ({concentration_add1} mg/mL), {formula_add2} ({concentration_add2} mg/mL) and {formula_add3} ({concentration_add3} mg/mL), the additive were added to the precursor solution.",
    "And chlorinated {formula_add1}, {formula_add2} and {formula_add3} under {concentration_add1} mg/mL, {concentration_add2} mg/mL and {concentration_add3} mg/mL concentrations in perovskite precursor solution." ,

    ]

# Process Segments
PROCESS_SEGMENTS = [
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
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The perovskite precursor was spin-coated onto substrates with two stages program at {spin1_speed} rpm for {spin1_time} s, and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "Specifically, the perovskite precursor solution was first spinning at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite precursor was spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "For perovskite films fabrication, the perovskite precursor was spin-coated on the as prepared substrates at {spin1_speed} rpm for {spin1_time} s, subsequently at {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite precursor solutions were spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "Then the filtered perovskite precursor was spin-coated on substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite film is deposited by spin-coating with {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "Spread perovskite solution spin-coated in two steps, namely, {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite precursor solution was deposited on the substrate via a two-step spin coating process; first, the solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",
    "The precursor solution was spin-coated onto the substrate surface at {spin1_speed} rpm for {spin1_time} s, then accelerated to {spin2_speed} rpm and maintained at this speed for {spin2_time} s.",
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "For the perovskite deposition process, the perovskite films were deposited using a two-step spin-coating process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s  and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The perovskite solution was spin coated on the substrates at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",
    "The precursor solution was spin-coated in a two-step process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The perovskite precursor solutions were spin-coated on substrate at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and then, {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite precursor solution was then spin-coated at {spin1_speed} rpm for {spin1_time} s followed by an additional spin at {spin2_speed} rpm for {spin2_time} s.",
    "The prepared precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s onto the substrate.",
    "The precursor solution was spin-coated on the substrate at {spin1_speed} rpm for {spin1_time} s and then, {spin2_speed} rpm for {spin2_time} s.",
    "The precursor solution was deposited on the substrate and spin-coated with a two-step spin-coating procedure: {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite layer was deposited via a two-step spin-coating procedure with {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite solution was spin coated on the substrate at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",
    "For the perovskite films, the spin-coated process was divided by a consecutive two-step process, the spin rate of the first step is {spin1_speed} rpm for {spin1_time} s, and the spin rate of the second step is {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite layer was spin-coated with a two-step recipe, first at {spin1_speed} rpm for {spin1_time} s followed by {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite solution was deposited on substrate by two consecutive spin-coating steps of {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The perovskite solutions were spin-coated onto substrate at {spin1_speed} rpm for {spin1_time} s, subsequently at {spin2_speed} rpm for {spin2_time} s.",
    "The spin coating procedure was done in ambient air by a consecutive two-step spin-coating process at first {spin1_speed} rpm for {spin1_time} s and second {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite solution was deposited on the substrate and spun cast at {spin1_speed} rpm for {spin1_time} s followed by {spin2_speed} rpm for {spin2_time} s.",
    "For the perovskite film fabrication, the substrate was spun at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",
    "Then, the prepared precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s onto the ITO substrate.",
    "The perovskite film was deposited by spin-coating onto the substrate using two-step spin-coating process, first at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",
    "The precursor solution was deposited on the substrate and spun cast at {spin1_speed} rpm for {spin1_time} s, followed by {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite was deposited via a two-step spin-coating procedure with {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite precursor solution was then spin-coated onto a substrate at {spin1_speed} rpm for {spin1_time} s followed by an additional spin at {spin2_speed} rpm for {spin2_time} s.",
    "Afterwards, the perovskite precursor solution was deposited on the substrate via a two-step spin coating process; first, the solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",
    "The precursor solution was spin-coated onto the substrate surface at {spin1_speed} rpm for {spin1_time} s, then accelerated to {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite solutions were spin-coated onto the substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "For the perovskite deposition process, the perovskite solutions were deposited using a two-step spin-coating process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s (acceleration rate 500 rpm/s) and {spin2_speed} rpm for {spin2_time} s (acceleration rate 1000 rpm/s), respectively.",
    "The as prepared perovskite precursor was spin-coated onto the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The precursor solution was spin-coated in a two-step process at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The perovskite precursor solutions were spin-coated on substrate at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",
    "Specifically, the perovskite precursor solution was first deposited at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The perovskite precursor solution was dripped onto substrate, and a two-step spin-coating procedure was applied. The first step was carried out at {spin1_speed} rpm, followed by {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite is deposited via a two-step spin-coating procedure, first at {spin1_speed} rpm for {spin1_time} s and finally at {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite precursor was spin-coated onto the substrates with two stages program at {spin1_speed} rpm for {spin1_time} s, and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "The precursor solution was spin-coated on substrate at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The prepared precursor solution was spin coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s onto the substrate.",
    "The perovskite solutions were spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s, respectively.",
    "For perovskite films fabrication, the perovskite precursor was spin-coated on the as prepared substrates at {spin1_speed} rpm for {spin1_time} s and at {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite precursor solutions were spin-coated on the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite film was deposited by spin-coating at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "Perovskite solution was deposited in two steps, first at {spin1_speed} rpm for {spin1_time} s and then at {spin2_speed} rpm for {spin2_time} s.",
    "For the perovskite layer, the prepared perovskite solution was spin-coated at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "The perovskite film was deposited by spin-coating at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",
    "Then, the perovskite precursor solution was spin-coated at {spin1_speed} rpm for {spin1_time} s, and then at {spin2_speed} rpm for {spin2_time} s.",
    "For the fabrication of perovskite films, the perovskite solutions were spin-coated onto the substrates at {spin1_speed} rpm for {spin1_time} s and {spin2_speed} rpm for {spin2_time} s.",

    ]

# Antisolvent Segments
ANTISOLVENT_SEGMENTS = [
    "During the second spin-coating step, {antisolvent_volume} µL of antisolvent was introduced at last {antisolvent_timing} s.",
    "At a carefully chosen interval ({antisolvent_timing} s) during the second stage, {antisolvent_volume} µL of antisolvent was gently dispensed to improve crystallization.",
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
    "At the {antisolvent_timing} s of the second step, {antisolvent_volume} µL antisolvent was dropped.",
    "During the second step, antisolvent CB ({antisolvent_volume} µL) was dropped at the middle of the spinning substrate {antisolvent_timing} s prior to the end of the spinning.",
    "At the {antisolvent_timing} s of spinning, {antisolvent_volume} µL of CB was dripped onto the substrate centre.",
    "After {antisolvent_timing} s into the second stage, {antisolvent_volume} µL chlorobenzene antisolvent was dropped on top of the spinning substrates.",
    "During spin-coating process, {antisolvent_volume} µL of CB was dropped on the perovskite at {antisolvent_timing} s, prior to the end of the second procedure.",
    "During which CB ({antisolvent_volume} µL) was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",
    "{antisolvent_volume} µL CB was dropped on the perovskite film at {antisolvent_timing} s before the end of the program.",
    "{antisolvent_volume} µL of CB as antisolvent was dripped onto the substrate quickly at {antisolvent_timing} s during the second spinning step.",
    "At the last {antisolvent_timing} s, {antisolvent_volume} µL of chlorobenzene solution was dropped on the perovskite.",
    "Then, with {antisolvent_timing} s of spin time remaining, chlorobenzene ({antisolvent_volume} µL) was dispensed onto the middle of the substrate.",
    "{antisolvent_volume} µL of CB was dripped onto the substrate during spinning.",
    "At {antisolvent_timing} s before the end of the spin-coating procedure, {antisolvent_volume} µL CB was dropped onto the substrates.",
    "At the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL anisole was dropped as antisolvent.",
    "CB ({antisolvent_volume} µL) was dropped on the film at {antisolvent_timing} s before the end of the spinning.",
    "A total of {antisolvent_volume} µL of CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",
    "{antisolvent_volume} µL chlorobenzene as antisolvent was dropped {antisolvent_timing} s before the end of the spin-coating procedure.",
    "In the last {antisolvent_timing} s of the second step, the anti-solvent ({antisolvent_volume} µL of chlorobenzene) was dropped in the center at a constant rate",
    "During the second step, {antisolvent_volume} µL of chlorobenzene was dropped on the spinning substrate {antisolvent_timing} s before the end of the process.",
    "{antisolvent_volume} µL of chlorobenzene was quickly poured to extract the mixed solvents at the last of {antisolvent_timing} s.",
    "During the second spin coating step, {antisolvent_volume} µL CB was dripped onto the perovskite film at {antisolvent_timing} s before ending the program.",
    "In the last {antisolvent_timing} s of the second step, the anti-solvent ({antisolvent_volume} µL of CB) was dropped in the center of the substrate at a constant rate within 1 s.",
    "{antisolvent_volume} µL CB was dripped onto the center of film at {antisolvent_timing} s before the end of the spin-coating procedure.",
    "During the second spin coating step, {antisolvent_volume} µL of CB was deposited onto the perovskite film {antisolvent_timing} seconds before the program ended.",
    "{antisolvent_volume} µL CB as the antisolvent was dripped on the film at {antisolvent_timing} s before the end of the last procedure.",
    "A {antisolvent_volume} µL CB was dropped onto the substrate at the last {antisolvent_timing} s of the spin-coating, resulting in the formation of dark brown films.",
    "Then, {antisolvent_volume} µL CB was dropped onto the substrate during the second spin-coating step at the last {antisolvent_timing} s of the spin-coating.",
    "After {antisolvent_timing} s, {antisolvent_volume} µL chlorobenzene as antisolvent was casted vertically.",
    "At the {antisolvent_timing} s of the spin-coating process, {antisolvent_volume} µL anti-solvent was rapidly poured onto the perovskite film.",
    "After {antisolvent_timing} s of the second spin-coating step, {antisolvent_volume} µL of chlorobenzene was dripped onto the center of the substrate to induce fast crystallization of the perovskite film.",
    "During the spin-coating process, {antisolvent_volume} µL of CB as anti-solvent was quickly dropped onto the samples at a delay time of {antisolvent_timing} s.",
    "{antisolvent_volume} µL of antisolvents was dripped on the spinning substrate during the {antisolvent_timing} s of the second spin-coating step.",
    "{antisolvent_volume} µL chlorobenzene as antisolvent was dropped {antisolvent_timing} s before the end of the spin-coating procedure.",
    "In the last {antisolvent_timing} s of the second step, the anti-solvent ({antisolvent_volume} µL of chlorobenzene) was dropped in the center at a constant rate within 1 s.",
    "Anti-solvent ({antisolvent_volume} µL) was dropped on the film at {antisolvent_timing} s before the end of the spinning.",
    "During the second step end of {antisolvent_timing} s, {antisolvent_volume} µL of ethyl acetate was drop-coated to treat the perovskite films.",
    "After {antisolvent_timing} s, {antisolvent_volume} µL of anti-solvent was rapidly dropped on top of the spinning substrate.",
    "During the second spin-coating step, {antisolvent_volume} µL of EA was quickly poured onto the substrate after {antisolvent_timing}.",
    "{antisolvent_volume} µL CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",
    "Immediately before the end spin-coating process, {antisolvent_volume} µL of anisole was dropped onto the films.",
    "During this stage, {antisolvent_volume} µL CB antisolvent was quickly dripped onto the centre of the substrate at {antisolvent_timing} s before the end of the spin-coating process.",
    "The film was quickly washed with {antisolvent_volume} µL toluene at {antisolvent_timing} s during spin-coating.",
    "At the {antisolvent_timing} s of spinning, {antisolvent_volume} µL of anti-solvent chlorobenzene was dripped at the center.",
    "After {antisolvent_timing} s into spin-coating procedure, {antisolvent_volume} µL diethyl ether was dripped onto the spinning substrate.",
    "During the last step, {antisolvent_volume} µL of chlorobenzene was dropped on the film at {antisolvent_timing} s.",
    "In the second step, {antisolvent_volume} µL anisole was dropped onto the substrate during the last {antisolvent_timing} s of the spinning.",
    "{antisolvent_volume} µL CB as the antisolvent was dripped on the film at {antisolvent_timing} s before the end of the last procedure.",
    "After {antisolvent_timing} s, {antisolvent_volume} µL CB was dropped on the film.",
    "{antisolvent_volume} µL anisole was dropped onto the substrate during the last {antisolvent_timing} s of the spinning, resulting in the formation of dark brown films.",
    "{antisolvent_volume} µL CB was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",
    "During the second spin coating step, {antisolvent_volume} µL of CB was deposited onto the perovskite film {antisolvent_timing} s before the program ended.",
    "A total of {antisolvent_volume} µL of CB was slowly dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",
    "{antisolvent_volume} µL of antisolvent was dripped onto the substrate during spinning.",
    "At {antisolvent_timing} s before the end of the spin-coating procedure, {antisolvent_volume} µL CB was dropped onto the substrates.",
    "At the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL anisole was dropped as antisolvent.",
    "At the {antisolvent_timing} s of the second step, {antisolvent_volume} µL antisolvent was slowly dripped onto the center of the film at {antisolvent_timing} s before the end of the spinning program.",
    "During the second step, {antisolvent_volume} µL of chlorobenzene was dropped on the spinning substrate {antisolvent_timing} s before the end of the process.",
    "{antisolvent_volume} µL of chlorobenzene was quickly poured to extract the mixed solvents at the last of {antisolvent_timing} s.",
    "During the second spin coating step, {antisolvent_volume} µL CB was dripped onto the perovskite film at {antisolvent_timing} s before ending the program.",
    "{antisolvent_volume} µL of antisolvent was drop-coated onto the substrate while spinning.",
    "{antisolvent_volume} µL of CB was dropped on the perovskite film within {antisolvent_timing} s into the spin coating process.",
    "During the second step, antisolvent CB ({antisolvent_volume} µL) was dropped at the middle of the spinning substrate {antisolvent_timing} s prior to the end of the spinning.",
    "At the {antisolvent_timing} s of spinning, {antisolvent_volume} µL of antisolvent was dripped onto the substrate centre.",
    "After {antisolvent_timing} s into the second stage, {antisolvent_volume} µL chlorobenzene antisolvent was dropped on top of the spinning substrates (about 1 cm distance).",
    "During spin-coating process, {antisolvent_volume} µL of CB was dropped on the perovskite at {antisolvent_timing} s prior to the end of the second procedure.",
    "At the {antisolvent_timing} s of the second step, {antisolvent_volume} µL anisole was dropped as antisolvent.",
    "{antisolvent_volume} µL anti-solvent was quickly dripped at the {antisolvent_timing} s before the end of spin coating step.",
    "During the second spin coating step, {antisolvent_volume} µL of CB was deposited onto the perovskite film {antisolvent_timing} s before the program ended.",
    "During the second step, CB as antisolvent ({antisolvent_volume} µL) was dropped at the middle of the spinning substrate {antisolvent_timing} s prior to the end of the spinning.",
    "{antisolvent_volume} µL CB as the antisolvent was dripped on the film at {antisolvent_timing} s before the end of the last procedure.",
    "At the last {antisolvent_timing} s of the second step, {antisolvent_volume} µL CB was dropped as antisolvent.",
    "Antisolvent ({antisolvent_volume} µL) was dripped onto the center of film at {antisolvent_timing} s before the end of spin-coating.",
    "{antisolvent_volume} µL CB was dropped on the perovskite film at {antisolvent_timing} s before the end of the program.",
    "{antisolvent_volume} µL of CB as antisolvent was dripped onto the substrate quickly at {antisolvent_timing} s during the second spinning step.",
    "At the last {antisolvent_timing} s, {antisolvent_volume} µL of CB solution was dropped on the perovskite.",
    "With {antisolvent_timing} s of spin time remaining, CB ({antisolvent_volume} µL) was slowly dispensed onto the middle of the substrate.",
    "When the countdown was {antisolvent_timing} s, {antisolvent_volume} µL CB serving as antisolvent was dropped onto the substrates.",
    "{antisolvent_volume} µL CB was dropped {antisolvent_timing} s before the end of the procedure.",
    "According to the antisolvent method, {antisolvent_volume} µL of antisolvent was dropped on the film {antisolvent_timing} s before the end of the program.",
    "{antisolvent_volume} µL of CB as antisolvent was dripped onto the substrate quickly at {antisolvent_timing} s during the second spinning step.",
    "Then, with {antisolvent_timing} s of spin time remaining, CB ({antisolvent_volume} µL) was slowly dispensed onto the middle of the substrate.",
    "At the last {antisolvent_timing} s, {antisolvent_volume} µL of CB solution was dropped on the perovskite.",
    "At the {antisolvent_timing} s before the end of the progress, {antisolvent_volume} µL CB was evenly dripped onto the substrate.",
    "During the spin-coating, {antisolvent_volume} µL CB solution was dripped at {antisolvent_timing} s before ending.",
    "{antisolvent_volume} µL of antisolvent was dropped on the film {antisolvent_timing} s before the end of the program.",
    "CB ({antisolvent_volume} µL) was dropped at the center of the spinning substrate approximately {antisolvent_timing} s before the end of the spin coating procedure.",
    "During the spin-coating process, {antisolvent_volume} µL of CB antisolvent was quickly dripped onto the centre of the perovskite film {antisolvent_timing} s before the end of the process.",
    "During the second step, {antisolvent_volume} µL of CB as anti-solvent was quickly dripped onto the centre of the perovskite film {antisolvent_timing} s before the end of the spin-coating process.",

    ]

# Anneal Segments
ANNEAL_SEGMENTS = [
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
    "The perovskite sample was subsequently annealed at {anneal_temp} °C for {anneal_time} min.",
    "The sample was then annealed at {anneal_temp} °C for {anneal_time} min.",
    "The substrates were immediately transferred to the hotplate and annealed at {anneal_temp} °C for {anneal_time} min.",
    "Afterwards, the perovskite film was annealed at {anneal_temp} °C for {anneal_time} min.",
    "Then the film is annealed at {anneal_temp} °C for {anneal_time} min.",
    "Heat-treatment was implemented with the substrates for {anneal_time} min at {anneal_temp} °C.",
    "And then annealed at {anneal_temp} °C for {anneal_time} min.",
    "The as-coated film was then annealed at {anneal_temp} °C for {anneal_time} min.",
    "The films were then annealed at {anneal_temp} °C for {anneal_time} min.",
    "The film was immediately annealed at {anneal_temp} °C for {anneal_time} min.",
    "The subsequent film was then heated at {anneal_temp} °C for {anneal_time} min to obtain the bright perovskite film.",
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
    "The perovskite annealed at {anneal_temp} °C for {anneal_time} min.",
    "The subsequent film was then heated at {anneal_temp} °C for {anneal_time} min to obtain the bright perovskite film.",
    "Then, it was annealed at {anneal_temp} °C for {anneal_time} min.",
    "After the spin coating was completed, it was annealed on a hot stage at {anneal_temp} °C for {anneal_time} min.",
    "The film was immediately annealed at {anneal_temp} °C for {anneal_time} min.",
    "The deposited perovskite films were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",
    "Then the films were annealed at {anneal_temp} °C for {anneal_time} min to form the perovskite layer.",
    "Then, the as-prepared perovskite films were transferred onto a hotplate and annealed at {anneal_temp} °C for {anneal_time} min.",
    "The films were dried inside a N2 environment on a hot plate at a temperature of {anneal_temp} for {anneal_time} min.",
    "Subsequently the substrate was covered under a petri dish on a hotplate and annealed at {anneal_temp} for {anneal_time} in ambient air at 20 % relative humidity.",
    "Subsequently, the as-deposited films were annealed at {anneal_temp} for {anneal_time}.",
    "The films were then dried on a hot plate at {anneal_temp} °C for {anneal_time} min.",
    "Next, the substrates were quickly transferred for annealing at {anneal_temp} ℃ for {anneal_time} min.",
    "The substrate was immediately placed on a hotplate and annealed at {anneal_temp} °C for {anneal_time} min.",
    "The wet perovskite films were then transferred onto hot plate and annealed at {anneal_temp} °C for {anneal_time} min.",
    "The films were then annealed on a hot plate at {anneal_temp} °C for {anneal_time} min.",
    "The deposited perovskite films were subsequently annealed on a hotplate at {anneal_temp} °C for {anneal_time} min.",
    "The resulting wet perovskite films were annealed at {anneal_temp} °C for {anneal_time} min.",
    "The as-coated film was then annealed at {anneal_temp} °C for {anneal_time} min.",
    "Heat-treatment was implemented with the substrates for {anneal_time} min at {anneal_temp} °C.",
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

# Instruction Templates
INSTRUCTION_TEMPLATES = [
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


# Passivation Material Segments - Single
PASSIVATION_MATERIAL_SEGMENTS_SINGLE = [
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
    "For the surface treatment of perovskite films, chalcogen-concave molecular stock solutions of {formula_passivator1} ({concentration_passivator1} mg/mL) were spincoated on the perovskite film",
    "For the surface passivation layer, the {formula_passivator1} was dissolved in IPA at a concentration of {concentration_passivator1} mg/mL.",
    "{concentration_passivator1} mg/mL {formula_passivator1} was spin-coated onto the perovskite film.",
    "A small amount of {formula_passivator1} at a concentration of {concentration_passivator1} mg/mL was added into the chlorobenzene/IPA antisolvent mixture for interface modification.",
    "{formula_passivator1} as passivation layer was prepared with a concentration of {concentration_passivator1} mg/mL in IPA solution.",
    "{formula_passivator1} ({concentration_passivator1} mg/mL) was introduced as passivation layer, which was prepared in IPA mixed solution.",
    "{concentration_passivator1} mg/mL {formula_passivator1} in isopropyl alcohol was prepared as passivating layer.",
    "For the interfacial passivation layer, {formula_passivator1} with the concentration of {concentration_passivator1} mg/mL in IPA was used.",
    "The post-passivation layer was prepared by dissolving {concentration_passivator1} mg of {formula_passivator1} in 1 mL IPA and stirring for 1 h." ,
    "{concentration_passivator1} {formula_passivator1} was spin-coated onto the perovskite film.",
    "Later, the {concentration_passivator1} mg/mL {formula_passivator1} (in IPA) was evenly spread on the surface of the perovskite film.",
    "For the surface passivation layer, the {formula_passivator1} was dissolved in IPA at a concentration of {concentration_passivator1} mg/mL.",

    ]

# Passivation Material Segments - Dual
PASSIVATION_MATERIAL_SEGMENTS_DUAL = [
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

    "For the surface passivation layer, the {formula_passivator1} and {formula_passivator2} were dissolved in IPA at a concentration of {concentration_passivator1} mg/mL and {concentration_passivator2} mg/mL.",

    "For the interfacial passivation layer, {formula_passivator1} and {formula_passivator2} with the concentration of {concentration_passivator1} mg/mL and {concentration_passivator2} mg/mL were used.",

    "{formula_passivator1} ({concentration_passivator1} mg/mL) and {formula_passivator2} ({concentration_passivator2} mg/mL) were introduced as passivation layer.",

    "For the {formula_passivator1}–{formula_passivator2} modified layer, the treatment solution were prepared by dissolving {concentration_passivator1} mg {formula_passivator1} and {concentration_passivator2} mg {formula_passivator2} into 1 mL IPA.",

    "Subsequently, the mixed passivating agents of {formula_passivator1}+{formula_passivator2} ({concentration_passivator1} mg of {formula_passivator1} and {concentration_passivator2} mg of {formula_passivator2}) were dissolved in 1 mL of IPA.",


]

# Passivation Material Segments - Triple
PASSIVATION_MATERIAL_SEGMENTS_TRIPLE = [
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
    "For the surface treatment of perovskite films, chalcogen-concave molecular stock solutions of {formula_passivator1} ({concentration_passivator1} mg/mL), {formula_passivator2} ({concentration_passivator2} mg/mL) and {formula_passivator3} ({concentration_passivator3} mg/mL) were spin coated on the perovskite film",
    "For the surface passivation layer, the {formula_passivator1}, {formula_passivator2} and {formula_passivator3} were dissolved in IPA at a concentration of {concentration_passivator1} mg/mL, {concentration_passivator2} mg/mL and {concentration_passivator3} mg/mL.",

        ]

# Passivation Spin Segments
PASSIVATION_SPIN_SEGMENTS = [
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
    "For the surface treatment of perovskite films, the passivators were spincoated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Then passivators were spin-coated onto the as-prepared perovskite films at a speed of {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "For passivator treatment, the passivators were spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Then it was spin-coated on the cooled perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "For the surface passivation, passivators were spin-coated on perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Then, passivation solution was spin-coated on top of the as-prepared perovskite at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "After cooled to room temperature, passivators were deposited by spin-coating with {spin_speed_passivator} rpm.",
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
    "It was then spin-coated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "It was deposited on the surface of the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "It was spin-coated on top of perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "The surface treatment was finished by depositing passivation solution onto the perovskite film surface at a spin rate of {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Then the passivation solution was spin-coated on the inorganic perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Afterwards, the passivation solution was deposited on the perovskite film by spin-coating at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Subsequently, the passivation solution was dropped on the annealed perovskite films during a spin-coating procedure at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "The passivation solution was deposited on the perovskite layer by spin coating at {spin_speed_passivator} rpm for {spin_time_passivator} s without further annealing.",
    "For the surface treatment of perovskite films, the passivation solution was spin-coated on the perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Then the passivation solution was spin-coated onto the as-prepared perovskite films at a speed of {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "And then it was spin-coated on the cooled perovskite films at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "The spin coating was performed at {spin_speed_passivator} for {spin_time_passivator}.",
    "The passivation solution was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "For surface treatment, the passivation solution was spin-coated onto perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Afterward, the obtained saturated solution as passivating layer was spin-coated on the film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "Next, the passivation solution was dynamically spin-coated onto the as-formed perovskite at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "The passivation solution was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s on top of the perovskite film to form a passivation layer.",
    "For the surface passivation, the passivation solution was spin-coated on perovskite film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "For the passivation treatment, the passivation solution was spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "The passivation solution was spin-coated at {spin_speed_passivator} rpm for {spin_time_passivator} s onto the perovskite film.",
    "Then, the surface treatment solution was subsequently spin-coated on the film at {spin_speed_passivator} rpm for {spin_time_passivator} s.",
    "The passivation layers were sequentially spin-coated on the perovskite surface at {spin_speed_passivator} rpm for {spin_time_passivator} s.",

    ]

# Passivation Drop Segments
PASSIVATION_DROP_SEGMENTS = [
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
    "During spin-coating, {passivator_volume} µL of passivator was drop-casted onto the sample at {passivator_timing} s.",

    ]

# Passivation Anneal Segments
PASSIVATION_ANNEAL_SEGMENTS = [
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
    "The film was then annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "The films were subsequently dried at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "And followed by annealing at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "Then annealing at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "And then annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "And then transferred to the hotplate and annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "And heated at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "Subsequently, the sample was annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "Followed by annealing at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "Then, it was annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "Subsequently, the film was annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "It was then annealed on a hotplate at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min to form the perovskite film.",
    "Passivator solution was spin-coated and annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "Then, it was annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min.",
    "It was then annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min to remove the solvent residual.",
    "Thermal treatment involved annealing at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min to facilitate crystallization.",
    "It was then annealed at {anneal_temp_passivator} ℃ for {anneal_time_passivator} min as a post-treatment for PSCs.",

    ]

# RGB Image Analysis Templates
IMAGE_ANALYSIS_SEGMENTS = [
    "Image analysis shows that the spin-coating coverage reaches {coverage}%, and the average grayscale value of the film is {grayscale_value}"
]

# PL Analysis Templates
PL_ANALYSIS_SEGMENTS = [
    "Spectral analysis indicates that, upon the onset of annealing, the film reaches the explosive nucleation point at {peak_time} seconds, at which the photoluminescence (PL) intensity attains its maximum. Following this peak, the PL intensity decreases to 30% of its maximum value, with an average decay slope of {decay_slope}."
]

# XRD Analysis Templates - 12.6°
XRD_ANALYSIS_SEGMENTS_12 = [
    "XRD analysis showed a diffraction peak was identified at around 12.65°, with an intensity of {xrd_intensity_12} cts and a full width at half maximum (FWHM) of {xrd_fhwm_12}, which corresponds to the characteristic peak of PbI2. The relatively low intensity of this peak suggests a limited presence of residual PbI2."
]

# XRD Analysis Templates - Stress
XRD_ANALYSIS_SEGMENTS_STRESS = [
    "XRD analysis showed a diffraction peak was identified at 4.00°, with an intensity of {xrd_intensity_4} cts，which corresponds to the formation of a 2D structure within the perovskite lattice. The high intensity implies efficient surface passivation, contributing positively to device performance. GIXRD analysis further revealed a residual tensile stress of {xrd_Stress} MPa in the perovskite film via measurement conducted at an incident angle of 1°."
]


# ===================== Safe value retrieval utilities =====================
def gv(row: pd.Series, col: str, default: str = 'N/A') -> str:
    """Safely retrieve value from pandas Series.

    Args:
        row: Pandas Series containing experimental data.
        col: Column name to retrieve.
        default: Default value if column missing or NaN. Default is 'N/A'.

    Returns:
        String representation of value or default.
    """
    val = row[col] if col in row.index else default
    if pd.isna(val):
        val = default
    return str(val)

def _normalize_material(x) -> Optional[str]:
    """Normalize material name by stripping whitespace and filtering empty values.

    Args:
        x: Raw material value.

    Returns:
        Normalized string or None if invalid.
    """
    if x is None:
        return None
    s = str(x).strip()
    if s.lower() in ("", "n/a", "na", "none", "nan"):
        return None
    return s

def _collect_materials(row: pd.Series, cols: list[str]) -> list[str]:
    """Collect material names from specified columns in a row.

    Args:
        row: Pandas Series containing experimental data.
        cols: List of column names to extract materials from.

    Returns:
        List of unique material names preserving first occurrence order.
    """
    out, seen = [], set()
    for c in cols:
        val = row[c] if c in row.index else None
        name = _normalize_material(val)
        if name and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def generate_output_text(row: pd.Series, templates: dict) -> str:
    """Generate descriptive text from database row using templates.

    Args:
        row: Pandas Series containing experimental parameters.
        templates: Dictionary of template strings for each section.

    Returns:
        Generated descriptive text combining all sections.
    """
    parts = []

    # Introduction section
    parts.append(
        templates['intro'].format(
            prepared_term=templates['prepared_term'],
            pce=gv(row, 'PCE'), ff=gv(row, 'FF'), voc=gv(row, 'Voc'), jsc=gv(row, 'Jsc')
        )
    )

    # Perovskite formula
    parts.append(
        templates['perovskite_formula'].format(
            formula_pvk=gv(row, 'Formula PVK'),
            concentration_pvk=gv(row, 'Concentration PVK')
        )
    )

    # SAM (optional)
    if templates.get('sam_formula'):
        parts.append(
            templates['sam_formula'].format(
                formula_sam1=gv(row, 'Formula SAM 1'),
                concentration_sam1=gv(row, 'Concentration SAM 1'),
                formula_sam2=gv(row, 'Formula SAM 2'),
                concentration_sam2=gv(row, 'Concentration SAM 2'),
                formula_sam3=gv(row, 'Formula SAM 3'),
                concentration_sam3=gv(row, 'Concentration SAM 3')
            )
        )

    # Additives (optional)
    if templates.get('additive_formula'):
        parts.append(
            templates['additive_formula'].format(
                formula_add1=gv(row, 'Formula Additive 1'),
                concentration_add1=gv(row, 'Concentration Additive 1'),
                formula_add2=gv(row, 'Formula Additive 2'),
                concentration_add2=gv(row, 'Concentration Additive 2'),
                formula_add3=gv(row, 'Formula Additive 3'),
                concentration_add3=gv(row, 'Concentration Additive 3')
            )
        )

    # Process steps
    parts.append(
        templates['process'].format(
            spin1_speed=gv(row, 'Spin Coating Speed PVK 1'),
            spin1_time=gv(row, 'Spin Coating Time PVK 1'),
            spin2_speed=gv(row, 'Spin Coating Speed PVK 2'),
            spin2_time=gv(row, 'Spin Coating Time PVK 2')
        )
    )

    # Antisolvent
    parts.append(
        templates['antisolvent'].format(
            antisolvent_volume=gv(row, 'Antisolvent Volume'),
            antisolvent_timing=gv(row, 'Antisolvent Dropping Timing')
        )
    )

    # Annealing
    parts.append(
        templates['anneal'].format(
            anneal_temp=gv(row, 'Annealed Temperature PVK'),
            anneal_time=gv(row, 'Annealed Time PVK')
        )
    )

    # Passivation layer (optional)
    if templates.get('passivation_material'):
        parts.append(
            templates['passivation_material'].format(
                formula_passivator1=gv(row, 'Formula Passivator 1'),
                concentration_passivator1=gv(row, 'Concentration Passivator 1'),
                formula_passivator2=gv(row, 'Formula Passivator 2'),
                concentration_passivator2=gv(row, 'Concentration Passivator 2'),
                formula_passivator3=gv(row, 'Formula Passivator 3'),
                concentration_passivator3=gv(row, 'Concentration Passivator 3')
            )
        )
        if templates.get('passivation_spin'):
            parts.append(
                templates['passivation_spin'].format(
                    spin_speed_passivator=gv(row, 'Spin Coating Speed Passivator'),
                    spin_time_passivator=gv(row, 'Spin Coating Time Passivator')
                )
            )
        if templates.get('passivation_drop'):
            parts.append(
                templates['passivation_drop'].format(
                    passivator_timing=gv(row, 'Passivator Dropping Timing'),
                    passivator_volume=gv(row, 'Passivator Volume')
                )
            )
        if templates.get('passivation_anneal'):
            parts.append(
                templates['passivation_anneal'].format(
                    anneal_temp_passivator=gv(row, 'Annealed Temperature Passivator'),
                    anneal_time_passivator=gv(row, 'Annealed Time Passivator')
                )
            )

    # RGB (optional)
    rgb_keys = ['area_px2', 'gray_mean']
    if all(k in row.index for k in rgb_keys) and all(gv(row, k) != 'N/A' for k in rgb_keys):
        parts.append(
            templates['image_analysis'].format(
                coverage=gv(row, 'area_px2'),
                grayscale_value=gv(row, 'gray_mean'),
            )
        )

    # PL (optional)
    pl_keys = ['peak_time', 'decay_slope']
    if all(k in row.index for k in pl_keys) and all(gv(row, k) != 'N/A' for k in pl_keys):
        parts.append(
            templates['pl_analysis'].format(
                peak_time=gv(row, 'peak_time'),
                decay_slope=gv(row, 'decay_slope'),
            )
        )

    # XRD 12.6° segment (only use 12 template)
    if templates.get('xrd_analysis_12'):
        if gv(row, 'xrd_intensity_12.6') != 'N/A' and gv(row, 'xrd_fhwm_12.6') != 'N/A':
            parts.append(
                templates['xrd_analysis_12'].format(
                    xrd_intensity_12=gv(row, 'xrd_intensity_12.6'),
                    xrd_fhwm_12=gv(row, 'xrd_fhwm_12.6'),
                )
            )

    # XRD Stress/multi-peak segment (only use stress template)
    if templates.get('xrd_analysis_stress'):
        # Only write this section when xrd_Stress is valid
        if gv(row, 'xrd_Stress') != 'N/A':
            parts.append(
                templates['xrd_analysis_stress'].format(
                    xrd_intensity_4=gv(row, 'xrd_intensity_4'),
                    xrd_Stress=gv(row, 'xrd_Stress')
                )
            )

    return " ".join(parts)

def build_templates_for_row(row: pd.Series) -> dict:
    """Build template dictionary for a specific database row.

    This function randomly selects appropriate templates based on
    the presence of materials (SAM, additives, passivators).

    Args:
        row: Pandas Series containing experimental data.

    Returns:
        Dictionary mapping template keys to selected template strings.
    """
    prepared_term = random.choice(PREPARED_PHRASES)
    intro_template = random.choice(INTRO_SEGMENTS)
    perovskite_template = random.choice(PEROVSKITE_FORMULA_SEGMENTS)
    process_template = random.choice(PROCESS_SEGMENTS)
    antisolvent_template = random.choice(ANTISOLVENT_SEGMENTS)
    anneal_template = random.choice(ANNEAL_SEGMENTS)
    instruction_template = random.choice(INSTRUCTION_TEMPLATES)
    image_analysis_template = random.choice(IMAGE_ANALYSIS_SEGMENTS)
    pl_analysis_template = random.choice(PL_ANALYSIS_SEGMENTS)

    xrd_analysis_12 = random.choice(XRD_ANALYSIS_SEGMENTS_12)
    xrd_analysis_stress = random.choice(XRD_ANALYSIS_SEGMENTS_STRESS) if gv(row, 'xrd_Stress') != 'N/A' else ""

    # SAM
    sam1, sam2, sam3 = gv(row, 'Formula SAM 1'), gv(row, 'Formula SAM 2'), gv(row, 'Formula SAM 3')
    if sam1 == 'N/A':
        sam_formula_template = ""
    else:
        if sam2 == 'N/A' and sam3 == 'N/A':
            sam_formula_template = random.choice(SAM_FORMULA_SEGMENTS_SINGLE)
        elif sam3 == 'N/A':
            sam_formula_template = random.choice(SAM_FORMULA_SEGMENTS_DUAL)
        else:
            sam_formula_template = random.choice(SAM_FORMULA_SEGMENTS_TRIPLE)

    # Additives
    add1, add2, add3 = gv(row, 'Formula Additive 1'), gv(row, 'Formula Additive 2'), gv(row, 'Formula Additive 3')
    if add1 == 'N/A':
        additive_formula_template = ""
    else:
        if add2 == 'N/A' and add3 == 'N/A':
            additive_formula_template = random.choice(ADDITIVE_FORMULA_SEGMENTS_SINGLE)
        elif add3 == 'N/A':
            additive_formula_template = random.choice(ADDITIVE_FORMULA_SEGMENTS_DUAL)
        else:
            additive_formula_template = random.choice(ADDITIVE_FORMULA_SEGMENTS_TRIPLE)

    # Passivation layer
    passivation_material_template = ""
    passivation_spin_template = ""
    passivation_drop_template = ""
    passivation_anneal_template = ""
    if gv(row, 'Formula Passivator 1') != 'N/A':
        p2 = gv(row, 'Formula Passivator 2')
        p3 = gv(row, 'Formula Passivator 3')
        if p2 != 'N/A' and p3 != 'N/A':
            passivation_material_template = random.choice(PASSIVATION_MATERIAL_SEGMENTS_TRIPLE)
        elif p2 != 'N/A':
            passivation_material_template = random.choice(PASSIVATION_MATERIAL_SEGMENTS_DUAL)
        else:
            passivation_material_template = random.choice(PASSIVATION_MATERIAL_SEGMENTS_SINGLE)
        passivation_spin_template = random.choice(PASSIVATION_SPIN_SEGMENTS)
        passivation_drop_template = random.choice(PASSIVATION_DROP_SEGMENTS)
        passivation_anneal_template = random.choice(PASSIVATION_ANNEAL_SEGMENTS)

    return {
        'prepared_term': prepared_term,
        'intro': intro_template,
        'perovskite_formula': perovskite_template,
        'sam_formula': sam_formula_template,
        'additive_formula': additive_formula_template,
        'process': process_template,
        'antisolvent': antisolvent_template,
        'anneal': anneal_template,
        'instruction_template': instruction_template,
        'passivation_material': passivation_material_template,
        'passivation_spin': passivation_spin_template,
        'passivation_drop': passivation_drop_template,
        'passivation_anneal': passivation_anneal_template,
        'image_analysis': image_analysis_template,
    }

def row_to_text(row: pd.Series) -> str:
    """Convert database row to descriptive text.

    Args:
        row: Pandas Series containing experimental parameters.

    Returns:
        Generated descriptive text using random templates.
    """
    templates = build_templates_for_row(row)
    return generate_output_text(row, templates)

# Build template dictionary for a specific database row
# questions = {
#     "passivators": '''How does the peak intensity and residual stress of low dimensional perovskite characteristic peaks around 4 ° change in XRD characterization when passivating agents are used for surface treatment of perovskite?'''
# }

# questions = {
#     "additives": '''How will the peak intensity and half width of the 12.6 ° characteristic peak of additives added to perovskite precursors to prepare thin films change in XRD characterization?'''
# }

# questions = {
#     "sam": '''SAM is added to perovskite precursor to prepare thin films, and in-situ PL spectra are collected during annealing. How do the nucleation time and PL decay slope change, thereby affecting PCE, Voc, Jsc, and FF?'''
# }

questions = {
    "RGB": '''During the preparation of perovskite thin films, how do adjustments to perovskite composition concentration or process parameters affect the defect coverage ratio and grayscale intensity values obtained from image-based defect detection, thereby influencing the device performance parameters (PCE, Voc, Jsc, FF)?'''
}

import pandas as pd
from pathlib import Path
import json


import pandas as pd
import random
import json
from sqlalchemy import create_engine


DB_CONFIG: Dict[str, Any] = {}

def get_random_row_from_db(config: Dict[str, Any]) -> pd.Series:
    """Fetch random row from MySQL database.

    Args:
        config: Database configuration with keys:
            - host: Database host
            - user: Username
            - password: Password
            - database: Database name
            - port: Port number
            - table: Table name

    Returns:
        Pandas Series containing random row data.

    Raises:
        ValueError: If table is empty.
    """
    engine = create_engine(
        f"mysql+pymysql://{config['user']}:{config['password']}@"
        f"{config['host']}:{config['port']}/{config['database']}?charset=utf8mb4"
    )
    table = config['table']
    query = f"SELECT * FROM `{table}` ORDER BY RAND() LIMIT 1;"
    df = pd.read_sql(query, engine)
    if df.empty:
        raise ValueError("Table is empty")
    return df.iloc[0]


import pandas as pd
from sqlalchemy import create_engine

def get_all_rows_from_db(config: Dict[str, Any]) -> pd.DataFrame:
    """Fetch all rows from MySQL database.
    Args:
        config: Database configuration with keys: host, user, password, database, port, table
    Returns:
        Pandas DataFrame containing all row data.
    """
    engine = create_engine(
        f"mysql+pymysql://{config['user']}:{config['password']}@"
        f"{config['host']}:{config['port']}/{config['database']}?charset=utf8mb4"
    )
    table = config['table']

    query = f"SELECT * FROM `{table}`;"
    df = pd.read_sql(query, engine)
    if df.empty:
        print("Warning: Table is empty")
    return df



def main():
    """Main function to test text generation from database."""
    try:
        row = get_random_row_from_db(DB_CONFIG)
        row.index = row.index.str.strip()
        print("Random row from database:\n")
        print(row)
        output_text = row_to_text(row)
        print("Generated descriptive text:\n")
        print(output_text)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
