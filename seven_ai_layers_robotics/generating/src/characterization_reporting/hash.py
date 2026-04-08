import hashlib
import json

import mysql.connector

from seven_ai_layers_robotics.config import config

# Category: Global Configuration
MYSQL_CONFIG = {
    'host': config.generating_database.host,
    'port': config.generating_database.port,
    'user': config.generating_database.user,
    'password': config.generating_database.password,
    'database': config.generating_database.database,
    'charset': config.generating_database.charset,
}

def compute_pair_hash_from_row(row):
    """
    Calculate pair_hash from database row
    """
    
    if row["additive"]:
        factor_type = "Additive"
        factor_value = json.loads(row["additive"])
    elif row["passivator"]:
        factor_type = "Passivator"
        factor_value = json.loads(row["passivator"])
    elif row["sam"]:
        factor_type = "SAM"
        factor_value = json.loads(row["sam"])
    elif row["process"]:
        factor_type = "Process"
        factor_value = json.loads(row["process"])
    else:
        return None  

    payload = {
        "sample_id_1": row["sample_id_1"],
        "sample_id_2": row["sample_id_2"],
        "pair_source": row["pair_source"],
        "factor_type": factor_type,
        "factor_value": factor_value,
    }

    normalized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def backfill_hash():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, sample_id_1, sample_id_2, pair_source,
               additive, passivator, sam, process
        FROM characterisation_match
        WHERE content_hash IS NULL
    """)
    rows = cursor.fetchall()

    print(f"Number of records requiring hash backfill: {len(rows)}")

    update_sql = """
        UPDATE characterisation_match
        SET content_hash = %s
        WHERE id = %s
    """

    for r in rows:
        h = compute_pair_hash_from_row(r)
        if h:
            cursor.execute(update_sql, (h, r["id"]))

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    backfill_hash()
    