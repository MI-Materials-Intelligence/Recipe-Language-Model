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
        from app.config import config

        # Build LLM config from app.config
        llm_config = {
            "api_key": config.learning.api_key if hasattr(config, 'learning') else "",
            "base_url": config.learning.base_url if hasattr(config, 'learning') else "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": config.learning.model if hasattr(config, 'learning') else "qwen-plus",
            "temperature": config.learning.temperature if hasattr(config, 'learning') else 0.4,
        }

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
    if parent_dir:  # 只有当父目录非空时才创建
        os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def read_json_file(file_path: str) -> Any:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
def rebuild_mechanism_from_db(
    output_root: str,
    db_config: dict,
    table_name: str = "markdown_records"
):
    """
    从数据库重建 mechanism 文件夹结构。

    Args:
        output_root: 输出根目录，如 "./mechanism"
        db_config: MySQL 配置
        table_name: 表名
    """
    # 创建输出目录
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
                print(f"[WARN] skip invalid material: {material_key}")
                continue

            # 生成标准化文件名（不含 .md）
            filename_base = material_key
            if not filename_base:
                print(f"[WARN] empty filename for key: {material_key}")
                continue

            # 确定目标子目录
            if raw_category and isinstance(raw_category, str):
                cat_lower = raw_category.strip().lower()
                if cat_lower in valid_categories:
                    subdir = cat_lower.upper().capitalize()  # 'sam' → 'SAM'
                    target_dir = os.path.join(output_root, subdir)
                else:
                    target_dir = output_root  # 其他类别 → 根目录
            else:
                target_dir = output_root  # category 为 NULL/空 → 根目录

            os.makedirs(target_dir, exist_ok=True)
            md_path = os.path.join(target_dir, f"{filename_base}.md")

            # 写入文件
            try:
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[INFO] wrote {md_path}")
            except Exception as e:
                print(f"[ERROR] failed to write {md_path}: {e}")

        print(f"\n✅ Rebuilt {len(rows)} markdown files into '{output_root}'")

    except Error as e:
        print(f"[ERROR] database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
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
    将材料 / 变量名标准化成一个 key，用于 md 文件匹配：
    - 先用 MAPPING_RELATION 做一次别名修正（如 PEACI -> PEACl）
    - 再全部转大写，只保留字母和数字
    -> 文件名匹配自动忽略大小写
    """
    if not name:
        return ""
    s = name.strip()
    s = MAPPING_RELATION.get(s, s)  # 先统一别名
    return re.sub(r"[^A-Z0-9]+", "", s.upper())



def build_md_knowledge_map(expert_data_root: str) -> Dict[Tuple[Optional[str], str], str]:
    """
    扫描 expert_data_root 下所有 .md/.markdown 文件，建立：
        (类型, 标准化 key) -> md 文件路径

    这里的“类型”来自 md 所在父文件夹名（小写）：
        expert_data_root/
          SAM/
            2PACz.md         -> ('sam', '2PACZ')
            CB-PA.md         -> ('sam', 'CBPA')
          Additive/
            MACl.md          -> ('additive', 'MACL')
          Passivator/
            PSP.md           -> ('passivator', 'PSP')
          其它/根目录 md
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
    读 md 文本内容
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_material_names_from_filename(base: str) -> List[str]:
    """
    更鲁棒的材料名解析：
    - 支持：Adding PDADI / Removing PSP
    - 支持：Increasing PEABr / Decreasing PMACl
    - 支持：PEABr_ Decreasing / PMACl_ Increasing
    - 支持：A -> B / A → B / A->B
    - 支持：2PACz -_ CB-PA / MACl+_PEABr
    - 支持：2PACz_ Adding / 2PACz - Removing
    """
    s = (base or "").strip()
    if not s:
        return []

    # 统一箭头
    s = s.replace("→", "->").replace("➡", "->").replace("=>", "->")

    # ✅ 动作词统一管理（新增 Increasing/Decreasing）
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

        # 去掉前缀动作词：Adding/Removing/Increasing/Decreasing...
        t = re.sub(rf'^(?:{ACTION_WORDS})\s+', "", t, flags=re.IGNORECASE).strip()

        # ✅ 去掉后缀动作词：PEABr Decreasing / PMACl Increasing
        t = re.sub(rf'\s+(?:{ACTION_WORDS})$', "", t, flags=re.IGNORECASE).strip()

        # 去掉括号内容（浓度/单位常在括号里）
        t = re.sub(r'\(.*?\)', "", t).strip()

        # 截断逗号后内容（常见“PDADI, xxx”）
        t = t.split(",")[0].strip()

        # 如果还带了“mg/mL”这类单位，通常材料名在第一个token
        if " " in t:
            first = t.split()[0].strip()
            if re.search(r'\d', t) or re.search(r'(mg/ml|mM|mol|wt%|%)', t, flags=re.IGNORECASE):
                t = first

        # 清理边界符号
        t = t.strip(" _-+")
        return t

    # 1) 处理箭头替换：A -> B （可能出现多段 A->B->C）
    if "->" in s:
        parts = [p.strip() for p in s.split("->") if p.strip()]
        names = []
        for p in parts:
            p = _clean_token(p)
            if p:
                names.append(p)
        return names if names else [_clean_token(s)]

    # 2) 处理前缀动作词：Adding X / Removing Y / Increasing X / Decreasing Y
    m = re.match(rf'^({ACTION_WORDS})\s+(.+)$', s, flags=re.IGNORECASE)
    if m:
        tok = _clean_token(m.group(2))
        return [tok] if tok else [_clean_token(s)]

    # ✅ 2.5) 处理 “PEABr_ Decreasing / PMACl_ Increasing”
    # 只在 "_" 后面明显是动作词时才切分，避免误伤复杂命名
    m = re.match(rf'^(.*?)\s*_\s*({ACTION_WORDS})\b', s, flags=re.IGNORECASE)
    if m:
        left = _clean_token(m.group(1))
        return [left] if left else [_clean_token(s)]

    # 3) 处理 “2PACz -_ CB-PA”, “MACl+_PEABr”
    parts = re.split(r'\s*[-+]+_\s*', s)
    if len(parts) > 1:
        names = [_clean_token(p) for p in parts if _clean_token(p)]
        return names if names else [_clean_token(s)]

    # 4) 处理 “2PACz_ Adding / 2PACz - Removing / PEABr Increasing”（关键词在后）
    m = re.search(rf'^(.*?)[\s_+-]*({ACTION_WORDS})\b', s, flags=re.IGNORECASE)
    if m:
        left = _clean_token(m.group(1))
        return [left] if left else [_clean_token(s)]

    # 5) 默认：整串当材料名
    return [_clean_token(s)]



# ===== Task building =====
def get_tasks(expert_data_root: str, single_var_match_result_root: str, save_path: str, num_thres: int = 100):
    """
    新版 task 构造逻辑（按你更新后的匹配关系）：

    expert_data_root：
        - 下面有若干 md 文件，可以直接在根目录；
        - 也可以按类别分子文件夹：
            expert_data_root/
              SAM/
              Additive/
              Passivator/
              (其它可有可无)
        - SAM 子目录下放 SAM 材料的 md，
          Additive 子目录下放添加剂 md，
          Passivator 子目录下放钝化剂 md。

    single_var_match_result_root:
        - 下面有很多子文件夹，例如：
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

    匹配关系：
    1）Formula SAM* 目录：
        - 对 json 文件名（去 .json）做拆分：
            '2PACz -_ CB-PA'   -> ['2PACz', 'CB-PA']
            '2PACz_ Adding'    -> ['2PACz']
        - 每个材料名去 expert_data_root/SAM/ 里找对应 md（忽略大小写和符号）。
    2）Formula Additive* 目录：
        - 同样拆文件名，材料名去 expert_data_root/Additive/ 里找 md。
    3）Formula Passivator* 目录：
        - 拆文件名，材料名去 expert_data_root/Passivator/ 里找 md。
    4）其它（非 Formula*）目录：
        - 直接用 json 文件名（去 .json）作为 key，在 expert_data_root 的“通用” md 中匹配
          （即类型为 None 的那一类，通常是根目录或其它未特别指定的文件夹）。

    文件名匹配忽略大小写：通过 normalize_material_key 实现。
    """

    def _pure_id(s: str) -> str:
        if s is None:
            return ""
        return str(s).split(",")[0].strip()

    # 1. 预先构建 md 映射： (type_key, normalized_name) -> path
    md_map = build_md_knowledge_map(expert_data_root)
    md_text_cache: Dict[str, str] = {}

    def build_background_from_names(names: List[str], material_type: Optional[str]) -> Dict[str, Any]:
        """
        给定一组材料 / 变量名 + 类型（'sam'/'additive'/'passivator'/None），
        拼出对应 md 内容，组成 summary_text。
        """
        pieces: List[str] = []
        used_files: List[str] = []

        for name in names:
            key = normalize_material_key(name)

            # 先按类型精确匹配，比如 ('sam', '2PACZ')
            candidate_keys: List[Tuple[Optional[str], str]] = []
            if material_type is not None:
                candidate_keys.append((material_type, key))
            # 再退回到类型为 None 的通用 md（如果有）
            candidate_keys.append((None, key))

            md_path: Optional[str] = None
            for ck in candidate_keys:
                if ck in md_map:
                    md_path = md_map[ck]
                    break

            if not md_path:
                print(f"[WARN] no md found for '{name}' (type={material_type}, key='{key}')")
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

    # 2. 遍历 single_var_match_result_root 下的一级子文件夹
    for folder_name in os.listdir(single_var_match_result_root):
        folder_path = osp.join(single_var_match_result_root, folder_name)
        if not osp.isdir(folder_path):
            continue

        folder_lower = folder_name.strip().lower()

        # 判断是否是 Formula SAM / Additive / Passivator 三类
        is_formula_sam = folder_lower.startswith("formula sam")
        is_formula_additive = folder_lower.startswith("formula additive")
        is_formula_passivator = folder_lower.startswith("formula passivator")
        is_formula_folder = folder_lower.startswith("formula")

        # 对应 md 类型 key
        if is_formula_sam:
            mat_type: Optional[str] = "sam"
        elif is_formula_additive:
            mat_type = "additive"
        elif is_formula_passivator:
            mat_type = "passivator"
        else:
            mat_type = None   # 其它情况用通用 md

        json_files = read_files_by_extension(folder_path, extensions=[".json"])
        print(f"[INFO] folder '{folder_name}' | is_formula={is_formula_folder} | mat_type={mat_type} | json_files={len(json_files)}")

        # 3. 遍历该文件夹下的每个 json 文件
        for jf in json_files:
            base_name = osp.splitext(osp.basename(jf))[0]

            # 3.1 根据是否 Formula 目录，决定如何解析“名字”
            if is_formula_folder and mat_type in ("sam", "additive", "passivator"):
                # Formula SAM / Additive / Passivator -> 拆文件名得到多个材料名
                material_names = extract_material_names_from_filename(base_name)
            else:
                # 非上述 Formula 类（包括 Formula PVK 和所有非 Formula），
                # 直接用文件名作为一个变量名
                material_names = [base_name]

            expert_data = build_background_from_names(material_names, material_type=mat_type)

            # 3.2 读取匹配 json 内容，取出样本池
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

            # 3.3 每个文件最多采样 num_thres 条
            k = min(len(pool), num_thres)
            sampled = random.sample(pool, k=k) if len(pool) > k else pool

            # 3.4 构造最终的 task item（process_item 会用 expert_data.summary_text 当背景知识）
            for m in sampled:
                meta = m.get("Meta Info") or m.get("Meta_Info") or {}
                inputs = m.get("Input") or {}

                sid1 = _pure_id(meta.get("Sample_ID_1", ""))
                sid2 = _pure_id(meta.get("Sample_ID_2", ""))

                # 用 (sid1, sid2, folder_name, base_name) 做去重 key
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
async def process_item(item: Dict[str, Any], save_root: str) -> None:
    sid1_raw = (item.get("meta_info", {}).get("Sample_ID_1", "") or "").split(",")[0].strip()
    sid2_raw = (item.get("meta_info", {}).get("Sample_ID_2", "") or "").split(",")[0].strip()
    fn = f"{safe_filename(sid1_raw) or 'X'}_{safe_filename(sid2_raw) or 'Y'}.json"
    save_path = osp.join(save_root, fn)

    os.makedirs(save_root, exist_ok=True)

    async with semaphore:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                reference_analysis = (item.get("expert_data") or {}).get("summary_text") \
                                     or json.dumps(item.get("expert_data", {}), ensure_ascii=False)
                primary_materials_list = item.get("primary_materials") or (item.get("expert_data") or {}).get("material_names") or []
                primary_materials_str = ", ".join(primary_materials_list) if primary_materials_list else "None"

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

async def request_llm(data: List[Dict[str, Any]], save_root: str):
    print(f"[PATH] dist: {osp.abspath(save_root)}")
    os.makedirs(save_root, exist_ok=True)
    tasks = [process_item(item, save_root) for item in data]
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
    num_thres: int = 100,
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
                print(f"[WARN] no md found for '{name}' (type={material_type})")
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

    # 2. Load match_pair data from database
    import pymysql  # Or your MySQL driver

    # Auto-get db_config from app.config
    if db_config is None:
        try:
            from app.config import config
            db_config = {
                "host": config.learning_database.host,
                "port": config.learning_database.port,
                "user": config.learning_database.user,
                "password": config.learning_database.password,
                "database": config.learning_database.database,
                "charset": config.learning_database.charset,
            }
        except:
            pass

    # If still no config, use default values
    if db_config is None:
        db_config = {
            "host": "   ",
            "port": 3306,
            "user": "",
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
                FROM match_pair
            """)
            rows = cursor.fetchall()
    finally:
        conn.close()

    print(f"[INFO] Loaded {len(rows)} records from database")

    # 3. 按 task_name 分组（模拟原“文件夹”逻辑）
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

    # 4. 遍历每个 task_name（即原 folder_name）
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


        # 5. 对每条记录解析材料名
        for rec in records:
            # 解析 meta_info
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

            # ✅ 关键：用 json_filename 替代 base_name
            base_name = rec["json_filename"]  # 已去 .json

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
                "match_file": f"{base_name}.json",  # 模拟原文件名
                "expert_data": expert_data,
                "primary_materials": material_names,
            })

        # 可选：按类别采样（原逻辑是每个 JSON 文件采样，现在可按类别或全局采样）
        # 此处省略，因你可能希望保留全部

    print(f"[INFO] Total tasks built: {len(total_task)}")
    save_json_file(total_task, save_path)


# ===== Main =====
def main():
    # Load database configuration from app.config
    try:
        from app.config import config
        DB_CONFIG = {
            'host': config.learning_database.host,
            'port': config.learning_database.port,
            'user': config.learning_database.user,
            'password': config.learning_database.password,
            'database': config.learning_database.database,
            'charset': 'utf8mb4'
        }
    except:
        DB_CONFIG = {
            'host': '',
            'port': 3306,
            'user': '',
            'password': '',
            'database': '',
            'charset': 'utf8mb4'
        }

    MECHANISM_DIR = osp.join(DATA_DIR, "mechanism")  # RecipeQA/data/mechanism/
    rebuild_mechanism_from_db(MECHANISM_DIR, DB_CONFIG)

# 然后继续使用你原有的流程
    # expert_data_root = osp.join(DATA_DIR, "mechanism")  # RecipeQA/data/mechanism/
    # single_var_match_result_root = osp.join(DATA_DIR, "single_var_match_v4")
    task_save_path = osp.join(DATA_DIR, "optimized_tasks_from_db.json")
    dist_save_root = osp.join(DATA_DIR, "optimized")
    dataset_path = osp.join(DATA_DIR,"dataset", "optimized_dataset.json")

    if not osp.exists(task_save_path):
        get_tasks_from_db(
            expert_data_root=MECHANISM_DIR,
            save_path=task_save_path,
            num_thres=100
        )

    tasks = read_json_file(task_save_path)
    print(f"[INFO] tasks: {len(tasks)} | dist: {osp.abspath(dist_save_root)}")
    asyncio.run(request_llm(tasks, dist_save_root))

    dist_files = read_files_by_extension(dist_save_root, extensions=[".json"])
    print(f"[INFO] dist files: {len(dist_files)}")

    dataset = get_dataset(dist_save_root)
    save_json_file(dataset, dataset_path)
    print(f"[INFO] dataset size: {len(dataset)} -> {osp.abspath(dataset_path)}")

if __name__ == "__main__":
    main()
