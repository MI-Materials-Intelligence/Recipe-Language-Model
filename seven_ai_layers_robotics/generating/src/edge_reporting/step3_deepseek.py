# -*- coding: utf-8 -*-
"""
Stage 2: Process records with status=1 in  one by one
- Extract the experimental description with id from the .docx file specified by location
- Call DeepSeek to generate mechanism analysis
- Save as {type}_{id}.json
- Update status=2 upon success
"""

import os
import re
import json
import requests
from docx import Document
import pymysql
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================== Configuration Area ==================
# Load configuration from app.config
from seven_ai_layers_robotics.config import config

# Load DeepSeek configuration from config
DEEPSEEK_CONFIG = {
    'api_key': config.deepseek.api_key,
    'base_url': config.deepseek.base_url,
    'model': config.deepseek.model,
    'temperature': config.deepseek.temperature,
    'timeout': config.deepseek.timeout,
}

# Database configuration
DB_CONFIG = {
    'host': config.generating_database.host,
    'port': config.generating_database.port,
    'user': config.generating_database.user,
    'password': config.generating_database.password,
    'database': config.generating_database.database,
    'charset': config.generating_database.charset,
}

# DeepSeek API configuration
DEEPSEEK_API_KEY = DEEPSEEK_CONFIG.get("api_key", "")
API_URL_BASE = DEEPSEEK_CONFIG.get("base_url", "https://api.deepseek.com/v1/chat/completions")
# Ensure API_URL includes the complete /chat/completions path
if not API_URL_BASE.endswith("/chat/completions"):
    API_URL = API_URL_BASE.rstrip("/") + "/chat/completions"
else:
    API_URL = API_URL_BASE
MODEL_NAME = DEEPSEEK_CONFIG.get("model", "deepseek-reasoner")

# JSON output root directory (subdirectories by type)
# Automatically get current script directory and concatenate relative path to Generating/data/edge
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_ROOT_DIR = os.path.join(SCRIPT_DIR, "..", "..", "data", "edge")

# Reports directory (fixed path)
REPORTS_DIR = os.path.join(JSON_ROOT_DIR, "reports")

# .docx file mapping: type -> docx filename
DOCX_FILES_MAP = {
    "characterisation_pl_sam": "characterisation_pl_sam.docx",
    "characterisation_xrd_additives": "characterisation_xrd_additives.docx",
    "characterisation_xrd_passivators": "characterisation_xrd_passivators.docx",
    "characterisation_image_pvk": "characterisation_image_pvk.docx",
    "experiments_cleaned_data": "experiments_cleaned_data.docx"  # default/generic
}

MAX_WORKERS = 3  # DeepSeek may have rate limits, recommend ≤3

PROMPT_TEMPLATE = """
You are an expert in perovskite crystallization physics, interface chemistry, defect passivation, molecular engineering, and structural/optical characterization.

You will receive a full experimental description. Your task is to generate a **single continuous scientific paragraph** that integrates all mechanisms.

============================================================
STRICT INTERNAL REASONING RULES (DO NOT OUTPUT THESE SEPARATELY)
============================================================
Before writing the final paragraph, you must internally perform the following reasoning steps.  
These steps MUST NOT appear in the output, but the final paragraph MUST REFLECT them.

1. **Perovskite Layer Analysis (MANDATORY):**
   - Analyze the ABX3 structure (A-site, B-site, X-site roles).
   - Discuss phase stability, bandgap, tolerance factor, ion migration tendency.
   - Explain crystallization dynamics influenced by: precursor concentration, spin speeds, antisolvent timing/volume, annealing temperature/time.
   - Explain how these influence defect formation, carrier lifetime, morphology, recombination, and VOC/JSC/FF.

2. **For SAMs (if there are multiple SAMs, e.g., SAM1, SAM2, SAM3):**
   For EACH SAM:
       - Internally analyze: molecular structure, anchoring group, dipole moment, energy-level modulation, surface passivation roles.
   For ALL PAIRS of SAM combinations:
       - Internally analyze pairwise synergy.
   For ≥3 SAMs together:
       - Internally analyze collective synergy.
   All mechanisms MUST be integrated naturally into the final paragraph.

3. **For Additives (if multiple):**
   - Internally analyze individual roles.
   - Internally analyze pairwise synergy.
   - Internally analyze collective effects on nucleation, intermediate phases, grain growth, defect suppression.
   Integrated naturally into the paragraph.

4. **For Passivators (if multiple):**
   - Individual function.
   - Pairwise synergy.
   - Collective synergy.
   Integrated naturally into the paragraph.

🔥 5. **Characterization-Driven Mechanism Analysis (CONDITIONAL, MANDATORY IF PRESENT):**

   - If **image-derived characterization data** (e.g., film coverage metrics, grayscale intensity, defect density indicators, morphological uniformity descriptors extracted from optical/PL mapping images) is present:
       - Internally analyze thin-film continuity, defect distribution, crystallization uniformity, and their influence on charge transport pathways and non-radiative recombination.
       - Treat image-derived analysis strictly as *morphological and spatial evidence*, not as process description.

   - If **PL-related data** (e.g., PL intensity evolution, lifetime, decay slope, nucleation timing) is present:
       - Internally analyze carrier recombination pathways, defect density, crystallization kinetics, and radiative efficiency.

   - If **XRD-related data** (e.g., PbI₂ peaks at ~12.6°, 2D phase features, peak intensity/FWHM, residual stress indicators) is present:
       - Internally analyze crystallographic phase purity, secondary phase suppression, strain/stress state, and structural stability.

   - If **multiple characterization types (image / PL / XRD)** are present:
       - Internally analyze how *morphological, optical, and structural evidence jointly corroborate* defect suppression, crystallization control, and interfacial quality.

   - If a characterization type is NOT present, it MUST NOT be mentioned.


🔥 6. **STRICT ORDERING CONSTRAINT FOR FINAL PARAGRAPH (INTERNAL):**
   - Characterization-driven mechanisms (Image/PL/XRD) MUST be placed:
     **AFTER passivation mechanisms and BEFORE performance metrics**
   - Performance metrics MUST appear at the very end of the paragraph.

============================================================
FINAL OUTPUT RULES (THIS IS WHAT YOU ACTUALLY OUTPUT)
============================================================

You MUST output **one single, continuous, deeply reasoned scientific paragraph in English**, with:

1. Explicit explanation of:
   - Each SAM / additive / passivator individually
   - Synergy between every pair
   - Collective synergy of all components
   - Interaction with perovskite crystallization and interface charge transport
   - **Characterization-based physical evidence (Image/PL/XRD), if present**

2. No bullets, no lists, no headings.

3. The paragraph must read like a Nature Energy / Joule mechanism discussion.

4. The **final sentence MUST place the performance parameters (VOC, JSC, FF, PCE) at the end**, in ANY order.

============================================================

Now analyze the following experimental description and answer with ONE paragraph:

[Experimental Description]  
{experiment}
"""

# ================== Utility Functions ==================

def read_docx_paragraphs(docx_path):
    doc = Document(docx_path)
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]

def split_experiments_by_number(paragraphs):
    """Return [(index_str, text), ...]"""
    experiments = []
    current_block = []
    current_index = None
    number_pattern = re.compile(r'^(\d+)[\.\)]\s+')

    for para in paragraphs:
        m = number_pattern.match(para)
        if m:
            if current_index is not None:
                experiments.append((current_index, "\n".join(current_block).strip()))
                current_block = []
            current_index = m.group(1)
            cleaned = number_pattern.sub('', para, count=1).strip()
            current_block.append(cleaned)
        else:
            current_block.append(para)
    if current_index is not None and current_block:
        experiments.append((current_index, "\n".join(current_block).strip()))
    return experiments

def find_experiment_by_id(paragraphs, target_id):
    """Find the experimental description text with number target_id from .docx paragraphs"""
    try:
        target_id = str(int(float(target_id)))  # Compatible with 1.0 → "1"
    except:
        target_id = str(target_id)

    experiments = split_experiments_by_number(paragraphs)
    for idx_str, text in experiments:
        if idx_str == target_id:
            return text
    raise ValueError(f"Experimental description with number {target_id} not found in .docx")

def call_deepseek_api(experiment_text):
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": PROMPT_TEMPLATE.format(experiment=experiment_text)}],
        "temperature": 0.3
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return content.strip()

def extract_summary_from_mechanism(mechanism_text):
    lines = [l.rstrip() for l in mechanism_text.splitlines()]
    summary_lines = []
    started = False
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if started: summary_lines.append("")
            continue
        if not started and "Integrated Mechanism Summary" in line:
            started = True
            line = re.sub(r'\*\*|Integrated Mechanism Summary[:：]?', '', line, flags=re.IGNORECASE).strip()
            if line: summary_lines.append(line)
            continue
        if started:
            summary_lines.append(line)
    if started and summary_lines:
        return " ".join(l for l in summary_lines if l).strip()
    return mechanism_text.strip()

def build_json_obj(experiment_text, summary_text):
    return {
        "1_Abstract": {},
        "2_Introduction": experiment_text,
        "3_Result_Discussion": summary_text,
        "4_Conclusion": {},
        "5_Supporting_Information": {"substance": "", "reference": ""}
    }

# ================== Database Operations ==================

def fetch_pending_records():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT `index`, `type`, `id`, `location` FROM `` WHERE `status` = 1")
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return records

def mark_as_done(report_index):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("UPDATE `` SET `status` = 2 WHERE `index` = %s", (report_index,))
    conn.commit()
    cursor.close()
    conn.close()

# ================== Single Record Processing Function ==================

def process_single_record(report_index, record_type, record_id, docx_path):
    # 1. Construct JSON path
    json_dir = os.path.join(JSON_ROOT_DIR, record_type)
    json_path = os.path.join(json_dir, f"{record_id}.json")

    # 2. Skip if JSON already exists
    if os.path.exists(json_path):
        print(f"⏭️  JSON already exists, skipping: {json_path}")
        mark_as_done(report_index)
        return

    # 3. Read .docx and extract corresponding paragraph
    # Determine which .docx file to use based on type
    docx_filename = DOCX_FILES_MAP.get(record_type, "experiments_cleaned_data.docx")
    docx_path_fixed = os.path.join(REPORTS_DIR, docx_filename)

    if not os.path.exists(docx_path_fixed):
        raise FileNotFoundError(f".docx file does not exist: {docx_path_fixed} (type={record_type})")

    paragraphs = read_docx_paragraphs(docx_path_fixed)
    exp_text = find_experiment_by_id(paragraphs, record_id)
    print(f"Experiment text for {record_id}:\n{exp_text}\n")

    # 4. Call DeepSeek
    mechanism_full = call_deepseek_api(exp_text)
    print(f"Mechanism for {record_id}:\n{mechanism_full}\n")
    summary = extract_summary_from_mechanism(mechanism_full)
    print(f"Summary for {record_id}:\n{summary}\n")

    # 5. Save JSON
    os.makedirs(json_dir, exist_ok=True)
    json_obj = build_json_obj(exp_text, summary)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON generated: {json_path}")

    # 6. Update status
    mark_as_done(report_index)

# ================== Main Process ==================

def main():
    print("🔍 Starting Stage 2: Processing records with status=1 in ...")
    records = fetch_pending_records()
    if not records:
        print("📭 No pending records")
        return

    print(f"📥 Found {len(records)} pending records in total")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for rec in records:
            fut = executor.submit(
                process_single_record,
                rec['index'],
                rec['type'],
                rec['id'],
                rec['location']  # This is the .docx path
            )
            futures.append(fut)

        for i, fut in enumerate(as_completed(futures)):
            try:
                fut.result()
                print(f"[{i+1}/{len(records)}] Completed one record processing")
            except Exception as e:
                print(f"❌ Processing failed: {e}")

    print("🎉 Stage 2 completed!")

if __name__ == "__main__":
    main()