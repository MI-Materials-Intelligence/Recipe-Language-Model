from __future__ import annotations
def run_pass_report(
    *,
    seed: int | None = None,
    verbose: bool = True,
) -> None:
    """
    Run Image Process pipeline.

    Parameters
    ----------
    seed : int | None
        Override random seed (optional).
    verbose : bool
        Print start / end logs.
    """
    if verbose:
        print("▶ Running pass pair to report...")

    if seed is not None:
        import random
        import numpy as np
        random.seed(seed)
        np.random.seed(seed)

    main()

    if verbose:
        print("✅ Running pass pair to report finished.")



from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json
import mysql.connector
from pathlib import Path
import os
import re
from openai import OpenAI

import traceback  # ✅ Correct spelling
SYSTEM_PROMPT_ABSTRACT = (
    "You are a scientific writing assistant and an expert in the field of perovskite solar cells. "
    "Your task is to write an English ABSTRACT for a scientific paper (250–300 words) based only on the information provided by the user. "
    "FORMATTING RULES (MUST OBEY): "
    "• Output MUST be ONE SINGLE PARAGRAPH of continuous plain text. "
    "• Do NOT insert any headings, titles, section labels, Markdown (no '###', no bold, no lists). "
    "• Do NOT use bullet points or numbered lists. "
    "• Do NOT start with the word 'Abstract' or any title. "
    "• Do NOT insert blank lines or line breaks inside the abstract. "
    "CONTENT REQUIREMENTS: "
    "The abstract should follow this logical structure: "
    "(1) giving the background, briefly mentioning the potential of inverted (p–i–n) perovskite solar cells; "
    "(2) summarizing the key fabrication strategy or core process optimization(s), preferably in a 'from A to B' form (e.g., SAM, passivation agent or additive engineering); "
    "(3) reporting the main performance indicators (PCE, VOC, JSC, FF) and their improvement range. Only mention parameters that show a clear increase; if an index is flat or slightly decreased, do not mention it; "
    "(4) giving concise mechanism insights to explain why the improved recipe outperforms the control, without going into excessive detail; "
    "(5) concluding with the overall significance and potential impact of this optimization. "
    "Be precise and factual; avoid citations, figure/table mentions, and avoid introducing any information that is not supported by the input."
)

SYSTEM_PROMPT_TABLE = '''
You are a technical writing assistant for perovskite solar cells.

Your ONLY task in this conversation:
- Read the user's input (Result and Discussion).
- Then output ONE Markdown table.

VERY IMPORTANT FORMAT RULES:
- Output ONLY one Markdown table.
- Do NOT output any text before or after the table.
- Do NOT use code fences (no ```).
- Do NOT write headings or paragraphs.

The table MUST have EXACTLY these three columns in this order:
| F/P Optimization | Performance | Mechanism |

ROW RULES:
- Make ONE row for each metric that improved (VOC, JSC, FF, PCE).
- If a metric did not improve, do NOT make a row for it.

COLUMN CONTENT:
- F/P Optimization: describe the key formulation/process change using details from the input
(e.g., replacing PEABr with MACl at 0.7 mg/mL and reducing PSP to 2.0 mg/mL).
- Performance: write "from → to (+gain)" with units, for example:
VOC: 0.99 V → 1.03 V (+0.04 V)
JSC: 22.94 → 23.74 mA cm⁻² (+0.80 mA cm⁻²)
FF: 69.16% → 74.46% (+5.30 pct)
PCE: 15.76% → 18.35% (+2.59 pct)
- Mechanism: Detailed description of the mechanism and reasons for performance changes (e.g., dipole-induced work-function shift, defect passivation, band alignment, recombination suppression.).

DATA:
- Use ONLY numbers and mechanisms from the user's input.
'''


def get_answer_and_thinking(
    question: str,
    control: str,
    target: str,
    background_knowledge: str,
    Passivator: str,
):
    """
    Main analysis: return (answer_content_analyze, reasoning_content_analyze)
    """
    global client
    if client is None:
        raise RuntimeError("Please initialize the client object before calling get_answer_and_thinking.")

    # system prompt contains general role + background knowledge
    system_prompt = (
        "You are an expert in the field of perovskite solar cells. "
        "Please answer the question according to the professional background I provided. "
    )
    if background_knowledge:
        system_prompt += (
            "Here is the material-related background knowledge (selected by SAM):\n"
            f"{background_knowledge}"
        )
    else:
        system_prompt += (
            "No additional external background knowledge was provided for this question; "
            "please rely on your internal expertise."
        )

    # Pack question + control + target into the same user prompt
    user_content = (
        "You are given an original perovskite device (control) and an optimized device (target). "
        "Please analyze them and answer the question.\n\n"
        "Question:\n"
        f"Aiming at {Passivator}, {question}\n\n"
        "Control description:\n"
        f"{control}\n\n"
        "Target description:\n"
        f"{target}\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    completion = client.chat.completions.create(
        model="qwen-plus",  # Change to your own modelqwen3-max-preview
        messages=messages,
        extra_body={"enable_thinking": True},
        stream=True,
    )

    reasoning_content = ""  # Complete thinking process
    answer_content = ""     # Complete response
    is_answering = False

    for chunk in completion:
        if not getattr(chunk, "choices", None):
            usage = getattr(chunk, "usage", None)
            if usage:
                print("\nUsage:")
                print(usage)
            continue

        delta = chunk.choices[0].delta

        # Collect "thinking process"
        if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
            reasoning_content += delta.reasoning_content

        # Collect formal response
        if hasattr(delta, "content") and delta.content:
            if not is_answering:
                print("\n" + "=" * 20 + "Complete Response" + "=" * 20 + "\n")
                is_answering = True
            answer_content += delta.content

    return answer_content.strip(), reasoning_content.strip()

def load_pending_items(limit: int | None = None, factor_type: str = "SAM"):
    """
    Load pending records of specified regulation factor type
    factor_type: "SAM", "Additive", "Passivator", "Process"
    """
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True)

    # Select non-empty field based on type
    if factor_type == "SAM":
        condition = "sam IS NOT NULL AND sam != '' AND sam != '[]'"
    elif factor_type == "Additive":
        condition = "additive IS NOT NULL AND additive != '' AND additive != '[]'"
    elif factor_type == "Passivator":
        condition = "passivator IS NOT NULL AND passivator != '' AND passivator != '[]'"
    elif factor_type == "Process":
        condition = "process IS NOT NULL AND process != '' AND process != '[]'"
    else:
        raise ValueError("factor_type must be one of SAM / Additive / Passivator / Process")

    sql = f"""
    SELECT
        id,
        question,
        control,
        target,
        additive,
        passivator,
        sam,
        process,
        pair_source,
        sample_id_1,
        sample_id_2,
        sample_id_1_date,
        sample_id_2_date
    FROM {TABLE_NAME}
    WHERE status = 'pending' AND ({condition})
    ORDER BY id ASC
    """

    if limit is not None:
        sql += f" LIMIT {int(limit)}"

    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"📥 Loaded {factor_type} type pending records count: {len(rows)}")
    return rows

def db_row_to_item(row: dict) -> dict:
    """
    Convert a database row to your original JSON item structure
    (Ensures zero intrusion to subsequent logic)
    """

    item = {
        "question": row.get("question"),
        "control": row.get("control"),
        "target": row.get("target"),
        "pair_source": row.get("pair_source"),
        "sample_id_1": row.get("sample_id_1"),
        "sample_id_2": row.get("sample_id_2"),
        "sample_id_1_date": row.get("sample_id_1_date"),
        "sample_id_2_date": row.get("sample_id_2_date"),
    }

    # ⚠️ Only one of the four regulation factor types will match
    if row.get("sam"):
        item["SAM"] = json.loads(row["sam"]) if isinstance(row["sam"], str) else row["sam"]

    if row.get("additive"):
        item["Additive"] = json.loads(row["additive"]) if isinstance(row["additive"], str) else row["additive"]

    if row.get("passivator"):
        item["Passivator"] = json.loads(row["passivator"]) if isinstance(row["passivator"], str) else row["passivator"]

    if row.get("process"):
        item["Process"] = json.loads(row["process"]) if isinstance(row["process"], str) else row["process"]

    return item
def get_material_background_from_item(
    item: dict,
    material_content_map: dict,
    cache: dict
) -> str:
    """
    Extract material names from item (currently only from SAM),
    match in material_content_map loaded from database,
    concatenate corresponding markdown content as background knowledge.
    """

    material_names = []

    # ⚠️ Currently you explicitly say: only extract from SAM
    for key in ("Passivator",):
        vals = item.get(key) or []
        if isinstance(vals, list):
            material_names.extend(vals)
        else:
            if vals:
                material_names.append(vals)

    # Deduplicate + clean
    material_names = list({m for m in material_names if m})

    background_chunks = []

    for raw_name in material_names:
        norm_name = normalize_material_name(raw_name)

        # Use directly if in cache
        if norm_name in cache:
            background_chunks.append(cache[norm_name])
            continue

        content = material_content_map.get(norm_name)
        if content:
            cache[norm_name] = content
            background_chunks.append(content)
        else:
            print(
                f"[WARN] Material '{raw_name}' "
                f"(normalized as '{norm_name}') markdown not found in database"
            )

    if background_chunks:
        return "\n\n".join(background_chunks)
    else:
        return ""
# ========== 1. General LLM call encapsulation ==========

# === Global configuration (loaded from config file) ===
import sys
from pathlib import Path as PathLib
script_dir = PathLib(__file__).parent
generate_root = script_dir.parent.parent  # characterization_function -> generate
if str(generate_root) not in sys.path:
    sys.path.insert(0, str(generate_root))

# Import configuration loader (using Generating/src/config_loader.py)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from seven_ai_layers_robotics.config import config

# Load configuration from app.config
MYSQL_CONFIG = {
    'host': config.generating_database.host,
    'port': config.generating_database.port,
    'user': config.generating_database.user,
    'password': config.generating_database.password,
    'database': config.generating_database.database,
    'charset': config.generating_database.charset,
}
llm_config = {
    'api_key': config.generating_llm.dashscope_api_key,
    'base_url': config.generating_llm.base_url,
    'model': config.generating_llm.dashscope_model,
    'temperature': config.generating_llm.temperature,
    'timeout': config.generating_llm.timeout,
}

client = OpenAI(
    api_key=llm_config["api_key"],
    base_url=llm_config["base_url"]
)

TABLE_NAME = "characterisation_match"

# === Lock: for safe JSONL file writing ===
sft_file_lock = threading.Lock()
report_file_lock = threading.Lock()

# === Utility functions (unchanged) ===
def normalize_material_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    return re.sub(r"[^A-Z0-9]+", "", name.upper())

def ensure_parent_dir(path: str):
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

def build_material_content_map_from_db(category: str | None = None):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True)
    if category is not None:
        query = """
            SELECT material, content
            FROM expert_mechanisms
            WHERE content IS NOT NULL AND content != '' AND category = %s
        """
        cursor.execute(query, (category,))
    else:
        query = """
            SELECT material, content
            FROM expert_mechanisms
            WHERE content IS NOT NULL AND content != ''
        """
        cursor.execute(query)
    material_content_map = {}
    for row in cursor.fetchall():
        raw_material = row["material"]
        content = row["content"]
        key = normalize_material_name(raw_material)
        if key and content:
            material_content_map[key] = content
    cursor.close()
    conn.close()
    return material_content_map

def update_status(pair_id: int, status: str):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {TABLE_NAME} SET status = %s WHERE id = %s", (status, pair_id))
    conn.commit()
    cursor.close()
    conn.close()
def api_get_answer_and_thinking(system_prompt: str, user_prompt: str):
    """
    Secondary call (abstract / table): input system + user, with built-in reasoning_content.
    Return (answer_content, reasoning_content)
    """
    global client
    if client is None:
        raise RuntimeError("Please initialize the client object before calling api_get_answer_and_thinking.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    completion = client.chat.completions.create(
        model="qwen-plus",  # Change to your own modelqwen3-max-preview
        messages=messages,
        extra_body={"enable_thinking": True},
        stream=True,
    )

    reasoning_content = ""
    answer_content = ""
    is_answering = False

    for chunk in completion:
        if not getattr(chunk, "choices", None):
            usage = getattr(chunk, "usage", None)
            if usage:
                print("\nUsage (abstract/table):")
                print(usage)
            continue

        delta = chunk.choices[0].delta

        if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
            reasoning_content += delta.reasoning_content

        if hasattr(delta, "content") and delta.content:
            if not is_answering:
                is_answering = True
            answer_content += delta.content

    return answer_content.strip(), reasoning_content.strip()

# === LLM call functions (unchanged) ===
# ... [get_answer_and_thinking, api_get_answer_and_thinking, SYSTEM_PROMPT_ABSTRACT, SYSTEM_PROMPT_TABLE] ...

# === Single item processing function (key: thread-safe) ===
def process_single_item(
    pair_id: int,
    item: dict,
    material_content_map: dict,
    output_paths: dict,
):
    try:
        question = (item.get("question") or "").strip()
        control = (item.get("control") or "").strip()
        target = (item.get("target") or "").strip()
        passivator = item.get("Passivator", "")

        # Extract material names for printing
        materials_for_print = []
        for key in ("Passivator", "Additive", "SAM", "Process"):
            vals = item.get(key) or []
            if isinstance(vals, list):
                materials_for_print.extend(vals)
            elif vals:
                materials_for_print.append(vals)
        mat_info = ",".join(materials_for_print)

        print(f"\n========== Processing ID={pair_id} | Material [{mat_info}] ==========")
        print(f"Question: {question}")

        # Get background knowledge (read-only, thread-safe)
        background_knowledge = get_material_background_from_item(item, material_content_map, {})

        # First call: main analysis
        answer_content_analyze, reasoning_content_analyze = get_answer_and_thinking(
            question=question,
            control=control,
            target=target,
            background_knowledge=background_knowledge,
            Passivator=passivator
        )

        safe_control = control.replace('"', '\\"')
        safe_target = target.replace('"', '\\"')
        input_text = f'"control": "{safe_control}", "target": "{safe_target}"'

        # Second call: abstract
        user_prompt_abstract = f"""
Method (key fabrication details):
{input_text}

Results & Discussion (performance & mechanisms):
{answer_content_analyze}

Now write the ABSTRACT according to the system instructions above.
Output ONLY the abstract text as ONE SINGLE PARAGRAPH of 250–300 words,
with no title, no headings, no bullet points, and no extra line breaks.
Do not add any explanations before or after the abstract.
"""
        answer_content_abstract, reasoning_content_abstract = api_get_answer_and_thinking(
            SYSTEM_PROMPT_ABSTRACT, user_prompt_abstract
        )

        # Third call: table
        user_prompt_table = f"""
[REAL INPUT]
Results & Discussion (performance & mechanisms):
{answer_content_analyze}

[REAL OUTPUT]
Now, based on the INPUT above, write ONLY the Markdown table.
Start your answer with the header row:
| F/P Optimization | Performance | Mechanism |
"""
        answer_content_table, reasoning_content_table = api_get_answer_and_thinking(
            SYSTEM_PROMPT_TABLE, user_prompt_table
        )

        # Build report
        sample_info = {
            "sample_id_1": item.get("sample_id_1"),
            "sample_id_2": item.get("sample_id_2"),
            "sample_id_1_date": item.get("sample_id_1_date"),
            "sample_id_2_date": item.get("sample_id_2_date"),
        }
        filename = 'characterisation_pl_sam.csv'
        report = {
            "source_file": filename,
            "meta": {"Sample_Information": sample_info},
            "1_Abstract": answer_content_abstract,
            "2_Method": {
                "2_1_Control_F_P": control,
                "2_2_Optimized_F_P": target,
            },
            "3_Result_Discussion": answer_content_analyze,
            "4_Conclusion": {"4_1_Table": answer_content_table},
            "5_Supporting_Information": background_knowledge,
        }

        record = {
            "instruction": question,
            "input": input_text,
            "output": f"<think>{reasoning_content_analyze}</think><answer>{answer_content_analyze}</answer>",
        }

        # Safe write to JSONL
        with sft_file_lock:
            with open(output_paths["sft_jsonl"], "a", encoding="utf-8-sig") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()

        with report_file_lock:
            with open(output_paths["report_jsonl"], "a", encoding="utf-8-sig") as f:
                f.write(json.dumps(report, ensure_ascii=False) + "\n")
                f.flush()

        update_status(pair_id, "done")
        return record, report

    except Exception as e:
        print(f"❌ ID={pair_id} processing failed: {e}")
        traceback.print_exc()
        update_status(pair_id, "error")
        return None, None

# === Main function modification ===
def main() -> None:
    script_dir = Path(__file__).parent.resolve()
    # Output to Generating/data directory
    generating_root = script_dir.parent.parent  # Characterisation_Reporting -> Generating
    data_root = generating_root / "data"
    output_dir = data_root / "characterisation_xrd_passivators"
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "sft_json": output_dir / "sft_pairs_with_think_answer.json",
        "sft_jsonl": output_dir / "sft_pairs_with_think_answer.jsonl",
        "report_json": output_dir / "reports.json",
        "report_jsonl": output_dir / "reports.jsonl",
    }

    # Clear or create JSONL files
    for p in [paths["sft_jsonl"], paths["report_jsonl"]]:
        ensure_parent_dir(p)
        open(p, "w").close()  # Clear

    # Load material library (read-only, shareable)
    material_content_map = build_material_content_map_from_db("Passivator Mechanism Library")

    # Load pending items
    db_rows = load_pending_items(factor_type="Passivator")
    if not db_rows:
        print("✅ No pending records, exiting")
        return

    items = [(row["id"], db_row_to_item(row)) for row in db_rows]
    print(f"🚀 Preparing to process {len(items)} records in parallel...")

    records = []
    reports = []

    # ⚠️ Control concurrency (recommend 3~5 to avoid API rate limiting)
    max_workers = 4

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_single_item, pair_id, item, material_content_map, paths)
            for pair_id, item in items
        ]

        for future in as_completed(futures):
            record, report = future.result()
            if record and report:
                records.append(record)
                reports.append(report)

    # Save complete JSON arrays
    with open(paths["sft_json"], "w", encoding="utf-8-sig") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)
    with open(paths["report_json"], "w", encoding="utf-8-sig") as f:
        json.dump(reports, f, ensure_ascii=False, indent=4)

    print(f"✅ All completed! Processed {len(records)} records in total")
    print(f"📄 SFT JSON: {paths['sft_json']}")
    print(f"📄 Report JSON: {paths['report_json']}")
    print(f"📄 SFT JSONL: {paths['sft_jsonl']}")
    print(f"📄 Report JSONL: {paths['report_jsonl']}")

# === Other helper functions (db_row_to_item, get_material_background_from_item, load_pending_items) remain unchanged ===
# ... [Please keep your original functions here] ...

if __name__ == "__main__":
    run_pass_report()
    