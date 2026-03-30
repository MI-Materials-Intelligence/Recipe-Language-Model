# -*- coding: utf-8 -*-
"""
Variable Report Automated Data Processing Pipeline
Supports: Fetching pending data from the database -> Generating reports -> Saving to the data directory

Usage:
    1. Direct execution: python variable_report_pipeline.py
    2. External import: from variable_report_pipeline import VariableReportPipeline; pipeline = VariableReportPipeline(); pipeline.run()
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

# Load database and LLM configuration from app.config
DB_CONFIG = {
    'host': config.generating_database.host,
    'port': config.generating_database.port,
    'user': config.generating_database.user,
    'password': config.generating_database.password,
    'database': config.generating_database.database,
    'charset': config.generating_database.charset,
}
LLM_CONFIG = {
    'api_key': config.generating_llm.dashscope_api_key,
    'base_url': config.generating_llm.base_url,
    'model': config.generating_llm.dashscope_model,
    'temperature': config.generating_llm.temperature,
    'timeout': config.generating_llm.timeout,
}

# ==============================
# Built-in Configuration (No external input required)
# ==============================

# Working Directory (Defaults to current script path)
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

# Data Output Directory (Sibling to src)
DATA_DIR = os.path.join(WORK_DIR, "..", "data")

# ==============================
# Import Report Generation Modules
# ==============================

try:
    # Attempt to import Variable_Reporting module
    VARIABLE_REPORT_AVAILABLE = False

    # Add Variable_Reporting directory to sys.path
    _var_reporting_dir = os.path.join(_script_dir, 'Variable_Reporting')
    if _var_reporting_dir not in sys.path:
        sys.path.insert(0, _var_reporting_dir)

    try:
        from single_report_prepare import PerovskiteAnalyzer
        from single_report import ReportGenerator
        VARIABLE_REPORT_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️ Warning: Unable to import Variable_Reporting module. Error: {e}")

except Exception as e:
    VARIABLE_REPORT_AVAILABLE = False
    print(f"⚠️ Warning: Unable to load Variable_Reporting module, report generation functionality will be unavailable. Error: {e}")

# ==============================
# Core Class Encapsulation
# ==============================

class VariableReportPipeline:
    """Variable Report Automated Data Processing Pipeline"""

    def __init__(self,
                 db_config: Optional[Dict[str, Any]] = None,
                 llm_config: Optional[Dict[str, Any]] = None,
                 work_dir: Optional[str] = None):
        """
        Initialize the pipeline
        :param db_config: Database configuration (Optional, uses built-in config if not provided)
        :param llm_config: LLM configuration (Optional, uses built-in config if not provided)
        :param work_dir: Working directory (Optional, uses built-in config if not provided)
        """
        self.db_config = db_config if db_config else DB_CONFIG
        self.llm_config = llm_config if llm_config else LLM_CONFIG
        self.work_dir = work_dir if work_dir else WORK_DIR
        self.data_dir = DATA_DIR
        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def run(self, steps: str = 'all', rebuild_knowledge: bool = True, verbose: bool = True) -> bool:
        """
        Execute the report generation process
        :param steps: Steps to execute ('all', 'prepare', 'report')
        :param rebuild_knowledge: Whether to rebuild knowledge base (default True)
        :param verbose: Whether to print detailed logs
        :return: Success status
        """
        if not VARIABLE_REPORT_AVAILABLE:
            raise ImportError("Variable_Reporting module not found, unable to execute report generation.")

        try:
            # Step 1: Data preparation (mechanism analysis)
            if steps in ['all', 'prepare']:
                print(f"\n{'='*60}")
                print("📝 Starting data preparation (mechanism analysis)...")
                print(f"{'='*60}")

                analyzer = PerovskiteAnalyzer()
                result = analyzer.run(rebuild_knowledge=rebuild_knowledge)

                if verbose:
                    print(f"\n✅ Data preparation completed!")
                    print(f"📊 Statistics:")
                    print(f"   - Total tasks: {result.get('total_tasks', 0)}")
                    print(f"   - Success count: {result.get('success_count', 0)}")
                    print(f"   - Failed count: {result.get('failed_count', 0)}")
                    print(f"   - Dataset size: {result.get('dataset_size', 0)}")
                    print(f"   - Dataset path: {result.get('dataset_path', 'N/A')}")

                if result.get('success') is False:
                    print(f"\n⚠️ Data preparation stage failed: {result.get('reason', 'Unknown reason')}")
                    return False

            # Step 2: Report generation
            if steps in ['all', 'report']:
                print(f"\n{'='*60}")
                print("📝 Starting Variable report generation...")
                print(f"{'='*60}")

                generator = ReportGenerator()
                stats = generator.run()

                if verbose:
                    print(f"\n✅ Report generation completed!")
                    print(f"📊 Statistics:")
                    print(f"   - Total tasks: {stats.get('total', 0)}")
                    print(f"   - Matched: {stats.get('matched', 0)}")
                    print(f"   - Missing data: {stats.get('missing', 0)}")
                    print(f"   - Skipped: {stats.get('skipped', 0)}")

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
    print("📊 Variable Report Pipeline")
    print("=" * 60)

    # Direct execution, no parameters required
    pipeline = VariableReportPipeline()
    success = pipeline.run(steps='all', rebuild_knowledge=True, verbose=True)

    if not success:
        print("\n❌ Pipeline failed!")
        sys.exit(1)
    else:
        print("\n✅ All tasks completed!")
        