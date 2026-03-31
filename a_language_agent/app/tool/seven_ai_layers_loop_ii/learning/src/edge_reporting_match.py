# -*- coding: utf-8 -*-
"""
Edge Report Data Automated Processing Pipeline
Supports: DB export -> Cleaning and deduplication -> Write-back to DB

Usage:
    1. Run directly: python this_script.py
    2. Import externally: from this_script import EdgeReportPipeline; pipeline = EdgeReportPipeline(); pipeline.run_full_process(src_table="data50764", target_table="data50764_select")
"""

import os
import sys
from typing import Optional, Dict, Any

import sys
import os

# ==============================
# Import configuration
# ==============================
# Load database configuration from app.config
from app.config import config

DB_CONFIG = {
    'host': config.learning_database.host,
    'port': config.learning_database.port,
    'user': config.learning_database.user,
    'password': config.learning_database.password,
    'database': config.learning_database.database,
    'charset': config.learning_database.charset,
}

# ==============================
# Built-in configuration (no need to pass from external)
# ==============================

# Working directory (default to current script path)
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

# Data output directory (at same level as src)
DATA_DIR = os.path.join(WORK_DIR, "..", "data")

# ==============================
# Import extractor
# ==============================

try:
    # Use relative imports to avoid path issues in multi-process environments
    from .extraction.edge_report_extractor import EdgeReportExtractor
    EXTRACTOR_AVAILABLE = True
except ImportError as e:
    EXTRACTOR_AVAILABLE = False
    print(f"⚠️ WARNING: Unable to import EdgeReportExtractor, data extraction functionality will be unavailable. Error: {e}")

# ==============================
# Core class definition
# ==============================

class EdgeReportPipeline:
    """Edge Report Data Automated Processing Pipeline"""

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
            self.data_extractor = EdgeReportExtractor(self.db_config)

    def run_full_process(self, src_table: str) -> bool:
        """
        Execute complete workflow: export -> cleaning and deduplication -> write-back
        :param src_table: Source database table name
        :param target_table: Target database table name
        :return: Success status
        """
        if not EXTRACTOR_AVAILABLE:
            raise ImportError("EdgeReportExtractor module not found, unable to execute data extraction.")

        try:
            # Use EdgeReportExtractor for complete processing, all output to data directory
            target_table = "data50764_select"
            self.data_extractor.extract_and_process(src_table, target_table, self.data_dir)

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
    print("📊 Edge Report Data Automated Processing Pipeline")
    print("=" * 60)
    print(f"📁 Working Directory: {WORK_DIR}")
    print(f"🗄️  Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 60)

    # Initialize and execute
    pipeline = EdgeReportPipeline()
    success = pipeline.run_full_process(src_table="data50764", target_table="data50764_select")

    if not success:
        print("\n❌ Workflow execution failed, please check logs.")
        sys.exit(1)
    else:
        print("\n✅ All tasks completed!")
