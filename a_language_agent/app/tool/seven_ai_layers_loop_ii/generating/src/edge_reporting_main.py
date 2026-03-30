# -*- coding: utf-8 -*-
"""
Edge Report Automated Data Processing Pipeline
Supports: Data cleaning -> Generating experimental description reports -> Calling DeepSeek for mechanism analysis

Usage:
    1. Direct execution: python this_script.py
    2. External import: from this_script import EdgeReportPipeline; pipeline = EdgeReportPipeline(); pipeline.run()
"""

import os
import sys
from typing import Optional, Dict, Any

# ==============================
# Import Configuration Loader
# ==============================
# Add the current script's directory to sys.path to import config_loader
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

# Load configuration from app.config
from app.config import config

# Load database configuration from app.config (using Generating module)
DB_CONFIG = {
    'host': config.generating_database.host,
    'port': config.generating_database.port,
    'user': config.generating_database.user,
    'password': config.generating_database.password,
    'database': config.generating_database.database,
    'charset': config.generating_database.charset,
}
DEFAULT_DB_URI = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4"

# ==============================
# Built-in Configuration (No external input required)
# ==============================

# Working Directory (Defaults to current script path)
WORK_DIR = _script_dir

# Data Output Directory (Sibling to src)
DATA_DIR = os.path.join(WORK_DIR, "..", "data")

# ==============================
# Import Step Modules
# ==============================

try:
    # Attempt to import each step module
    STEP_MODULES = {}

    # Add Edge_Reporting directory to sys.path
    _edge_reporting_dir = os.path.join(_script_dir, 'Edge_Reporting')
    if _edge_reporting_dir not in sys.path:
        sys.path.insert(0, _edge_reporting_dir)

    # Step 2: Generate Report
    try:
        import step2_report
        STEP_MODULES['step2'] = step2_report
    except ImportError as e:
        print(f"⚠️ Warning: Unable to import step2_report module. Error: {e}")

    # Step 3: DeepSeek Analysis
    try:
        import step3_deepseek
        STEP_MODULES['step3'] = step3_deepseek
    except ImportError as e:
        print(f"⚠️ Warning: Unable to import step3_deepseek module. Error: {e}")

    MODULES_AVAILABLE = len(STEP_MODULES) > 0

except Exception as e:
    MODULES_AVAILABLE = False
    print(f"⚠️ Warning: Unable to load step modules, some functionality will be unavailable. Error: {e}")


# ==============================
# Core Class Encapsulation
# ==============================

class EdgeReportPipeline:
    """Edge Report Automated Data Processing Pipeline"""

    def __init__(self,
                 db_uri: Optional[str] = None,
                 db_config: Optional[Dict[str, Any]] = None,
                 json_root_dir: Optional[str] = None,
                 work_dir: Optional[str] = None):
        """
        Initialize the pipeline
        :param db_uri: Database URI (Optional, uses built-in config if not provided)
        :param db_config: Database configuration (Optional, uses built-in config if not provided)
        :param json_root_dir: JSON root directory (Optional, uses built-in config if not provided)
        :param work_dir: Working directory (Optional, uses built-in config if not provided)
        """
        self.db_uri = db_uri if db_uri else DEFAULT_DB_URI
        self.db_config = db_config if db_config else DB_CONFIG
        self.json_root_dir = json_root_dir if json_root_dir else WORK_DIR
        self.work_dir = work_dir if work_dir else WORK_DIR
        self.data_dir = DATA_DIR

        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        # Dynamically inject configuration into each step module
        self._setup_step2()
        self._setup_step3()


    def _setup_step2(self):
        """Configure Step 2 module"""
        if 'step2' not in STEP_MODULES:
            return

        s2 = STEP_MODULES['step2']
        s2.DB_URI = self.db_uri
        s2.DB_CONFIG = self.db_config
        # Correct the output path in TASKS to absolute path, save to Generating/data/reports directory
        reports_dir = os.path.join(self.data_dir,  "edge", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        if hasattr(s2, 'TASKS'):
            for task in s2.TASKS:
                base_name = os.path.basename(task.get("output", ""))
                task["output"] = os.path.join(reports_dir, base_name)

    def _setup_step3(self):
        """Configure Step 3 module"""
        if 'step3' not in STEP_MODULES:
            return

        s3 = STEP_MODULES['step3']
        s3.DB_CONFIG = self.db_config
        # JSON output to data directory, not src directory
        s3.JSON_ROOT_DIR = os.path.join(self.data_dir)
        # Fix API URL (original code has extra spaces at the end)
        if hasattr(s3, 'API_URL'):
            s3.API_URL = s3.API_URL.strip()


    def run_step2(self, verbose: bool = True):
        """Execute Step 2: Generate experimental description report"""
        if 'step2' not in STEP_MODULES:
            raise ImportError("step2_report module not found")

        if verbose:
            print("📄 Step 2: Generating experimental description report")

        s2 = STEP_MODULES['step2']
        s2.ensure_single_report_unique_index()
        if hasattr(s2, 'TASKS'):
            for task in s2.TASKS:
                df = s2.read_table(task["table"])
                s2.generate_docx_from_df(
                    df=df,
                    output_path=task["output"],
                    xrd_mode=task.get("xrd_mode"),
                    index_col=task.get("index_col"),
                    source_table=task["table"]
                )

    def run_step3(self, verbose: bool = True):
        """Execute Step 3: Call DeepSeek to generate mechanism analysis"""
        if 'step3' not in STEP_MODULES:
            raise ImportError("step3_deepseek module not found")

        if verbose:
            print("🧠 Step 3: Calling DeepSeek to generate mechanism analysis")

        s3 = STEP_MODULES['step3']
        s3.main()

    def run(self, steps: str = 'all', verbose: bool = True) -> bool:
        """
        Execute the report generation process
        :param steps: Steps to execute ('all', 'step1', 'step2', 'step3', or combinations like 'step1,step2')
        :param verbose: Whether to print detailed logs
        :return: Success status
        """
        if not MODULES_AVAILABLE:
            raise ImportError("Step modules not found, unable to execute report generation.")

        try:
            if steps == 'all':
                # Execute all steps
                step_list = ['step2', 'step3']
            else:
                # Execute specified steps
                step_list = [s.strip() for s in steps.split(',')]

            for step_name in step_list:
                if step_name == 'step2':
                    self.run_step2(verbose=verbose)
                elif step_name == 'step3':
                    self.run_step3(verbose=verbose)
                else:
                    print(f"⚠️ Skipping unknown step: {step_name}")

            if verbose:
                print("\n🎉 Entire process completed!")
            return True

        except Exception as e:
            print(f"🛑 Process interrupted: {e}")
            import traceback
            traceback.print_exc()
            return False


# ==============================
# Main Entry Point (Script Direct Execution)
# ==============================

if __name__ == "__main__":
    print("=" * 60)
    print("📊 Edge Report Automated Data Processing Pipeline")
    print("=" * 60)
    print(f"📁 Working Directory: {WORK_DIR}")
    print(f"🗄️  Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"📂 Data Output Directory: {DATA_DIR}")
    print("=" * 60)
    print(f"📋 Available Step Modules: {list(STEP_MODULES.keys())}")
    print("=" * 60)

    # Initialize and execute
    pipeline = EdgeReportPipeline()
    success = pipeline.run(steps='all', verbose=True)

    if not success:
        print("\n❌ Process execution failed, please check logs.")
        sys.exit(1)
    else:
        print("\n✅ All tasks completed!")
        