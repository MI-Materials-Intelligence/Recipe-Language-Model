# -*- coding: utf-8 -*-
"""
Robotic Learning Data Automated Processing Pipeline
Supports: DB export -> Excel conversion -> Algorithm matching -> Write-back to DB -> Cleanup

Usage:
    1. Run directly: python this_script.py
    2. Import externally: from this_script import RoboticDataPipeline; pipeline = RoboticDataPipeline(); pipeline.run_full_process(table_name="xxx")
"""

import csv
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import mysql.connector
import pandas as pd
from mysql.connector import Error

# Load database configuration from app.config
try:
    from seven_ai_layers_robotics.config import config
    DB_CONFIG = {
        'host': config.learning_database.host,
        'port': config.learning_database.port,
        'user': config.learning_database.user,
        'password': config.learning_database.password,
        'database': config.learning_database.database,
        'charset': config.learning_database.charset,
    }
except Exception as e:
    print(f"⚠️ WARNING: Failed to load config, using empty database configuration. Error: {e}")
    DB_CONFIG = {
        'host': '',
        'port': 3306,
        'user': 'root',
        'password': '',
        'database': '',
        'charset': 'utf8mb4'
    }

# Working directory and data output paths
WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(WORK_DIR, "data")

# Import pipeline functions and extractor
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
    """Robotic Learning Data Automated Processing Pipeline.
    
    Supports: DB export -> Excel conversion -> Algorithm matching -> 
    Write-back to DB -> Cleanup
    """

    def __init__(
        self,
        db_config: Optional[Dict[str, Any]] = None,
        work_dir: Optional[str] = None,
    ):
        """Initialize pipeline.
        
        Args:
            db_config: Database configuration dictionary. Defaults to DB_CONFIG if not provided.
            work_dir: Working directory path. Defaults to WORK_DIR if not provided.
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
        """Execute external matching algorithm pipeline.
        
        Args:
            xlsx_filename: Input Excel filename to process.
            
        Returns:
            True if successful.
            
        Raises:
            ImportError: If single_var_matching_pipeline module is not available.
            Exception: If pipeline execution fails.
        """
        if not PIPELINE_AVAILABLE:
            raise ImportError(
                "single_var_matching_pipeline module not found, unable to execute matching."
            )
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
        SELECT 1 FROM no_characterisation_match
        WHERE sample_id_1 = %s AND sample_id_2 = %s
          AND reverse_diff_class = %s AND analysis_type = %s
        LIMIT 1
        """
        cursor.execute(query, (sid1, sid2, reverse_diff_class, analysis_type))
        return cursor.fetchone() is not None

    def _insert_record(self, cursor, analysis_type, reverse_diff_class, sid1, sid2, ctrl_fab, tgt_fab, file_path, meta_info):
        query = """
        INSERT INTO no_characterisation_match
        (analysis_type, reverse_diff_class, sample_id_1, sample_id_2,
         control_device_fabrication, target_device_fabrication, json_file_path, meta_info)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        meta_json_str = json.dumps(meta_info, ensure_ascii=False)
        cursor.execute(query, (analysis_type, reverse_diff_class, sid1, sid2, ctrl_fab, tgt_fab, file_path, meta_json_str))

    def _process_matched_pair(self, pair: dict, file_path: str, cursor, stats):
        """
        Process a single matched pair from the new format (list of pairs).
        
        Args:
            pair: Dictionary containing matched pair information
            file_path: Path to the JSON file
            cursor: Database cursor
            stats: Statistics dictionary
        """
        try:
            # Extract required fields from the pair
            pair_index = pair.get("pair_index", "")
            diff_columns = pair.get("diff_columns", [])
            
            # Extract sample IDs from pair_index (format: "SampleID_123-SampleID_456")
            if not pair_index or "-" not in pair_index:
                return
            
            parts = pair_index.split("-")
            if len(parts) != 2:
                return
            
            sid1_raw = parts[0].replace("SampleID_", "").strip()
            sid2_raw = parts[1].replace("SampleID_", "").strip()
            
            if not sid1_raw.isdigit() or not sid2_raw.isdigit():
                return
            
            sid1 = int(sid1_raw)
            sid2 = int(sid2_raw)
            
            # Use diff_columns as reverse_diff_class (join them)
            reverse_diff_class = ";".join(diff_columns) if isinstance(diff_columns, list) else str(diff_columns)
            
            # Get analysis type (default to "formula" or infer from data)
            analysis_type = pair.get("analysis_type", "formula")
            
            # Get fabrication info
            ctrl_fab = pair.get("control_device_fabrication", "").strip()
            tgt_fab = pair.get("target_device_fabrication", "").strip()
            
            # Build meta info from pair data
            meta_info = {
                "pair_index": pair_index,
                "diff_columns": diff_columns,
                "date": pair.get("date", ""),
                "PCE_change": pair.get("PCE_Change", ""),
                "diff_part": pair.get("diff_part", ""),
            }
            
            # Check if record exists
            if self._record_exists(cursor, str(sid1), str(sid2), reverse_diff_class, analysis_type):
                stats['skipped'] += 1
            else:
                self._insert_record(cursor, analysis_type, reverse_diff_class, str(sid1), str(sid2), ctrl_fab, tgt_fab, file_path, meta_info)
                stats['inserted'] += 1
                
        except Exception as e:
            print(f"⚠️ Warning: Failed to process pair: {e}")

    def _process_json_file(self, file_path, cursor, stats):
        """
        Process a single JSON file and insert records into database.
        Supports two formats:
        1. Old format: {"reverse_diff_class": "...", "data": {...}}
        2. New format (list of matched pairs): [{"pair_index": "...", "diff_columns": [...], ...}]
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ JSON parsing failed: {file_path} - {e}")
            return
        
        # Check if this is the new format (list of matched pairs)
        if isinstance(data, list):
            # New format: process each matched pair directly
            for pair in data:
                self._process_matched_pair(pair, file_path, cursor, stats)
        elif isinstance(data, dict):
            # Old format: extract reverse_diff_class and data
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

    def run_full_process(
        self, table_name: str, output_xlsx_name: Optional[str] = None
    ) -> bool:
        """Execute complete workflow: export -> conversion -> matching -> write-back -> cleanup.
        
        Args:
            table_name: Source database table name.
            output_xlsx_name: Output Excel filename. Defaults to table_name.xlsx if not provided.
            
        Returns:
            True if successful.
            
        Raises:
            ImportError: If DataExtractor module is not available.
            Exception: If any workflow step fails.
        """
        if not EXTRACTOR_AVAILABLE:
            raise ImportError(
                "DataExtractor module not found, unable to execute data extraction."
            )

        if output_xlsx_name is None:
            output_xlsx_name = f"{table_name}.xlsx"

        # All intermediate files output to data directory
        csv_file = os.path.join(self.data_dir, "temp_export.csv")
        xlsx_file = os.path.join(self.data_dir, output_xlsx_name)

        try:
            # Step 1 & 2: Use DataExtractor for export and conversion
            self.data_extractor.extract_and_convert(table_name, csv_file, xlsx_file)

            # Step 3: Pipeline - use CSV file instead of XLSX to avoid CRC-32 errors
            print("\n📝 Using CSV format for matching pipeline to avoid Excel corruption issues...")
            if not self.run_matching_pipeline("temp_export.csv"):
                raise Exception("Pipeline execution failed")

            # Step 4: Ingest
            # Scan BOTH date directory and tasks directory for JSON files
            # json_folder_date = os.path.join(self.data_dir, "fp", "date")
            json_folder_tasks = os.path.join(self.data_dir, "fp", "tasks")
            
            print(f"\n📥 Starting to write JSON results to database...")
            total_stats = {'inserted': 0, 'skipped': 0}
            
            # First, scan date directory (original matched pairs)
            # if os.path.exists(json_folder_date):
            #     print(f"   Scanning date directory: {json_folder_date}")
            #     date_stats = self.ingest_json_to_db(json_folder_path=json_folder_date, do_cleanup=False)
            #     total_stats['inserted'] += date_stats['inserted']
            #     total_stats['skipped'] += date_stats['skipped']
            # else:
            #     print(f"   ⚠️ Date directory not found: {json_folder_date}")
            
            # Then, scan tasks directory (classified by diff type)
            if os.path.exists(json_folder_tasks):
                print(f"   Scanning tasks directory: {json_folder_tasks}")
                tasks_stats = self.ingest_json_to_db(json_folder_path=json_folder_tasks, do_cleanup=False)
                total_stats['inserted'] += tasks_stats['inserted']
                total_stats['skipped'] += tasks_stats['skipped']
            else:
                print(f"   ⚠️ Tasks directory not found: {json_folder_tasks}")
            
            print(f"\n📊 Total inserted: {total_stats['inserted']}, skipped: {total_stats['skipped']}")

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
    success = pipeline.run_full_process(table_name="experiments_data")

    if not success:
        print("\n❌ Workflow execution failed, please check logs.")
        sys.exit(1)
    else:
        print("\n✅ All tasks completed!")
