import os
import os.path as osp
import json
import random
import re
import uuid
from typing import Dict, Any, List, Optional
import asyncio
from openai import AsyncOpenAI
from collections import defaultdict
import pymysql
import mysql.connector
from mysql.connector import Error

# ===== Config Loader =====
def _load_recipeqa_config() -> Dict[str, Any]:
    """Load RecipeQA configuration from config.toml.

    Returns:
        Dictionary containing LLM and database configuration.
    """
    try:
        from pathlib import Path
        import tomllib

        # Try multiple possible paths
        current_file = Path(__file__).resolve()

        # Path 1: recipeQA -> seven_ai_layers_robotics -> project root (2 levels up)
        project_root = current_file.parent.parent.parent
        config_path = project_root / "config.toml"

        # Path 2: Try alternative path structure
        if not config_path.exists():
            project_root = current_file.parent.parent.parent.parent
            config_path = project_root / "config.toml"

        if not config_path.exists():
            print(f"[WARN] Config file not found: {config_path}, using default values")
            return {}

        with config_path.open("rb") as f:
            config = tomllib.load(f)

        # Return recipeqa_llm configuration
        recipeqa_llm_config = config.get("recipeqa_llm", {})
        recipeqa_db_config = config.get("recipeqa", {}).get("database", {})

        result = {}
        if recipeqa_llm_config:
            result.update(recipeqa_llm_config)
        if recipeqa_db_config:
            result["database"] = recipeqa_db_config

        return result
    except Exception as e:
        print(f"[WARN] Failed to load config: {e}, using default values")
        return {}


RECIPEQA_CONFIG: Dict[str, Any] = _load_recipeqa_config()

# Import configuration from app.config
import sys
from pathlib import Path as PathLib
script_dir = PathLib(__file__).parent
recipeqa_root = script_dir.parent.parent  # report_to_qa -> RecipeQA
if str(recipeqa_root) not in sys.path:
    sys.path.insert(0, str(recipeqa_root))

try:
    from seven_ai_layers_robotics.config import config
    RECIPEQA_LLM_CONFIG = {
        'api_key': config.recipeqa_llm.dashscope_api_key,
        'base_url': config.recipeqa_llm.base_url,
        'model': config.recipeqa_llm.dashscope_model,
        'temperature': config.recipeqa_llm.temperature,
        'timeout': config.recipeqa_llm.timeout,
    }
except Exception as e:
    print(f"[WARN] Failed to import from app.config: {e}, using default values")
    RECIPEQA_LLM_CONFIG = {}

# ===== Config =====
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # RecipeQA
DATA_DIR: str = os.path.join(BASE_DIR, "..", "data")  # RecipeQA/data/

# Load LLM configuration from app.config
LLM_CONFIG: Dict[str, Any] = RECIPEQA_LLM_CONFIG or {
    'api_key': '',
    'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    'model': '',
    'temperature': 0.4,
    'timeout': 60,
}

MAX_CONCURRENT_REQUESTS: int = 5
MAX_RETRIES: int = 5
RETRY_BASE_DELAY: int = 10

MAPPING_RELATION: Dict[str, str] = {
    "DMAcPA": "DMACPA",
    "PEACI": "PEACl",
    "PY3": "py3",
    "Py3": "py3",
    "PEACL": "PEACl",
}

client: AsyncOpenAI = AsyncOpenAI(
    api_key=LLM_CONFIG["api_key"],
    base_url=LLM_CONFIG["base_url"]
)
semaphore: asyncio.Semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

SYS_PROMPT = """
You are a perovskite mechanims expert.
Knowledge you may use:
Provided Background Knowledge(Materials Mechanism Knowledge). Do not use any other sources.
Task: For the newly supplied formulation(s), give a mechanism-level analysis that explains the observed device behavior (e.g., Jsc, FF, Voc or any metrics provided).
Constraints:
- Background Knowledge (internal reasoning only), Background Knowledge is internal only. Never mention "background / provided / expert analysis / given text" etc.
- Use only the two provided knowledge sources; no external facts or guesses.
- Focus on formulation effects; ignore processing/fabrication details unless explicitly defined as part of the formulation identity.
- Explicitly connect formulation → (defects/recombination/transport/interfaces/ion migration/morphology) → (Voc/Jsc/FF/PCE).
- Be deep, specific, and correct; avoid generic or boilerplate statements.
"""

USER_PROMPT = """
Background Knowledge: {reference_analysis},
Perovskite formula and process as Control: {control_device_fabrication},
Optimized parameters for perovskite formula and process: {target_device_fabrication}
"""

# ===== Utils =====
def safe_filename(name: str) -> str:
    """Remove invalid characters from filename.

    Args:
        name: Original filename.

    Returns:
        Sanitized filename with invalid characters replaced by underscores.
    """
    name = (name or "").strip()
    return re.sub(r'[\\/:\*?"<>\|]+', '_', name)

def read_text_file(path: str) -> str:
    """Read text content from file.

    Args:
        path: File path to read.

    Returns:
        File content as string.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def atomic_write_json(path: str, data: Any) -> None:
    """Atomically write JSON data to file.

    Args:
        path: Target file path.
        data: Data to serialize to JSON.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}.{uuid.uuid4().hex}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def save_json_file(data: Any, file_path: str, indent: int = 2) -> None:
    """Save data to JSON file.

    Args:
        data: Data to serialize.
        file_path: Output file path.
        indent: JSON indentation level. Default is 2.
    """
    parent_dir = os.path.dirname(file_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def read_json_file(file_path: str) -> Any:
    """Read JSON file and parse content.

    Args:
        file_path: Path to JSON file.

    Returns:
        Parsed JSON data.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """Recursively find files by extension in directory.

    Args:
        directory: Root directory to search.
        extensions: List of file extensions to match.

    Returns:
        List of absolute file paths matching the extensions.
    """
    if not os.path.isdir(directory):
        return []
    out = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in extensions):
                out.append(os.path.join(root, file))
    return out

def normalize_material_key(name: str) -> str:
    if not name:
        return ""
    s = name.strip()
    s = MAPPING_RELATION.get(s, s)
    return re.sub(r"[^A-Z0-9]+", "", s.upper())

def build_md_knowledge_map(expert_data_root: str) -> Dict[tuple, str]:
    md_files = read_files_by_extension(expert_data_root, extensions=[".md", ".markdown"])
    mapping = {}
    for path in md_files:
        base = os.path.splitext(os.path.basename(path))[0]
        key = normalize_material_key(base)
        if not key:
            continue
        parent = os.path.basename(os.path.dirname(path)).strip().lower()
        type_key = parent if parent in ("sam", "additive", "passivator") else None
        map_key = (type_key, key)
        if map_key in mapping and mapping[map_key] != path:
            print(f"[WARN] duplicate md key: {map_key}")
        mapping[map_key] = path
    print(f"[INFO] loaded {len(mapping)} md knowledge files from {osp.abspath(expert_data_root)}")
    return mapping

def extract_material_names_from_filename(base: str) -> List[str]:
    s = (base or "").strip()
    if not s:
        return []
    s = s.replace("→", "->").replace("➡", "->").replace("=>", "->")
    ACTION_WORDS = r"adding|removing|add|remove|replacing|replace|replaced|increasing|decreasing|increase|decrease|increased|decreased"
    def _clean_token(t: str) -> str:
        t = (t or "").strip()
        t = re.sub(rf'^(?:{ACTION_WORDS})\s+', "", t, flags=re.IGNORECASE).strip()
        t = re.sub(rf'\s+(?:{ACTION_WORDS})$', "", t, flags=re.IGNORECASE).strip()
        t = re.sub(r'\(.*?\)', "", t).strip()
        t = t.split(",")[0].strip()
        if " " in t:
            first = t.split()[0].strip()
            if re.search(r'\d', t) or re.search(r'(mg/ml|mM|mol|wt%|%)', t, flags=re.IGNORECASE):
                t = first
        return t.strip(" _-+")
    if "->" in s:
        parts = [p.strip() for p in s.split("->") if p.strip()]
        names = [_clean_token(p) for p in parts if _clean_token(p)]
        return names if names else [_clean_token(s)]
    if re.match(rf'^({ACTION_WORDS})\s+(.+)$', s, flags=re.IGNORECASE):
        tok = _clean_token(re.match(rf'^({ACTION_WORDS})\s+(.+)$', s, flags=re.IGNORECASE).group(2))
        return [tok] if tok else [_clean_token(s)]
    if re.match(rf'^(.*?)\s*_\s*({ACTION_WORDS})\b', s, flags=re.IGNORECASE):
        left = _clean_token(re.match(rf'^(.*?)\s*_\s*({ACTION_WORDS})\b', s, flags=re.IGNORECASE).group(1))
        return [left] if left else [_clean_token(s)]
    parts = re.split(r'\s*[-+]+_\s*', s)
    if len(parts) > 1:
        names = [_clean_token(p) for p in parts if _clean_token(p)]
        return names if names else [_clean_token(s)]
    if re.search(rf'^(.*?)[\s_+-]*({ACTION_WORDS})\b', s, flags=re.IGNORECASE):
        left = _clean_token(re.search(rf'^(.*?)[\s_+-]*({ACTION_WORDS})\b', s, flags=re.IGNORECASE).group(1))
        return [left] if left else [_clean_token(s)]
    return [_clean_token(s)]

def _pure_id(s: str) -> str:
    if s is None:
        return ""
    return str(s).split(",")[0].strip()

def build_background_from_names(names: List[str], material_type: Optional[str], md_map, md_text_cache) -> Dict[str, Any]:
    pieces = []
    used_files = []
    for name in names:
        key = normalize_material_key(name)
        candidate_keys = [(material_type, key)] if material_type else []
        candidate_keys.append((None, key))
        md_path = None
        for ck in candidate_keys:
            if ck in md_map:
                md_path = md_map[ck]
                break
        if not md_path:
            # print(f"[WARN] no md found for '{name}' (type={material_type})")
            continue
        if md_path not in md_text_cache:
            try:
                md_text_cache[md_path] = read_text_file(md_path)
            except Exception as e:
                print(f"[WARN] fail to read md '{md_path}': {e}")
                continue
        pieces.append(f"### {name}\n{md_text_cache[md_path]}")
        used_files.append(os.path.basename(md_path))
    return {
        "summary_text": "\n\n".join(pieces),
        "material_names": names,
        "md_files": used_files,
    }

# ===== Task building =====
def get_tasks_from_db(
    expert_data_root: str,
    save_path: str,
    num_thres: int = 100,
    db_config: Optional[Dict[str, Any]] = None
):
    if db_config is None:
        # Try to load from RECIPEQA_CONFIG first
        recipeqa_db = RECIPEQA_CONFIG.get("database", {})

        if not recipeqa_db:
            # Try to load from main config file
            try:
                from pathlib import Path
                import tomllib

                current_file = Path(__file__).resolve()
                # Try path 1: project root / config.toml
                project_root = current_file.parent.parent.parent
                config_path = project_root / "config.toml"

                # Try path 2: alternative structure
                if not config_path.exists():
                    project_root = current_file.parent.parent.parent.parent
                    config_path = project_root / "config.toml"

                if config_path.exists():
                    with config_path.open("rb") as f:
                        config = tomllib.load(f)
                    # First try recipeqa.database, then fallback to main database
                    recipeqa_db = config.get("recipeqa", {}).get("database", {})
                    if not recipeqa_db:
                        recipeqa_db = config.get("database", {})
            except Exception as e:
                print(f"[WARN] Failed to load config: {e}")
                pass

        # Use loaded config or default values
        db_config = recipeqa_db if recipeqa_db else {
            "host": "",
            "port": 13330,
            "user": "root",
            "password": "",
            "database": "",
            "charset": "utf8mb4"
        }

    md_map = build_md_knowledge_map(expert_data_root)
    md_text_cache = {}

    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT
                    id,
                    task_name,
                    json_filename,
                    meta_info,
                    sample_id_1,
                    sample_id_2,
                    control_device_fabrication,
                    target_device_fabrication
                FROM no_characterisation_match
                WHERE status = 0
            """)
            rows = cursor.fetchall()
    finally:
        conn.close()

    print(f"[INFO] Loaded {len(rows)} records with status=0 from database")

    grouped = defaultdict(list)
    for row in rows:
        record = {
            "id": row[0],
            "task_name": row[1],
            "json_filename": row[2],
            "meta_info": row[3],
            "sample_id_1": row[4],
            "sample_id_2": row[5],
            "control_device_fabrication": row[6],
            "target_device_fabrication": row[7] or "",
        }
        grouped[row[1]].append(record)

    total_task = []
    seen = set()

    for folder_name, records in grouped.items():
        folder_lower = folder_name.strip().lower()
        is_formula_sam = folder_lower.startswith("formula sam")
        is_formula_additive = folder_lower.startswith("formula additive")
        is_formula_passivator = folder_lower.startswith("formula passivator")
        mat_type = "sam" if is_formula_sam else "additive" if is_formula_additive else "passivator" if is_formula_passivator else None

        if mat_type is None:
            print(f"[SKIP] Skipping non-Formula category: {folder_name}")
            continue

        for rec in records:
            meta = {}
            try:
                if isinstance(rec["meta_info"], str):
                    meta = json.loads(rec["meta_info"])
                elif isinstance(rec["meta_info"], dict):
                    meta = rec["meta_info"]
            except:
                meta = {}

            sid1 = _pure_id(meta.get("Sample_ID_1") or rec["sample_id_1"])
            sid2 = _pure_id(meta.get("Sample_ID_2") or rec["sample_id_2"])
            base_name = rec["json_filename"]

            if mat_type in ("sam", "additive", "passivator"):
                material_names = extract_material_names_from_filename(base_name)
            else:
                material_names = [base_name]

            expert_data = build_background_from_names(material_names, mat_type, md_map, md_text_cache)

            dedup_key = (sid1, sid2, folder_name, base_name)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            total_task.append({
                "record_id": rec["id"],
                "meta_info": meta,
                "control_device_fabrication": rec["control_device_fabrication"],
                "target_device_fabrication": rec["target_device_fabrication"],
                "category_folder": folder_name,
                "match_file": f"{base_name}.json",
                "expert_data": expert_data,
                "primary_materials": material_names,
            })

    print(f"[INFO] Total tasks built: {len(total_task)}")
    save_json_file(total_task, save_path)
    return [t["record_id"] for t in total_task]

# ===== Inference =====
async def process_single_item(item: Dict[str, Any], save_root: str, success_ids: list) -> None:
    record_id = item.get("record_id")
    if not record_id:
        return

    sid1_raw = (item.get("meta_info", {}).get("Sample_ID_1", "") or "").split(",")[0].strip()
    sid2_raw = (item.get("meta_info", {}).get("Sample_ID_2", "") or "").split(",")[0].strip()
    fn = f"{safe_filename(sid1_raw) or 'X'}_{safe_filename(sid2_raw) or 'Y'}.json"
    save_path = osp.join(save_root, fn)
    base_payload = {
        "think_part": "",
        "answer_part": "",
        "control_device_fabrication": item.get("control_device_fabrication", ""),
        "target_device_fabrication": item.get("target_device_fabrication", ""),
        "meta_info": item.get("meta_info", {}),
    }

    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                reference_analysis = (item.get("expert_data") or {}).get("summary_text") \
                                     or json.dumps(item.get("expert_data", {}), ensure_ascii=False)
                primary_materials_list = item.get("primary_materials") or []
                primary_materials_str = ", ".join(primary_materials_list) if primary_materials_list else "None"

                sys_prompt = SYS_PROMPT.format(primary_materials=primary_materials_str)
                user_prompt = USER_PROMPT.format(
                    primary_materials=primary_materials_str,
                    reference_analysis=reference_analysis,
                    control_device_fabrication=item.get("control_device_fabrication", ""),
                    target_device_fabrication=item.get("target_device_fabrication", ""),
                )

                response = await client.chat.completions.create(
                    model=LLM_CONFIG["model"],
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=LLM_CONFIG["temperature"],
                    extra_body={"enable_thinking": True},
                    stream=True
                )

                reasoning_content, answer_content = "", ""
                async for chunk in response:
                    choices = getattr(chunk, "choices", None)
                    if not choices:
                        continue
                    delta = choices[0].delta
                    rc = getattr(delta, "reasoning_content", None)
                    cp = getattr(delta, "content", None)
                    if rc:
                        reasoning_content += rc
                    if cp:
                        answer_content += cp

                payload = {
                    **base_payload,
                    "think_part": reasoning_content.strip(),
                    "answer_part": answer_content.strip(),
                }
                atomic_write_json(save_path, payload)
                success_ids.append(record_id)
                return

            except Exception as e:
                if attempt >= MAX_RETRIES:
                    stub = {**base_payload, "error": repr(e)}
                    atomic_write_json(save_path, stub)
                    return
                await asyncio.sleep(RETRY_BASE_DELAY * attempt + random.uniform(0, 1))

async def request_llm(data: List[Dict[str, Any]], save_root: str) -> List[int]:
    print(f"[PATH] dist: {osp.abspath(save_root)}")
    os.makedirs(save_root, exist_ok=True)
    success_ids = []
    tasks = [process_single_item(item, save_root, success_ids) for item in data]
    await asyncio.gather(*tasks, return_exceptions=True)
    return success_ids

# ===== Batch DB Update =====
def batch_update_status(db_config: dict, record_ids: List[int], status: int):
    if not record_ids:
        return
    conn = mysql.connector.connect(**db_config)
    try:
        cursor = conn.cursor()
        for i in range(0, len(record_ids), 1000):
            batch = record_ids[i:i+1000]
            placeholders = ','.join(['%s'] * len(batch))
            cursor.execute(
                f"UPDATE no_characterisation_match SET status = %s WHERE id IN ({placeholders})",
                [status] + batch
            )
        conn.commit()
        print(f"[DB] Updated {len(record_ids)} records to status={status}")
    finally:
        conn.close()

# ===== Dataset =====
def get_dataset(data_root: str) -> List[Dict[str, Any]]:
    out = []
    files = read_files_by_extension(data_root, extensions=[".json"])
    for f in files:
        data = read_json_file(f)
        sys_prompt = "Based on the perovskite formulation and process description, mechanistically analyze the device's Voc, FF, Jsc, and PCE."
        user_prompt = "Control Device Fabrication: {control_device_fabrication}. Optimization Device Fabrication: {target_device_fabrication}."
        think_part = data.get('think_part', '')
        answer_part = data.get('answer_part', '')
        out.append({
            "instruction": sys_prompt,
            "input": user_prompt.format(
                control_device_fabrication=data.get("control_device_fabrication", ""),
                target_device_fabrication=data.get("target_device_fabrication", "")
            ),
            "output": f"<think>{think_part}</think><answer>{answer_part}</answer>"
        })
    return out

# ===== Rebuild mechanism =====
def rebuild_mechanism_from_db(output_root: str, db_config: dict, table_name: str = "expert_mechanisms"):
    os.makedirs(output_root, exist_ok=True)
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT category_2, material, content FROM `{table_name}`")
        rows = cursor.fetchall()
        valid_categories = {"sam", "additive", "passivator"}
        for row in rows:
            raw_category = row.get("category_2")
            material_key = row.get("material", "")
            content = row.get("content", "")
            if not material_key or not isinstance(material_key, str):
                continue
            if raw_category and isinstance(raw_category, str):
                cat_lower = raw_category.strip().lower()
                if cat_lower in valid_categories:
                    subdir = cat_lower.capitalize()
                    target_dir = os.path.join(output_root, subdir)
                else:
                    target_dir = output_root
            else:
                target_dir = output_root
            os.makedirs(target_dir, exist_ok=True)
            md_path = os.path.join(target_dir, f"{material_key}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(content)
        print(f"\n Rebuilt {len(rows)} markdown files into '{output_root}'")
    except Error as e:
        print(f"[ERROR] database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# ===== Main =====
def main():

    dist_save_root = osp.join(BASE_DIR, "..","..", "Generating", "data", "single")
    print(f"[PATH] dist: {osp.abspath(dist_save_root)}")
    dataset_path = osp.join(DATA_DIR,"dataset", "single_dataset.json")

    dist_files = read_files_by_extension(dist_save_root, extensions=[".json"])
    print(f"[INFO] dist files: {len(dist_files)}")

    dataset = get_dataset(dist_save_root)
    save_json_file(dataset, dataset_path)
    print(f"[INFO] dataset size: {len(dataset)} -> {osp.abspath(dataset_path)}")

if __name__ == "__main__":
    main()
