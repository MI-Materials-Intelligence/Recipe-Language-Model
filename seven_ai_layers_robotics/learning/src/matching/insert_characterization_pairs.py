from __future__ import annotations

import json
import hashlib
from typing import List, Dict
import os
import mysql.connector
from mysql.connector import Error
from pathlib import Path

# =========================
# Import configuration from app.config
# =========================
from app.config import config

# ==========================
# MySQL Configuration
# ==========================
MYSQL_CONFIG = {
    "host": config.learning_database.host,
    "user": config.learning_database.user,
    "password": config.learning_database.password,
    "database": config.learning_database.database,
    "port": config.learning_database.port,
    "charset": config.learning_database.charset,
}

TABLE_NAME = "experiments_characterization_pairs"

# 工作目录（默认为当前脚本所在路径的父目录）
WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# JSON 文件输入目录（在 data 目录下）
DATA_DIR = os.path.join(WORK_DIR,"..", "data")

FILES = [
    os.path.join(DATA_DIR, "PL_sam", "PL_sam_pairs.json"),
    os.path.join(DATA_DIR, "Image_process", "image_process_pairs.json"),
    os.path.join(DATA_DIR, "XRD_additives", "additive_xrd_pairs.json"),
    os.path.join(DATA_DIR, "XRD_passivators", "passivators_xrd_pairs.json"),
]

# ==============================
# JSON 读取（array / 多对象拼接）
# ==============================
def load_json_records(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()

    # Case 1: 标准 JSON array
    if content.startswith("["):
        return json.loads(content)

    # Case 2: 多个 {} 拼接
    records = []
    buf = ""
    depth = 0
    for ch in content:
        if ch == "{":
            depth += 1
        if depth > 0:
            buf += ch
        if ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    records.append(json.loads(buf))
                except Exception:
                    pass
                buf = ""
    return records


# ==============================
# Pair hash（去重核心）
# ==============================
def compute_pair_hash(record: dict) -> str:
    """
    基于：
    sample_id_1 + sample_id_2 + pair_source + 调控因子（类型 + 内容）
    生成唯一 hash
    """

    if "Additive" in record:
        factor_type = "Additive"
        factor_value = record.get("Additive")
    elif "Passivator" in record:
        factor_type = "Passivator"
        factor_value = record.get("Passivator")
    elif "SAM" in record:
        factor_type = "SAM"
        factor_value = record.get("SAM")
    elif "Process" in record:
        factor_type = "Process"
        factor_value = record.get("Process")
    else:
        raise ValueError("❌ 未找到调控因子字段")

    payload = {
        "sample_id_1": record.get("sample_id_1"),
        "sample_id_2": record.get("sample_id_2"),
        "pair_source": record.get("pair_source"),
        "factor_type": factor_type,
        "factor_value": factor_value,
    }

    normalized = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True
    )

    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# ==============================
# 增量插入（IGNORE + hash）
# ==============================
def insert_records_incremental(
    conn,
    records: List[Dict],
    file_path: str,
):
    cursor = conn.cursor()

    sql = f"""
    INSERT IGNORE INTO {TABLE_NAME} (
        question, control, target,
        additive, passivator, sam, process,
        pair_source,
        sample_id_1, sample_id_2,
        sample_id_1_date, sample_id_2_date,
        status, file_path,
        content_hash
    ) VALUES (
        %s, %s, %s,
        %s, %s, %s, %s,
        %s,
        %s, %s,
        %s, %s,
        %s, %s,
        %s
    )
    """

    batch = []

    for r in records:
        pair_hash = compute_pair_hash(r)

        batch.append((
            r.get("question"),
            r.get("control"),
            r.get("target"),

            json.dumps(r.get("Additive")) if "Additive" in r else None,
            json.dumps(r.get("Passivator")) if "Passivator" in r else None,
            json.dumps(r.get("SAM")) if "SAM" in r else None,
            json.dumps(r.get("Process")) if "Process" in r else None,

            r.get("pair_source"),
            r.get("sample_id_1"),
            r.get("sample_id_2"),
            r.get("sample_id_1_date"),
            r.get("sample_id_2_date"),

            "pending",
            file_path,
            pair_hash,
        ))

    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
        print(
            f"✅ {file_path} | "
            f"尝试 {len(batch)} 条 | "
            f"新增 {cursor.rowcount} 条"
        )

    cursor.close()


# ==============================
# 主逻辑
# ==============================
def main() -> None:
    conn = None
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("🔌 MySQL connected")

        for file_path in FILES:
            print(f"\n📂 Processing: {file_path}")
            records = load_json_records(file_path)
            print(f"   ➜ {len(records)} records")

            if records:
                insert_records_incremental(conn, records, file_path)

    except Error as e:
        print(f"❌ MySQL error: {e}")

    finally:
        if conn and conn.is_connected():
            conn.close()
            print("\n🔒 MySQL connection closed")


# ==============================
# Pipeline / Agent 入口
# ==============================
def run(
    *,
    verbose: bool = True,
) -> None:
    if verbose:
        print("▶ Running Insert Characterization Pairs pipeline...")

    main()

    if verbose:
        print("✅ Insert Characterization Pairs pipeline finished.")


# ==============================
# CLI
# ==============================
if __name__ == "__main__":
    run()
