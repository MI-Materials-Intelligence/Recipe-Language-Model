# -*- coding: utf-8 -*-
"""
Robotic Learning Data Automated Processing Pipeline
Supports: DB export -> Excel conversion -> Algorithm matching -> Write-back to DB -> Cleanup

Usage:
    1. Run directly: python this_script.py
    2. Import externally: from this_script import RoboticDataPipeline; pipeline = RoboticDataPipeline(); pipeline.run_full_process(table_name="xxx")
"""

import os
import sys
import csv
import json
import shutil
import pandas as pd
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any

# ==============================
# Built-in configuration (no need to pass from external)
# ==============================

# Database configuration
DB_CONFIG = {
    'host': '',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': '',
    'charset': 'utf8mb4'
}

# Working directory (default to parent directory of current script path)
WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data output directory
DATA_DIR = os.path.join(WORK_DIR, "data")

# ==============================
# Import pipeline function and extractor
# ==============================

try:
    # Use relative imports to avoid path issues in multi-process environments
    from .matching.single_var_matching_pipeline import run as single_var_matching_pipeline
    PIPELINE_AVAILABLE = True
except ImportError as e:
    PIPELINE_AVAILABLE = False
    print(f"⚠️ WARNING: Unable to import single_var_matching_pipeline, matching functionality will be unavailable. Error: {e}")
except Exception as e:
    PIPELINE_AVAILABLE = False
    print(f"⚠️ WARNING: Unable to load single_var_matching_pipeline, matching functionality will be unavailable. Error: {e}")

try:
    from .extraction.data_extractor import DataExtractor
    EXTRACTOR_AVAILABLE = True
except ImportError as e:
    EXTRACTOR_AVAILABLE = False
    print(f"⚠️ WARNING: Unable to import DataExtractor, data extraction functionality will be unavailable. Error: {e}")


# ==============================
# Core class definition
# ==============================

class RoboticDataPipeline:
    """Robotic Learning Data Automated Processing Pipeline"""

    def __init__(self,
                 db_config: Optional[Dict[str, Any]] = None,
                 work_dir: Optional[str] = None):
        """
        Initialize pipeline
        :param db_config: Database configuration (optional, uses built-in config if not provided)
        :param work_dir: Working directory (optional, uses built-in config if not provided)
        """
        self.db_config = db_config if db_config else DB_CONFIG
        self.work_dir = work_dir if work_dir else WORK_DIR
        self.data_dir = DATA_DIR
        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        # Initialize data extractor
        if EXTRACTOR_AVAILABLE:
            self.data_extractor = DataExtractor(self.db_config)



    def run_matching_pipeline(self, xlsx_filename: str) -> bool:
        """Execute external matching algorithm Pipeline"""
        if not PIPELINE_AVAILABLE:
            raise ImportError("single_var_matching_pipeline module not found, unable to execute matching.")
        try:
            print("🚀 Starting single_var_matching_pipeline...")
            # Execute matching in data directory
            single_var_matching_pipeline(self.data_dir, xlsx_filename)
            return True
        except Exception as e:
            print(f"❌ Pipeline execution failed: {e}")
            return False

    # ==============================
    # JSON processing internal methods
    # ==============================

    @staticmethod
    def _extract_id_from_sample_field(s: str) -> str:
        if not s or not isinstance(s, str):
            return ""
        return s.split(",")[0].strip()

    def _record_exists(self, cursor, sid1, sid2, reverse_diff_class, analysis_type) -> bool:
        query = """
        SELECT 1 FROM match_pair_copy1
        WHERE sample_id_1 = %s AND sample_id_2 = %s
          AND reverse_diff_class = %s AND analysis_type = %s
        LIMIT 1
        """
        cursor.execute(query, (sid1, sid2, reverse_diff_class, analysis_type))
        return cursor.fetchone() is not None

    def _insert_record(self, cursor, analysis_type, reverse_diff_class, sid1, sid2, ctrl_fab, tgt_fab, file_path, meta_info):
        query = """
        INSERT INTO match_pair_copy1
        (analysis_type, reverse_diff_class, sample_id_1, sample_id_2,
         control_device_fabrication, target_device_fabrication, json_file_path, meta_info)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        meta_json_str = json.dumps(meta_info, ensure_ascii=False)
        cursor.execute(query, (analysis_type, reverse_diff_class, sid1, sid2, ctrl_fab, tgt_fab, file_path, meta_json_str))

    def _process_json_file(self, file_path, cursor, stats):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ JSON parsing failed: {file_path} - {e}")
            return

        reverse_diff_class = data.get("reverse_diff_class", "")
        json_data = data.get("data", {})

        for pair_key, content in json_data.items():
            meta = content.get("Meta Info", {})
            inputs = content.get("Input", {})
            analysis_type = meta.get("Analysis_Type", "")
            raw_sid1 = meta.get("Sample_ID_1", "")
            raw_sid2 = meta.get("Sample_ID_2", "")

            sid1 = self._extract_id_from_sample_field(raw_sid1)
            sid2 = self._extract_id_from_sample_field(raw_sid2)

            if not sid1.isdigit() or not sid2.isdigit():
                continue

            ctrl_fab = inputs.get("control_device_fabrication", "").strip()
            tgt_fab = inputs.get("target_device_fabrication", "").strip()

            if self._record_exists(cursor, sid1, sid2, reverse_diff_class, analysis_type):
                stats['skipped'] += 1
            else:
                self._insert_record(cursor, analysis_type, reverse_diff_class, sid1, sid2, ctrl_fab, tgt_fab, file_path, meta)
                stats['inserted'] += 1

    def ingest_json_to_db(self, json_folder_path: Optional[str] = None, do_cleanup: bool = True) -> Dict[str, int]:
        """
        Scan JSON folder and insert into database
        :param json_folder_path: JSON result directory, defaults to data_dir/fp/tasks
        :param do_cleanup: Whether to clean up intermediate files after processing
        :return: Statistics dictionary {'inserted': int, 'skipped': int}
        """
        if json_folder_path is None:
            json_folder_path = os.path.join(self.data_dir, "fp", "tasks")

        conn = None
        cursor = None
        stats = {'inserted': 0, 'skipped': 0}
        total_files = 0

        try:
            print("🔌 Connecting to database...")
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            print(f"📂 Starting to scan directory: {json_folder_path}")
            if not os.path.exists(json_folder_path):
                print(f"⚠️ Directory does not exist: {json_folder_path}")
                return stats

            for root, _, files in os.walk(json_folder_path):
                for file in files:
                    if file.lower().endswith('.json'):
                        full_path = os.path.join(root, file)
                        total_files += 1
                        print(f"📄 Processing: {full_path}")
                        self._process_json_file(full_path, cursor, stats)

            conn.commit()
            print("\n" + "="*50)
            print(f"✅ Scanning completed: {total_files} JSON files")
            print(f"📊 Actually inserted new records: {stats['inserted']}")
            print(f"⏭️  Skipped duplicate records: {stats['skipped']}")
            print("="*50)

            if do_cleanup:
                self.cleanup_intermediate_files()

            return stats

        except Error as e:
            print(f"❌ Database error: {e}")
            if conn: conn.rollback()
            raise e
        except Exception as e:
            print(f"💥 Other error: {e}")
            if conn: conn.rollback()
            raise e
        finally:
            if conn and conn.is_connected():
                if cursor: cursor.close()
                conn.close()
                print("🔌 Database connection closed.")

    def cleanup_intermediate_files(self):
        """Delete intermediate files and fp directory under data directory"""
        deleted = []

        # Delete fp and formula directories under data directory
        fp_dir = os.path.join(self.data_dir, "fp")
        fp_dir2 = os.path.join(self.data_dir, "formula")
        if os.path.exists(fp_dir):
            try:
                shutil.rmtree(fp_dir)
                shutil.rmtree(fp_dir2)
                deleted.append(f"📁 Deleted directory: {fp_dir}")
                deleted.append(f"📁 Deleted directory: {fp_dir2}")
            except Exception as e:
                print(f"⚠️ Unable to delete directory: {e}")

        # Delete intermediate CSV files under data directory
        intermediate_csvs = [
            "re_formula_remove_abnormal.csv",
            "re_formula_dedup.csv",
            "re_fp_dedup.csv",
            "re_no_dedup.csv",
            "temp_export.csv"
        ]

        for csv_file in intermediate_csvs:
            csv_path = os.path.join(self.data_dir, csv_file)
            if os.path.exists(csv_path):
                try:
                    os.remove(csv_path)
                    deleted.append(f"🗑️  Deleted file: {csv_path}")
                except Exception as e:
                    print(f"⚠️ Unable to delete {csv_file}: {e}")

        # Delete generated Excel files (if needed)
        # Note: Input xlsx files are not deleted here, only intermediate process files

        if deleted:
            print("\n🧹 Cleanup completed:")
            for msg in deleted:
                print(f"  {msg}")
        else:
            print("ℹ️ No intermediate files to clean up.")

    def run_full_process(self, table_name: str, output_xlsx_name: Optional[str] = None) -> bool:
        """
        Execute complete workflow: export -> conversion -> matching -> write-back -> cleanup
        :param table_name: Source database table name
        :param output_xlsx_name: Output Excel filename (optional, defaults to table_name.xlsx)
        :return: Success status
        """
        if not EXTRACTOR_AVAILABLE:
            raise ImportError("DataExtractor module not found, unable to execute data extraction.")

        if output_xlsx_name is None:
            output_xlsx_name = f"{table_name}.xlsx"

        # All intermediate files output to data directory
        csv_file = os.path.join(self.data_dir, "temp_export.csv")
        xlsx_file = os.path.join(self.data_dir, output_xlsx_name)

        try:
            # Step 1 & 2: Use DataExtractor for export and conversion
            self.data_extractor.extract_and_convert(table_name, csv_file, xlsx_file)

            # Step 3: Pipeline
            if not self.run_matching_pipeline(output_xlsx_name):
                raise Exception("Pipeline execution failed")

            # Step 4: Ingest
            json_folder = os.path.join(self.data_dir, "fp", "tasks")
            if os.path.exists(json_folder):
                print("\n📥 Starting to write JSON results to database...")
                self.ingest_json_to_db(json_folder_path=json_folder, do_cleanup=True)
            else:
                print(f"⚠️ JSON result directory does not exist: {json_folder}")

            self.cleanup_intermediate_files()

            print("\n🎉 Full workflow completed successfully!")
            return True

        except Exception as e:
            print(f"🛑 Workflow interrupted: {e}")
            return False


# ==============================
# Main entry point (script direct execution)
# ==============================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Robotic Learning Data Automated Processing Pipeline")
    print("=" * 60)
    print(f"📁 Working Directory: {WORK_DIR}")
    print(f"🗄️  Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 60)

    # Get user input for table name
    # table_name = input("\n📋 Please enter the database table name to process: ").strip()

    # if not table_name:
    #     print("❌ Table name cannot be empty, exiting.")
    #     sys.exit(1)

    # Initialize and execute
    pipeline = RoboticDataPipeline()
    success = pipeline.run_full_process(table_name="data3000")

    if not success:
        print("\n❌ Workflow execution failed, please check logs.")
        sys.exit(1)
    else:
        print("\n✅ All tasks completed!")
