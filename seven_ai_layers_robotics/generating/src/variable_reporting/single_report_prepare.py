#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
perovskite_analyzer.py
Perovskite Mechanism Analyzer - Single-file encapsulated module

Supports external invocation:
    1. Import method: from perovskite_analyzer import PerovskiteAnalyzer
    2. Command-line method: python perovskite_analyzer.py --config config.json

Author: Your Name
Date: 2026
"""

import os
import os.path as osp
import json
import random
import re
import uuid
import asyncio
import argparse
from typing import Dict, Any, List, Optional, Union
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from openai import AsyncOpenAI
import pymysql
import mysql.connector
from mysql.connector import Error

# Import configuration loader
import sys
from pathlib import Path as PathLib
script_dir = PathLib(__file__).parent
# Add generating/src to sys.path to use config_loader under Generating
generating_src = script_dir.parent  # Variable_Reporting -> generating/src
if str(generating_src) not in sys.path:
    sys.path.insert(0, str(generating_src))

# Import configuration from app.config
from seven_ai_layers_robotics.config import config


# ============================================================================
# 📦 Configuration Class (supports dict/JSON/default values)
# ============================================================================

@dataclass
class DBConfig:
    host: str = None  # Loaded from config file
    port: int = None
    user: str = None
    password: str = None
    database: str = None
    charset: str = "utf8mb4"

    def __post_init__(self):
        """Load default values from app.config after initialization"""
        if self.host is None:
            cfg = {
                'host': config.generating_database.host,
                'port': config.generating_database.port,
                'user': config.generating_database.user,
                'password': config.generating_database.password,
                'database': config.generating_database.database,
                'charset': config.generating_database.charset,
            }
            object.__setattr__(self, 'host', cfg.get('host', ''))
            object.__setattr__(self, 'port', cfg.get('port', 3306))
            object.__setattr__(self, 'user', cfg.get('user', 'root'))
            object.__setattr__(self, 'password', cfg.get('password', ''))
            object.__setattr__(self, 'database', cfg.get('database', ''))

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DBConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class LLMConfig:
    api_key: str = None  # Loaded from config file
    base_url: str = None
    model: str = "qwen3-max-preview"
    temperature: float = 0.4
    max_concurrent: int = 5
    max_retries: int = 5
    retry_base_delay: int = 10

    def __post_init__(self):
        """Load default values from app.config after initialization"""
        if self.api_key is None or self.base_url is None:
            cfg = {
                'api_key': config.generating_llm.dashscope_api_key,
                'base_url': config.generating_llm.base_url,
                'model': config.generating_llm.dashscope_model,
            }
            if self.api_key is None:
                object.__setattr__(self, 'api_key', cfg.get('api_key', ''))
            if self.base_url is None:
                object.__setattr__(self, 'base_url', cfg.get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1  '))

    def to_client_kwargs(self) -> Dict[str, Any]:
        return {"api_key": self.api_key, "base_url": self.base_url.rstrip("/") + "/"}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PathConfig:
    expert_data_root: str = "data\\mechanism"
    task_save_path: str = "data\\tasks_from_db.json"
    dist_save_root: str = "data\\single"
    dataset_path: str = "data\\single_var_dataset.json"

    def __post_init__(self):
        """Convert relative paths to absolute paths relative to Generating directory after initialization"""
        # Get Generating directory (two levels up from this file: Variable_Reporting -> src -> Generating)
        generating_dir = PathLib(__file__).resolve().parents[2]

        # Convert relative paths to absolute paths
        object.__setattr__(self, 'expert_data_root', str(generating_dir / self.expert_data_root))
        object.__setattr__(self, 'task_save_path', str(generating_dir / self.task_save_path))
        object.__setattr__(self, 'dist_save_root', str(generating_dir / self.dist_save_root))
        object.__setattr__(self, 'dataset_path', str(generating_dir / self.dataset_path))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PathConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AnalyzerConfig:
    db: DBConfig = field(default_factory=DBConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    material_mapping: Dict[str, str] = field(default_factory=lambda: {
        "DMAcPA": "DMACPA", "PEACI": "PEACl", "PY3": "py3",
        "Py3": "py3", "PEACL": "PEACl",
    })

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalyzerConfig":
        return cls(
            db=DBConfig.from_dict(data.get("db", {})),
            llm=LLMConfig.from_dict(data.get("llm", {})),
            paths=PathConfig.from_dict(data.get("paths", {})),
            material_mapping=data.get("material_mapping", cls().material_mapping),
        )

    @classmethod
    def from_json(cls, json_path: str) -> "AnalyzerConfig":
        with open(json_path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


# ============================================================================
# 🛠️ Utility Functions (for internal use)
# ============================================================================

def _safe_filename(name: str) -> str:
    name = (name or "").strip()
    return re.sub(r'[\\/:\*\?"<>\|]+', '_', name)

def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _atomic_write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp.{os.getpid()}.{uuid.uuid4().hex}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def _save_json_file(data: Any, file_path: str, indent: int = 2) -> None:
    parent_dir = os.path.dirname(file_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def _read_json_file(file_path: str) -> Any:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _read_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    if not os.path.isdir(directory):
        return []
    out = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in extensions):
                out.append(os.path.join(root, file))
    return out

def _normalize_material_key(name: str, mapping: Dict[str, str]) -> str:
    if not name:
        return ""
    s = name.strip()
    s = mapping.get(s, s)
    return re.sub(r"[^A-Z0-9]+", "", s.upper())

def _extract_material_names_from_filename(base: str, mapping: Dict[str, str]) -> List[str]:
    """Extract material names from filename (simplified version, keeping core logic)"""
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
    parts = re.split(r'\s*[-+]+_\s*', s)
    if len(parts) > 1:
        names = [_clean_token(p) for p in parts if _clean_token(p)]
        return names if names else [_clean_token(s)]
    return [_clean_token(s)]

def _pure_id(s: str) -> str:
    if s is None:
        return ""
    return str(s).split(",")[0].strip()


# ============================================================================
# 🧠 Core Analyzer Class (external invocation entry point)
# ============================================================================

class PerovskiteAnalyzer:
    """
    Perovskite Mechanism Analyzer - Main entry class

    Usage examples:
        # Method 1: Use default configuration
        analyzer = PerovskiteAnalyzer()
        result = analyzer.run()

        # Method 2: Custom configuration
        config = AnalyzerConfig.from_json("config.json")
        analyzer = PerovskiteAnalyzer(config)
        result = analyzer.run()

        # Method 3: Step-by-step invocation
        tasks = analyzer.fetch_tasks()
        success_ids = asyncio.run(analyzer.inference(tasks))
        analyzer.update_status(success_ids)
    """

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

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        # Use default configuration or passed configuration
        self.config = config or AnalyzerConfig()

        # If configuration has no values, load defaults from app.config
        if self.config.db.host is None:
            cfg = {
                'host': config.generating_database.host,
                'port': config.generating_database.port,
                'user': config.generating_database.user,
                'password': config.generating_database.password,
                'database': config.generating_database.database,
                'charset': config.generating_database.charset,
            }
            object.__setattr__(self.config.db, 'host', cfg.get('host', '0'))
            object.__setattr__(self.config.db, 'port', cfg.get('port', ))
            object.__setattr__(self.config.db, 'user', cfg.get('user', 'root'))
            object.__setattr__(self.config.db, 'password', cfg.get('password', ''))
            object.__setattr__(self.config.db, 'database', cfg.get('database', ''))

        if self.config.llm.api_key is None:
            cfg = {
                'api_key': config.generating_llm.dashscope_api_key,
                'base_url': config.generating_llm.base_url,
                'model': config.generating_llm.dashscope_model,
            }
            object.__setattr__(self.config.llm, 'api_key', cfg.get('api_key', ''))
            object.__setattr__(self.config.llm, 'base_url', cfg.get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1  '))
            object.__setattr__(self.config.llm, 'model', cfg.get('model', 'qwen-plus'))

        self._client = AsyncOpenAI(**self.config.llm.to_client_kwargs())
        self._semaphore = asyncio.Semaphore(self.config.llm.max_concurrent)
        self._md_text_cache: Dict[str, str] = {}
        self._md_map: Dict[tuple, str] = {}
        self._init_knowledge_map()
        print(f"[INFO] Database config: {self.config.db.host}:{self.config.db.port}/{self.config.db.database}")

    def _init_knowledge_map(self):
        """Initialize knowledge base mapping"""
        md_files = _read_files_by_extension(self.config.paths.expert_data_root, extensions=[".md", ".markdown"])
        for path in md_files:
            base = os.path.splitext(os.path.basename(path))[0]
            key = _normalize_material_key(base, self.config.material_mapping)
            if not key:
                continue
            parent = os.path.basename(os.path.dirname(path)).strip().lower()
            type_key = parent if parent in ("sam", "additive", "passivator") else None
            self._md_map[(type_key, key)] = path
        print(f"[INFO] loaded {len(self._md_map)} md knowledge files")

    def _build_background(self, names: List[str], material_type: Optional[str]) -> Dict[str, Any]:
        """Build background knowledge"""
        pieces, used_files = [], []
        for name in names:
            key = _normalize_material_key(name, self.config.material_mapping)
            candidate_keys = [(material_type, key)] if material_type else []
            candidate_keys.append((None, key))
            md_path = next((self._md_map[ck] for ck in candidate_keys if ck in self._md_map), None)
            if not md_path:
                print(f"[WARN] no md found for '{name}' (type={material_type})")
                continue
            if md_path not in self._md_text_cache:
                try:
                    self._md_text_cache[md_path] = _read_text_file(md_path)
                except Exception as e:
                    print(f"[WARN] fail to read md '{md_path}': {e}")
                    continue
            pieces.append(f"### {name}\n{self._md_text_cache[md_path]}")
            used_files.append(os.path.basename(md_path))
        return {
            "summary_text": "\n\n".join(pieces),
            "material_names": names,
            "md_files": used_files,
        }

    def fetch_tasks(self, num_thres: int = 100) -> List[Dict[str, Any]]:
        """Fetch pending tasks from database"""
        conn = pymysql.connect(**self.config.db.to_dict())
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, task_name, json_filename, meta_info, sample_id_1, sample_id_2,
                           control_device_fabrication, target_device_fabrication
                    FROM match_pair WHERE status = 0
                """)
                rows = cursor.fetchall()
        finally:
            conn.close()

        grouped = defaultdict(list)
        for row in rows:
            grouped[row[1]].append({
                "id": row[0], "task_name": row[1], "json_filename": row[2],
                "meta_info": row[3], "sample_id_1": row[4], "sample_id_2": row[5],
                "control_device_fabrication": row[6], "target_device_fabrication": row[7] or "",
            })

        tasks, seen = [], set()
        for folder_name, records in grouped.items():
            folder_lower = folder_name.strip().lower()
            mat_type = next((
                t for prefix, t in [("formula sam", "sam"), ("formula additive", "additive"), ("formula passivator", "passivator")]
                if folder_lower.startswith(prefix)
            ), None)
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
                    pass

                sid1 = _pure_id(meta.get("Sample_ID_1") or rec["sample_id_1"])
                sid2 = _pure_id(meta.get("Sample_ID_2") or rec["sample_id_2"])
                base_name = rec["json_filename"]
                material_names = _extract_material_names_from_filename(base_name, self.config.material_mapping) if mat_type in ("sam", "additive", "passivator") else [base_name]
                expert_data = self._build_background(material_names, mat_type)
                dedup_key = (sid1, sid2, folder_name, base_name)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)

                tasks.append({
                    "record_id": rec["id"], "meta_info": meta,
                    "control_device_fabrication": rec["control_device_fabrication"],
                    "target_device_fabrication": rec["target_device_fabrication"],
                    "category_folder": folder_name, "match_file": f"{base_name}.json",
                    "expert_data": expert_data, "primary_materials": material_names,
                })

        print(f"[INFO] Total tasks built: {len(tasks)}")
        _save_json_file(tasks, self.config.paths.task_save_path)
        return tasks

    async def _process_single(self, item: Dict[str, Any], save_root: str, success_ids: list) -> None:
        """Process single task (async)"""
        record_id = item.get("record_id")
        if not record_id:
            return
        sid1 = (item.get("meta_info", {}).get("Sample_ID_1", "") or "").split(",")[0].strip()
        sid2 = (item.get("meta_info", {}).get("Sample_ID_2", "") or "").split(",")[0].strip()
        fn = f"{_safe_filename(sid1) or 'X'}_{_safe_filename(sid2) or 'Y'}.json"
        save_path = osp.join(save_root, fn)

        async with self._semaphore:
            for attempt in range(1, self.config.llm.max_retries + 1):
                try:
                    ref = (item.get("expert_data") or {}).get("summary_text") or json.dumps(item.get("expert_data", {}), ensure_ascii=False)
                    mats = item.get("primary_materials") or []
                    sys_prompt = self.SYS_PROMPT.format(primary_materials=", ".join(mats) if mats else "None")
                    user_prompt = self.USER_PROMPT.format(
                        reference_analysis=ref,
                        control_device_fabrication=item.get("control_device_fabrication", ""),
                        target_device_fabrication=item.get("target_device_fabrication", ""),
                    )
                    response = await self._client.chat.completions.create(
                        model=self.config.llm.model,
                        messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                        temperature=self.config.llm.temperature,
                        extra_body={"enable_thinking": True},
                        stream=True
                    )
                    reasoning, answer = "", ""
                    async for chunk in response:
                        choices = getattr(chunk, "choices", None)
                        if not choices:
                            continue
                        delta = choices[0].delta
                        if getattr(delta, "reasoning_content", None):
                            reasoning += delta.reasoning_content
                        if getattr(delta, "content", None):
                            answer += delta.content

                    payload = {
                        "think_part": reasoning.strip(), "answer_part": answer.strip(),
                        "control_device_fabrication": item.get("control_device_fabrication", ""),
                        "target_device_fabrication": item.get("target_device_fabrication", ""),
                        "meta_info": item.get("meta_info", {}),
                    }
                    _atomic_write_json(save_path, payload)
                    success_ids.append(record_id)
                    return
                except Exception as e:
                    if attempt >= self.config.llm.max_retries:
                        stub = {"error": repr(e), **{k: v for k, v in locals().items() if k in ["reasoning", "answer"]}}
                        _atomic_write_json(save_path, stub)
                        return
                    await asyncio.sleep(self.config.llm.retry_base_delay * attempt + random.uniform(0, 1))

    async def inference(self, tasks: List[Dict[str, Any]]) -> List[int]:
        """Execute batch inference"""
        os.makedirs(self.config.paths.dist_save_root, exist_ok=True)
        success_ids = []
        await asyncio.gather(*[self._process_single(t, self.config.paths.dist_save_root, success_ids) for t in tasks], return_exceptions=True)
        return success_ids

    def update_status(self, record_ids: List[int], status: int):
        """Batch update database status"""
        if not record_ids:
            return
        conn = mysql.connector.connect(**self.config.db.to_dict())
        try:
            cursor = conn.cursor()
            for i in range(0, len(record_ids), 1000):
                batch = record_ids[i:i+1000]
                placeholders = ','.join(['%s'] * len(batch))
                cursor.execute(f"UPDATE match_pair SET status = %s WHERE id IN ({placeholders})", [status] + batch)
            conn.commit()
            print(f"[DB] Updated {len(record_ids)} records to status={status}")
        finally:
            conn.close()

    def build_dataset(self, output_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Build final dataset"""
        output_path = output_path or self.config.paths.dataset_path
        out = []
        files = _read_files_by_extension(self.config.paths.dist_save_root, extensions=[".json"])
        for f in files:
            data = _read_json_file(f)
            sys_prompt = "Based on the perovskite formulation and process description, mechanistically analyze the device's Voc, FF, Jsc, and PCE."
            user_prompt = "Control Device Fabrication: {control_device_fabrication}. Optimization Device Fabrication: {target_device_fabrication}."
            out.append({
                "instruction": sys_prompt,
                "input": user_prompt.format(
                    control_device_fabrication=data.get("control_device_fabrication", ""),
                    target_device_fabrication=data.get("target_device_fabrication", "")
                ),
                "output": f"<think>{data.get('think_part', '')}</think><answer>{data.get('answer_part', '')}</answer>"
            })
        _save_json_file(out, output_path)
        print(f"[INFO] dataset size: {len(out)} -> {output_path}")
        return out

    def rebuild_knowledge(self, output_root: Optional[str] = None):
        """Rebuild Markdown knowledge base from database"""
        output_root = output_root or self.config.paths.expert_data_root
        os.makedirs(output_root, exist_ok=True)

        print(f"[INFO] Rebuilding knowledge base to: {output_root}")
        print(f"[INFO] Connecting to database: {self.config.db.host}:{self.config.db.port}/{self.config.db.database}")

        try:
            # Test database connection
            print("[INFO] Testing database connection...")
            conn = mysql.connector.connect(**self.config.db.to_dict(), connect_timeout=10)

            if conn.is_connected():
                print("[SUCCESS] Database connected!")
            else:
                print("[ERROR] Failed to connect to database")
                return

            cursor = conn.cursor(dictionary=True)

            # Check if table exists
            print("[INFO] Checking if table 'markdown_records' exists...")
            cursor.execute("SHOW TABLES LIKE 'markdown_records'")
            result = cursor.fetchone()

            if not result:
                print(f"[WARN] Table 'markdown_records' not found in database")
                print(f"[WARN] Skipping knowledge rebuild, will use existing files if any")
                cursor.close()
                conn.close()
                return

            print("[INFO] Table found, fetching data...")
            cursor.execute("SELECT category_2, material, content FROM `markdown_records`")
            rows = cursor.fetchall()

            if not rows:
                print(f"[WARN] No data in 'markdown_records' table")
                cursor.close()
                conn.close()
                return

            print(f"[INFO] Fetched {len(rows)} records from database")

            valid_categories = {"sam", "additive", "passivator"}
            count = 0

            for row in rows:
                material_key = row.get("material", "")
                content = row.get("content", "")
                if not material_key or not isinstance(material_key, str):
                    continue

                raw_category = row.get("category_2")
                if raw_category and isinstance(raw_category, str):
                    cat_lower = raw_category.strip().lower()
                    subdir = cat_lower.capitalize() if cat_lower in valid_categories else None
                    target_dir = os.path.join(output_root, subdir) if subdir else output_root
                else:
                    target_dir = output_root

                os.makedirs(target_dir, exist_ok=True)
                with open(os.path.join(target_dir, f"{material_key}.md"), "w", encoding="utf-8") as f:
                    f.write(content)
                count += 1

            print(f"\n✅ Rebuilt {count} markdown files into '{output_root}'")
            cursor.close()
            conn.close()

        except mysql.connector.Error as e:
            print(f"[ERROR] MySQL error: {e}")
            print(f"[ERROR] Cannot connect to database at {self.config.db.host}:{self.config.db.port}")
            print(f"[WARN] Skipping knowledge rebuild, will use existing files if any")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            print(f"[WARN] Skipping knowledge rebuild")

    async def run_async(self, rebuild_knowledge: bool = True) -> Dict[str, Any]:
        """Async version of main entry point (recommended for Agent/Tool scenarios)"""
        # Rebuild knowledge base first (if needed) to ensure latest mechanism data
        if rebuild_knowledge:
            self.rebuild_knowledge()
            print("[INFO] Knowledge base rebuilt")

        # Reinitialize knowledge graph (load newly generated .md files)
        self._md_text_cache.clear()
        self._md_map.clear()
        self._init_knowledge_map()

        tasks = self.fetch_tasks()
        if not tasks:
            print("[INFO] No tasks with status=0, exit.")
            return {"success": False, "reason": "no_pending_tasks"}

        all_ids = [t["record_id"] for t in tasks]
        success_ids = await self.inference(tasks)  # ✅ Direct await

        self.update_status(success_ids, status=1)
        failed_ids = [rid for rid in all_ids if rid not in success_ids]
        if failed_ids:
            self.update_status(failed_ids, status=3)

        dataset = self.build_dataset()

        return {
            "success": True,
            "total_tasks": len(tasks),
            "success_count": len(success_ids),
            "failed_count": len(all_ids) - len(success_ids),
            "dataset_size": len(dataset),
            "dataset_path": self.config.paths.dataset_path,
        }

    def run(self, rebuild_knowledge: bool = True) -> Dict[str, Any]:
        """Synchronous version of main entry point - compatible with all runtime environments"""
        import asyncio

        # Rebuild knowledge base first (if needed)
        if rebuild_knowledge:
            self.rebuild_knowledge()
            print("[INFO] Knowledge base rebuilt")

        # Reinitialize knowledge graph (load newly generated .md files)
        self._md_text_cache.clear()
        self._md_map.clear()
        self._init_knowledge_map()

        tasks = self.fetch_tasks()
        if not tasks:
            print("[INFO] No tasks with status=0, exit.")
            return {"success": False, "reason": "no_pending_tasks"}

        all_ids = [t["record_id"] for t in tasks]

        # Run async inference in a compatible way
        try:
            loop = asyncio.get_running_loop()
            # Existing event loop: run in thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.inference(tasks))
                success_ids = future.result()
        except RuntimeError:
            # No event loop: run directly
            success_ids = asyncio.run(self.inference(tasks))

        self.update_status(success_ids, status=1)
        failed_ids = [rid for rid in all_ids if rid not in success_ids]
        if failed_ids:
            self.update_status(failed_ids, status=3)

        dataset = self.build_dataset()

        return {
            "success": True,
            "total_tasks": len(tasks),
            "success_count": len(success_ids),
            "failed_count": len(all_ids) - len(success_ids),
            "dataset_size": len(dataset),
            "dataset_path": self.config.paths.dataset_path,
        }

# ============================================================================
# 🚀 Command-line entry point (optional)
# ============================================================================

def _parse_args():
    parser = argparse.ArgumentParser(description="Perovskite Mechanism Analyzer")
    parser.add_argument("--config", type=str, default=None, help="Path to config JSON file")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild knowledge files from DB")
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch tasks, skip inference")
    parser.add_argument("--inference-only", action="store_true", help="Only run inference on existing tasks")
    return parser.parse_args()


def main():
    """Simple and direct entry point - no parameters required"""
    print("=" * 60)
    print("🔬 Perovskite Mechanism Analyzer")
    print("=" * 60)

    # Direct instantiation and run
    analyzer = PerovskiteAnalyzer()

    # Execute full pipeline (rebuild knowledge base by default)
    result = analyzer.run(rebuild_knowledge=True)

    print(f"\n✅ Pipeline completed!")
    print(f"📊 Results:")
    print(f"   - Total tasks: {result.get('total_tasks', 0)}")
    print(f"   - Success: {result.get('success_count', 0)}")
    print(f"   - Failed: {result.get('failed_count', 0)}")
    print(f"   - Dataset size: {result.get('dataset_size', 0)}")
    print(f"   - Saved to: {result.get('dataset_path', 'N/A')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
