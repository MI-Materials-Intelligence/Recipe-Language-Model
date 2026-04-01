import os
import os.path as osp
import json
import random
import re
import uuid
from typing import Dict, Any, List
import asyncio
from openai import AsyncOpenAI
from typing import Tuple, Optional
import os
import mysql.connector
from mysql.connector import Error
from collections import defaultdict

# ===== Config Loader =====
def load_recipeqa_config():
    """Load RecipeQA configuration from app.config"""
    try:
        from seven_ai_layers_robotics.config import config

        # Build LLM config from app.config - use recipeqa_llm instead of learning
        llm_config = {
            "api_key": config.recipeqa_llm.dashscope_api_key if hasattr(config, 'recipeqa_llm') else "",
            "base_url": config.recipeqa_llm.base_url if hasattr(config, 'recipeqa_llm') else "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": config.recipeqa_llm.dashscope_model if hasattr(config, 'recipeqa_llm') else "qwen-plus",
            "temperature": config.recipeqa_llm.temperature if hasattr(config, 'recipeqa_llm') else 0.4,
        }

        # Debug print to verify API key is loaded
        # if llm_config.get("api_key"):
            # print(f"[INFO] RecipeQA LLM config loaded: api_key={llm_config['api_key'][:10]}...***")
        # else:
            # print("[WARN] RecipeQA LLM api_key is empty!")

        return llm_config
    except Exception as e:
        print(f"[WARN] Failed to load config: {e}, using default values")
        return {}

# ===== Config =====
# Current file location: RecipeQA/src/distill/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # RecipeQA
DATA_DIR = os.path.join(BASE_DIR, "data")  # RecipeQA/data

# Load LLM configuration from app.config
RECIPEQA_CONFIG = load_recipeqa_config()
LLM_CONFIG = {
    "api_key": RECIPEQA_CONFIG.get("api_key", ""),
    "base_url": RECIPEQA_CONFIG.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    "model": RECIPEQA_CONFIG.get("model", "qwen-plus"),
    "temperature": RECIPEQA_CONFIG.get("temperature", 0.4),
}

client = AsyncOpenAI(
    api_key=LLM_CONFIG["api_key"],
    base_url=LLM_CONFIG["base_url"]
)
MAX_CONCURRENT_REQUESTS = RECIPEQA_CONFIG.get("max_concurrent_requests", 5)
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
MAX_RETRIES = RECIPEQA_CONFIG.get("max_retries", 5)
RETRY_BASE_DELAY = RECIPEQA_CONFIG.get("retry_base_delay", 10)

MAPPING_RELATION = {
    "DMAcPA": "DMACPA",
    "PEACI": "PEACl",
    "PY3": "py3",
    "Py3": "py3",
    "PEACL": "PEACl",
}

SYS_PROMPT = """
You are a perovskite solar cell formulation optimization expert. FORMULATION ONLY.

Inputs in the user message:
- PRIMARY_MATERIALS_CANDIDATES: {primary_materials}  (hint only)
- Background_Knowledge (internal reasoning only)
- CONTROL_Device
- OPTIMIZED_Device (internal reference only; never mention)
- Question

Hard rules:
1) FORMULATION ONLY. You may change only composition variables (perovskite stoichiometry/molarity, additives/passivators/dopants, SAM/interlayers and their concentrations). Treat all processing as fixed (do not propose any process change).
2) OPTIMIZED_Device is for internal grounding only. Never mention it or imply you were given a reference/target/second device.
3) Background_Knowledge is internal only. Never mention "background / provided / expert analysis / given text" etc.
4) Do NOT use meta labels or headings such as "Step", "CONTROL metrics", "optimized metrics", "exact", "fuzzy", "range/bounds", "computed/calculated", "formula/equation". Start directly with paragraphs (no markdown titles).

Candidate-handling (must do first, but narrate naturally):
- Scan the CONTROL formulation and LOCATE each candidate: whether present, where used, and concentration if reported.
- Then judge its role in CONTROL (helping / limiting / neutral) using CONTROL performance + mechanism knowledge.
- Only then propose how to adjust it in the improved formulation. The final formulation you recommend must match the OPTIMIZED_Device composition (internally).

Mechanism constraints:
- Detailed mechanistic explanations must be primarily about the candidate materials that have support in Background_Knowledge.
- For other formulation differences not supported by Background_Knowledge: mention only briefly and qualitatively; do NOT invent eV energy levels, trap % numbers, or detailed functional-group binding unless explicitly stated in Background_Knowledge.

Numerical reporting (optimized values must be blurred; never reveal exact O):
- Baseline device: you MAY quote single-value metrics as provided (PCE/Voc/Jsc/FF).
- Improved device: report each metric only as an interval, using these internal rules with OPTIMIZED values O:
  * Voc interval: [max(O-0.02, 0), min(O+0.02, 1.16)]
  * Jsc interval: [max(O-0.20, 0), min(O+0.20, 26.6)]
  * FF interval:  [max(O-1.0, 0),  min(O+1.0, 86.0)]
  * PCE interval: compute internally from the interval endpoints (use the same multiplicative relation), but do NOT mention any formula or computation.
- If any needed metric is missing: say “not reported” and do not guess.

Depth requirements (make the answer more detailed):
- Explicitly connect formulation → (defects/recombination/transport/interfaces/ion migration/morphology) → (Voc/Jsc/FF/PCE).
- Explain at concrete “failure modes” in the baseline and how the proposed formulation changes mitigate them.
- Mention at trade-offs or side-effects and why the chosen adjustment is still preferable.
- State the final optimized formulation changes as an actionable list (material + concentration change), without using meta labels.

"""


USER_PROMPT = """
Background_Knowledge (internal reasoning only):
{reference_analysis}

CONTROL_Device:
{control_device_fabrication}

OPTIMIZED_Device (internal reference only; do NOT mention explicitly in your answer):
{target_device_fabrication}

Question:
Starting from the CONTROL device, analyze formulation limitations and propose an optimized formulation.
Focus your detailed mechanistic explanation on PRIMARY_MATERIALS and quantify performance improvements using:
- exact CONTROL metrics (if reported)
- fuzzy ranges for optimized metrics (do not output exact optimized numbers).
Do not propose any process changes.
"""




# ===== Utils =====
def safe_filename(name: str) -> str:
    name = (name or "").strip()
    return re.sub(r'[\\/:\*\?"<>\|]+', '_', name)

def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def atomic_write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}.{uuid.uuid4().hex}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def save_json_file(data: Any, file_path: str, indent: int = 2) -> None:
    parent_dir = os.path.dirname(file_path)
    if parent_dir:  # Create only when parent directory is not empty
        os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def read_json_file(file_path: str) -> Any:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
def rebuild_mechanism_from_db(
    output_root: str,
    db_config: dict,
    table_name: str = "expert_mechanisms"
):
    """
    Rebuild mechanism folder structure from database.

    Args:
        output_root: Output directory, e.g., "./mechanism"
        db_config: MySQL configuration
        table_name: Table name
    """
    print(f"[INFO] Starting rebuild_mechanism_from_db...")
    print(f"[INFO] DB config: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    print(f"[INFO] Table: {table_name}")
    print(f"[INFO] Output dir: {output_root}")
    
    # Create output directory
    os.makedirs(output_root, exist_ok=True)
    print(f"[INFO] Created output directory: {output_root}")

    try:
        print(f"[INFO] Connecting to database...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        print(f"[INFO] Database connection successful")

        print(f"[INFO] Executing query: SELECT category_2, material, content FROM `{table_name}`")
        cursor.execute(f"SELECT category_2, material, content FROM `{table_name}`")
        rows = cursor.fetchall()
        print(f"[INFO] Retrieved {len(rows)} records from database")

        valid_categories = {"sam", "additive", "passivator"}
        written_count = 0

        for row in rows:
            raw_category = row.get("category_2")
            material_key = row.get("material", "")
            content = row.get("content", "")

            if not material_key or not isinstance(material_key, str):
                print(f"[WARN] skip invalid material: '{material_key}' (type: {type(material_key)})")
                continue

            # Generate standardized filename (without .md)
            filename_base = material_key
            if not filename_base:
                print(f"[WARN] empty filename for key: {material_key}")
                continue

            # Determine target subdirectory
            if raw_category and isinstance(raw_category, str):
                cat_lower = raw_category.strip().lower()
                if cat_lower in valid_categories:
                    subdir = cat_lower.upper().capitalize()  # 'sam' → 'SAM'
                    target_dir = os.path.join(output_root, subdir)
                    print(f"[DEBUG] Category '{raw_category}' -> subdir '{subdir}'")
                else:
                    target_dir = output_root  # Other categories → root directory
                    print(f"[DEBUG] Category '{raw_category}' not in valid_categories, using root")
            else:
                target_dir = output_root  # category is NULL/empty → root directory

            os.makedirs(target_dir, exist_ok=True)
            md_path = os.path.join(target_dir, f"{filename_base}.md")

            # Write file
            try:
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(content)
                written_count += 1
                if written_count <= 10 or written_count % 100 == 0:  # Print first 10 and every 100th
                    print(f"[INFO] wrote {md_path}")
            except Exception as e:
                print(f"[ERROR] failed to write {md_path}: {e}")

        print(f"\n✅ Rebuilt {written_count} markdown files into '{output_root}'")
        print(f"[INFO] Total records processed: {len(rows)}")
        print(f"[INFO] Total files written: {written_count}")

    except Error as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print(f"[INFO] Database connection closed")
# ===== Main =====
def read_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    if not os.path.isdir(directory):
        return []
    out = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in extensions):
                out.append(os.path.join(root, file))
    return out

def _safe_get(d: dict, path: List[str], default: str = "") -> str:
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur if isinstance(cur, str) else (json.dumps(cur, ensure_ascii=False) if cur is not None else default)

def normalize_material_key(name: str) -> str:
    """
    Normalize material/variable name to a key for md file matching:
    - First use MAPPING_RELATION for alias correction (e.g., PEACI -> PEACl)
    - Then convert all to uppercase, keep only letters and numbers
    -> Filename matching automatically ignores case
    """
    if not name:
        return ""
    s = name.strip()
    s = MAPPING_RELATION.get(s, s)  # 先统一别名
    return re.sub(r"[^A-Z0-9]+", "", s.upper())



def build_md_knowledge_map(expert_data_root: str) -> Dict[Tuple[Optional[str], str], str]:
    """
    Scan all .md/.markdown files under expert_data_root and create:
        (type, normalized key) -> md file path

    Here "type" comes from md's parent folder name (lowercase):
        expert_data_root/
          SAM/
            2PACz.md         -> ('sam', '2PACZ')
            CB-PA.md         -> ('sam', 'CBPA')
          Additive/
            MACl.md          -> ('additive', 'MACL')
          Passivator/
            PSP.md           -> ('passivator', 'PSP')
          Other/root directory md
            Annealed Temperature PVK.md -> (None, 'ANNEALEDTEMPERATUREPVK')
    """
    md_files = read_files_by_extension(expert_data_root, extensions=[".md", ".markdown"])
    mapping: Dict[Tuple[Optional[str], str], str] = {}

    for path in md_files:
        base = os.path.splitext(os.path.basename(path))[0]
        key = normalize_material_key(base)
        if not key:
            continue

        parent = os.path.basename(os.path.dirname(path)).strip().lower()
        if parent in ("sam", "additive", "passivator"):
            type_key: Optional[str] = parent     # 'sam' / 'additive' / 'passivator'
        else:
            type_key = None                      # 其它目录或根目录

        map_key = (type_key, key)
        if map_key in mapping and mapping[map_key] != path:
            print(f"[WARN] duplicate md key: {map_key} -> {mapping[map_key]} , {path}")
        mapping[map_key] = path

    print(f"[INFO] loaded {len(mapping)} md knowledge files from {osp.abspath(expert_data_root)}")
    return mapping


def read_text_file(path: str) -> str:
    """
    Read md text content
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_material_names_from_filename(base: str) -> List[str]:
    """
    More robust material name parsing:
    - Supports: Adding PDADI / Removing PSP
    - Supports: Increasing PEABr / Decreasing PMACl
    - Supports: PEABr_ Decreasing / PMACl_ Increasing
    - Supports: A -> B / A → B / A->B
    - Supports: 2PACz -_ CB-PA / MACl+_PEABr
    - Supports: 2PACz_ Adding / 2PACz - Removing
    """
    s = (base or "").strip()
    if not s:
        return []

    # Unify arrows
    s = s.replace("→", "->").replace("➡", "->").replace("=>", "->")

    # ✅ Unify action words
    ACTION_WORDS = (
        r"adding|removing|add|remove|"
        r"replacing|replace|replaced|"
        r"increasing|decreasing|increase|decrease|"
        r"increased|decreased"
    )
    ACTION_RE = re.compile(rf"^(?:{ACTION_WORDS})\b", flags=re.IGNORECASE)
    ACTION_TAIL_RE = re.compile(rf"\b(?:{ACTION_WORDS})$", flags=re.IGNORECASE)

    def _clean_token(t: str) -> str:
        t = (t or "").strip()
        if not t:
            return ""

        # Remove prefix action words: Adding/Removing/Increasing/Decreasing...
        t = re.sub(rf'^(?:{ACTION_WORDS})\s+', "", t, flags=re.IGNORECASE).strip()

        # ✅ Remove suffix action words: PEABr Decreasing / PMACl Increasing
        t = re.sub(rf'\s+(?:{ACTION_WORDS})$', "", t, flags=re.IGNORECASE).strip()

        # Remove parentheses content (concentration/units often in parentheses)
        t = re.sub(r'\(.*?\)', "", t).strip()

        # Truncate content after comma (common "PDADI, xxx")
        t = t.split(",")[0].strip()

        # If still has units like "mg/mL", usually material name is in first token
        if " " in t:
            first = t.split()[0].strip()
            if re.search(r'\d', t) or re.search(r'(mg/ml|mM|mol|wt%|%)', t, flags=re.IGNORECASE):
                t = first

        # Clean boundary symbols
        t = t.strip(" _-+")
        return t

    # 1) Handle arrow replacement: A -> B (may have multiple segments A->B->C)
    if "->" in s:
        parts = [p.strip() for p in s.split("->") if p.strip()]
        names = []
        for p in parts:
            p = _clean_token(p)
            if p:
                names.append(p)
        return names if names else [_clean_token(s)]

    # 2) Handle prefix action words: Adding X / Removing Y / Increasing X / Decreasing Y
    m = re.match(rf'^({ACTION_WORDS})\s+(.+)$', s, flags=re.IGNORECASE)
    if m:
        tok = _clean_token(m.group(2))
        return [tok] if tok else [_clean_token(s)]

    # ✅ 2.5) Handle "PEABr_ Decreasing / PMACl_ Increasing"
    # Only split when action word is clearly after "_", to avoid misinterpreting complex names
    m = re.match(rf'^(.*?)\s*_\s*({ACTION_WORDS})\b', s, flags=re.IGNORECASE)
    if m:
        left = _clean_token(m.group(1))
        return [left] if left else [_clean_token(s)]

    # 3) Handle "2PACz -_ CB-PA", "MACl+_PEABr"
    parts = re.split(r'\s*[-+]+_\s*', s)
    if len(parts) > 1:
        names = [_clean_token(p) for p in parts if _clean_token(p)]
        return names if names else [_clean_token(s)]

    # 4) Handle "2PACz_ Adding / 2PACz - Removing / PEABr Increasing" (keyword at end)
    m = re.search(rf'^(.*?)[\s_+-]*({ACTION_WORDS})\b', s, flags=re.IGNORECASE)
    if m:
        left = _clean_token(m.group(1))
        return [left] if left else [_clean_token(s)]

    # 5) Default: treat entire string as material name
    return [_clean_token(s)]

# ===== Task building =====
def get_tasks(expert_data_root: str, single_var_match_result_root: str, save_path: str, num_thres: int = 100):
    """
    New task construction logic (according to updated matching relationship):

    expert_data_root:
        - Contains md files directly in root directory;
        - Or organized by category subfolders:
            expert_data_root/
              SAM/
              Additive/
              Passivator/
              (others optional)
        - SAM materials md under SAM/,
          Additives md under Additive/,
          Passivators md under Passivator/.

    single_var_match_result_root:
        - Contains many subfolders, e.g.:
            Annealed Temperature Passivator/
            Annealed Temperature PVK/
            Antisolvent Dropping Timing/
            Antisolvent Volume/
            Formula Additive 1/
            Formula Additive 2/
            Formula Passivator 1/
            Formula SAM 1/
            Formula SAM 2/
            Formula PVK/
            ...

    Matching relationship:
    1) Formula SAM* directories:
        - Split json filename (remove .json):
            '2PACz -_ CB-PA'   -> ['2PACz', 'CB-PA']
            '2PACz_ Adding'    -> ['2PACz']
        - Find corresponding md in expert_data_root/SAM/ for each material name (ignore case and symbols).
    2) Formula Additive* directories:
        - Similarly split filename, find md in expert_data_root/Additive/ for material names.
    3) Formula Passivator* directories:
        - Split filename, find md in expert_data_root/Passivator/ for material names.
    4) Other (non-Formula*) directories:
        - Use json filename (remove .json) directly as key, match in "general" md of expert_data_root
          (i.e., type is None, usually root directory or other unspecified folders).

    Filename matching ignores case: implemented via normalize_material_key.
    """

    def _pure_id(s: str) -> str:
        if s is None:
            return ""
        return str(s).split(",")[0].strip()

    # 1. Pre-build md mapping: (type_key, normalized_name) -> path
    md_map = build_md_knowledge_map(expert_data_root)
    md_text_cache: Dict[str, str] = {}

    def build_background_from_names(names: List[str], material_type: Optional[str]) -> Dict[str, Any]:
        """
        Given a list of material/variable names + type ('sam'/'additive'/'passivator'/None),
        concatenate corresponding md content to form summary_text.
        """
        pieces: List[str] = []
        used_files: List[str] = []

        for name in names:
            key = normalize_material_key(name)

            # First match by type precisely, e.g., ('sam', '2PACZ')
            candidate_keys: List[Tuple[Optional[str], str]] = []
            if material_type is not None:
                candidate_keys.append((material_type, key))
            # Then fallback to general md with type None (if any)
            candidate_keys.append((None, key))

            md_path: Optional[str] = None
            for ck in candidate_keys:
                if ck in md_map:
                    md_path = md_map[ck]
                    break

            if not md_path:
                # print(f"[WARN] no md found for '{name}' (type={material_type}, key='{key}')")
                continue

            if md_path not in md_text_cache:
                try:
                    md_text_cache[md_path] = read_text_file(md_path)
                except Exception as e:
                    print(f"[WARN] fail to read md '{md_path}': {e!r}")
                    continue

            pieces.append(f"### {name}\n{md_text_cache[md_path]}")
            used_files.append(osp.basename(md_path))

        summary_text = "\n\n".join(pieces)
        return {
            "summary_text": summary_text,
            "material_names": names,
            "md_files": used_files,
        }

    total_task: List[Dict[str, Any]] = []
    seen: set = set()

    if not osp.isdir(single_var_match_result_root):
        print(f"[WARN] single_var_match_result_root not a dir: {single_var_match_result_root}")
        save_json_file(total_task, save_path)
        return

    # 2. Traverse single_var_match_result_root's first-level subfolders
    for folder_name in os.listdir(single_var_match_result_root):
        folder_path = osp.join(single_var_match_result_root, folder_name)
        if not osp.isdir(folder_path):
            continue

        folder_lower = folder_name.strip().lower()

        # Determine if it's Formula SAM / Additive / Passivator categories
        is_formula_sam = folder_lower.startswith("formula sam")
        is_formula_additive = folder_lower.startswith("formula additive")
        is_formula_passivator = folder_lower.startswith("formula passivator")
        is_formula_folder = folder_lower.startswith("formula")

        # Corresponding md type key
        if is_formula_sam:
            mat_type: Optional[str] = "sam"
        elif is_formula_additive:
            mat_type = "additive"
        elif is_formula_passivator:
            mat_type = "passivator"
        else:
            mat_type = None   # Use general md for other cases

        json_files = read_files_by_extension(folder_path, extensions=[".json"])
        print(f"[INFO] folder '{folder_name}' | is_formula={is_formula_folder} | mat_type={mat_type} | json_files={len(json_files)}")

        # 3. Traverse each json file in this folder
        for jf in json_files:
            base_name = osp.splitext(osp.basename(jf))[0]

            # 3.1 Decide how to parse "names" based on whether it's Formula directory
            if is_formula_folder and mat_type in ("sam", "additive", "passivator"):
                # Formula SAM / Additive / Passivator -> split filename to get multiple material names
                material_names = extract_material_names_from_filename(base_name)
            else:
                # Non-above Formula categories (including Formula PVK and all non-Formula),
                # use filename directly as variable name
                material_names = [base_name]

            expert_data = build_background_from_names(material_names, material_type=mat_type)

            # 3.2 Read matching json content, extract sample pool
            data_obj = read_json_file(jf)
            pool: List[Dict[str, Any]] = []
            if isinstance(data_obj, dict):
                if isinstance(data_obj.get("data"), dict):
                    pool = list(data_obj["data"].values())
                elif isinstance(data_obj.get("data"), list):
                    pool = data_obj["data"]
                elif isinstance(data_obj.get("Data"), dict):
                    pool = list(data_obj["Data"].values())
                elif isinstance(data_obj.get("Data"), list):
                    pool = data_obj["Data"]
            elif isinstance(data_obj, list):
                pool = data_obj

            if not pool:
                print(f"[WARN] empty pool in {jf}")
                continue

            # 3.3 Sample at most num_thres entries per file
            k = min(len(pool), num_thres)
            sampled = random.sample(pool, k=k) if len(pool) > k else pool

            # 3.4 Construct final task item (process_item will use expert_data.summary_text as background knowledge)
            for m in sampled:
                meta = m.get("Meta Info") or m.get("Meta_Info") or {}
                inputs = m.get("Input") or {}

                sid1 = _pure_id(meta.get("Sample_ID_1", ""))
                sid2 = _pure_id(meta.get("Sample_ID_2", ""))

                # Use (sid1, sid2, folder_name, base_name) as deduplication key
                dedup_key = (sid1, sid2, folder_name, base_name)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)

                total_task.append({
                    "meta_info": meta,
                    "control_device_fabrication": inputs.get("control_device_fabrication", ""),
                    "target_device_fabrication": inputs.get("target_device_fabrication", ""),
                    "category_folder": folder_name,
                    "match_file": osp.basename(jf),
                    "expert_data": expert_data,  # 里有 summary_text，process_item 会用来喂给 API
                    "primary_materials": expert_data.get("material_names", []),
                })

    print(f"[INFO] total tasks built: {len(total_task)}")
    save_json_file(total_task, save_path)


# ===== Inference =====
async def process_item(item: Dict[str, Any], save_root: str, md_map: Dict = None) -> None:
    sid1_raw = (item.get("meta_info", {}).get("Sample_ID_1", "") or "").split(",")[0].strip()
    sid2_raw = (item.get("meta_info", {}).get("Sample_ID_2", "") or "").split(",")[0].strip()
    fn = f"{safe_filename(sid1_raw) or 'X'}_{safe_filename(sid2_raw) or 'Y'}.json"
    save_path = osp.join(save_root, fn)

    os.makedirs(save_root, exist_ok=True)
    
    # ✅ Skip if output file already exists
    if osp.exists(save_path):
        print(f"[SKIP] Output already exists: {osp.abspath(save_path)}")
        return

    # ✅ Load expert_data at runtime from md files (saves 90% JSON space)
    material_names = item.get("primary_materials", [])
    material_type = item.get("material_type")  # 'sam' / 'additive' / 'passivator' / None
    
    if md_map is not None and material_names:
        # Build reference_analysis from md files dynamically
        pieces = []
        for name in material_names:
            key = normalize_material_key(name)
            candidate_keys = [(material_type, key), (None, key)] if material_type else [(None, key)]
            md_path = None
            for ck in candidate_keys:
                if ck in md_map:
                    md_path = md_map[ck]
                    break
            if md_path:
                try:
                    pieces.append(f"### {name}\n{read_text_file(md_path)}")
                except Exception as e:
                    print(f"[WARN] fail to read md '{md_path}': {e}")
        reference_analysis = "\n\n".join(pieces) if pieces else "No background knowledge available."
    else:
        reference_analysis = "No background knowledge available."
    
    primary_materials_str = ", ".join(material_names) if material_names else "None"

    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                sys_prompt = SYS_PROMPT.format(
                    primary_materials=primary_materials_str
                )

                user_prompt = USER_PROMPT.format(
                    primary_materials=primary_materials_str,
                    reference_analysis=reference_analysis,
                    control_device_fabrication=item.get("control_device_fabrication", ""),
                    target_device_fabrication=item.get("target_device_fabrication", ""),
                )


                response = await client.chat.completions.create(
                    # model="qwen3-max-preview",
                    model=LLM_CONFIG.get("model", "qwen-plus"),
                    # model="qwen3-235b-a22b-instruct-2507",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=LLM_CONFIG.get("temperature", 0.4),
                    extra_body={"enable_thinking": True},
                    stream=True
                )

                reasoning_content, answer_content, chunks = "", "", 0
                async for chunk in response:
                    choices = getattr(chunk, "choices", None)
                    if not choices:
                        continue
                    chunks += 1
                    delta = choices[0].delta
                    rc = getattr(delta, "reasoning_content", None)
                    if rc:
                        reasoning_content += rc
                    cp = getattr(delta, "content", None)
                    if cp:
                        answer_content += cp

                think_part  = (reasoning_content or "").strip()
                answer_part = (answer_content or "").strip()

                payload = {
                    "think_part": think_part,
                    "answer_part": answer_part,
                    "control_device_fabrication": item.get("control_device_fabrication", ""),
                    "target_device_fabrication": item.get("target_device_fabrication", ""),
                    "meta_info": item.get("meta_info", {}),
                }
                atomic_write_json(save_path, payload)
                print(f"[SAVED] {osp.abspath(save_path)} | chunks={chunks} | think_len={len(think_part)} | answer_len={len(answer_part)}")
                return

            except Exception as e:
                print(f"[WARN] attempt {attempt} failed: {e!r}")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_BASE_DELAY * attempt + random.uniform(0, 1))
                else:
                    stub = {
                        "think_part": "",
                        "answer_part": "",
                        "error": repr(e),
                        "control_device_fabrication": item.get("control_device_fabrication", ""),
                        "target_device_fabrication": item.get("target_device_fabrication", ""),
                        "meta_info": item.get("meta_info", {}),
                    }
                    try:
                        atomic_write_json(save_path, stub)
                        print(f"[FALLBACK] {osp.abspath(save_path)}")
                    except Exception as e2:
                        print(f"[FATAL] cannot save stub: {e2!r} | path={osp.abspath(save_path)}")
                    return

async def request_llm(data: List[Dict[str, Any]], save_root: str, expert_data_root: str = None):
    print(f"[PATH] dist: {osp.abspath(save_root)}")
    os.makedirs(save_root, exist_ok=True)
    
    # ✅ Build md knowledge map for runtime retrieval
    md_map = {}
    if expert_data_root and osp.isdir(expert_data_root):
        md_map = build_md_knowledge_map(expert_data_root)
    
    tasks = [process_item(item, save_root, md_map) for item in data]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            print(f"[TASK-ERR] #{i}: {repr(r)}")

# ===== Dataset =====
def get_dataset(data_root: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    files = read_files_by_extension(data_root, extensions=[".json"])
    for f in files:
        data = read_json_file(f)
        sys_prompt = "Based on the perovskite formulation and process description, mechanistically analyze the device's Voc, FF, Jsc, and PCE."
        user_prompt = "Control Device Fabrication: {control_device_fabrication}."
        think_part = data.get('think_part', '')
        answer_part = data.get('answer_part', '')
        out.append({
            "instruction": sys_prompt,
            "input": user_prompt.format(
                control_device_fabrication=data.get("control_device_fabrication", "")
            ),
            "output": f"<think>{think_part}</think><answer>{answer_part}</answer>"
        })
    return out
def get_tasks_from_db(
    expert_data_root: str,
    save_path: str,
    num_thres: int = 1,
    db_config: Optional[Dict[str, Any]] = None
):
    def _pure_id(s: str) -> str:
        if s is None:
            return ""
        return str(s).split(",")[0].strip()

    # 1. Build expert knowledge map (unchanged)
    md_map = build_md_knowledge_map(expert_data_root)
    md_text_cache: Dict[str, str] = {}

    def build_background_from_names(names: List[str], material_type: Optional[str]) -> Dict[str, Any]:
        pieces: List[str] = []
        used_files: List[str] = []
        for name in names:
            key = normalize_material_key(name)
            candidate_keys = []
            if material_type is not None:
                candidate_keys.append((material_type, key))
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

    # 2. Load  data from database
    import pymysql  # Or your MySQL driver

    # Auto-get db_config from app.config
    if db_config is None:
        try:
            from seven_ai_layers_robotics.config import config
            db_config = {
                "host": config.learning_database.host,
                "port": config.learning_database.port,
                "user": config.learning_database.user,
                "password": config.learning_database.password,
                "database": config.learning_database.database,
                "charset": config.learning_database.charset,
            }
        except Exception as e:
            print(f"[WARN] Failed to load config from seven_ai_layers_robotics.config: {e}")
            pass

    # If still no config, use remote database default values
    if db_config is None:
        db_config = {
            "host": "",
            "port": 13330,
            "user": "root",
            "password": "",
            "database": "",
            "charset": "utf8mb4"
        }

    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    task_name,
                    json_filename,
                    meta_info,
                    sample_id_1,
                    sample_id_2,
                    control_device_fabrication,
                    target_device_fabrication
                FROM no_characterisation_match
            """)
            rows = cursor.fetchall()
    finally:
        conn.close()

    print(f"[INFO] Loaded {len(rows)} records from database")

    # 3. Group by task_name (simulate original "folder" logic)
    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for row in rows:
        record = {
            "task_name": row[0],
            "json_filename": row[1],
            "meta_info": row[2],
            "sample_id_1": row[3],
            "sample_id_2": row[4],
            "control_device_fabrication": row[5],
            "target_device_fabrication": row[6] or "",
        }
        grouped[row[0]].append(record)

    total_task: List[Dict[str, Any]] = []
    seen = set()

    # 4. Traverse each task_name (i.e., original folder_name)
    for folder_name, records in grouped.items():
        folder_lower = folder_name.strip().lower()

        is_formula_sam = folder_lower.startswith("formula sam")
        is_formula_additive = folder_lower.startswith("formula additive")
        is_formula_passivator = folder_lower.startswith("formula passivator")
        is_formula_folder = folder_lower.startswith("formula")

        if is_formula_sam:
            mat_type = "sam"
        elif is_formula_additive:
            mat_type = "additive"
        elif is_formula_passivator:
            mat_type = "passivator"
        else:
            mat_type = None
        print(f"[INFO] Processing category '{folder_name}' | type={mat_type} | count={len(records)}")
        if mat_type is None:
            print(f"[SKIP] Skipping non-Formula category: {folder_name}")
            continue


        # 5. Parse material names for each record
        for rec in records:
            # Parse meta_info
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

            # ✅ Key: Use json_filename instead of base_name
            base_name = rec["json_filename"]  # Already removed .json

            if is_formula_folder and mat_type in ("sam", "additive", "passivator"):
                material_names = extract_material_names_from_filename(base_name)
            else:
                material_names = [base_name]

            expert_data = build_background_from_names(material_names, material_type=mat_type)

            dedup_key = (sid1, sid2, folder_name, base_name)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            total_task.append({
                "meta_info": meta,
                "control_device_fabrication": rec["control_device_fabrication"],
                "target_device_fabrication": rec["target_device_fabrication"],
                "category_folder": folder_name,
                "match_file": f"{base_name}.json",
                "primary_materials": material_names,
                "material_type": mat_type,  # ✅ For runtime md retrieval
                # ❌ Removed: expert_data (saves ~90% space)
            })

        # Optional: Sample by category (original logic samples per JSON file, now can sample by category or globally)
        # Omitted here, as you may want to retain all

    print(f"[INFO] Total tasks built: {len(total_task)}")
    save_json_file(total_task, save_path)


# ===== Main =====
def main():
    # Load database configuration from app.config
    try:
        from seven_ai_layers_robotics.config import config
        DB_CONFIG = {
            'host': config.learning_database.host,
            'port': config.learning_database.port,
            'user': config.learning_database.user,
            'password': config.learning_database.password,
            'database': config.learning_database.database,
            'charset': 'utf8mb4'
        }
        print(f"[INFO] Loaded DB config: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    except Exception as e:
        print(f"[WARN] Failed to load config from seven_ai_layers_robotics.config: {e}")
        # Use default remote database config
        DB_CONFIG = {
            'host': '0',
            'port': 13330,
            'user': 'root',
            'password': '',
            'database': '',
            'charset': 'utf8mb4'
        }
        print(f"[INFO] Using default DB config: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

    MECHANISM_DIR = osp.join(DATA_DIR, "mechanism")  # RecipeQA/data/mechanism/
    rebuild_mechanism_from_db(MECHANISM_DIR, DB_CONFIG)

# Then continue with your original workflow
    # expert_data_root = osp.join(DATA_DIR, "mechanism")  # RecipeQA/data/mechanism/
    # single_var_match_result_root = osp.join(DATA_DIR, "single_var_match_v4")
    task_save_path = osp.join(DATA_DIR, "optimized_tasks_from_db.json")
    dist_save_root = osp.join(DATA_DIR, "optimized")
    dataset_path = osp.join(DATA_DIR,"dataset", "optimized_dataset.json")

    if not osp.exists(task_save_path):
        get_tasks_from_db(
            expert_data_root=MECHANISM_DIR,
            save_path=task_save_path,
            num_thres=1
        )

    tasks = read_json_file(task_save_path)
    print(f"[INFO] tasks: {len(tasks)} | dist: {osp.abspath(dist_save_root)}")
    # ✅ Pass expert_data_root for runtime md loading
    asyncio.run(request_llm(tasks, dist_save_root, MECHANISM_DIR))

    dist_files = read_files_by_extension(dist_save_root, extensions=[".json"])
    print(f"[INFO] dist files: {len(dist_files)}")

    dataset = get_dataset(dist_save_root)
    save_json_file(dataset, dataset_path)
    print(f"[INFO] dataset size: {len(dataset)} -> {osp.abspath(dataset_path)}")

if __name__ == "__main__":
    main()
