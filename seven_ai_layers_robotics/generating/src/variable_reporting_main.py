# -*- coding: utf-8 -*-
"""Variable Report Automated Data Processing Pipeline.

This module provides an automated pipeline for data preparation, generating
variable reports, and saving to the data directory.

Usage:
    1. Direct execution: python variable_reporting_main.py
    2. External import: from variable_reporting_main import VariableReportPipeline
"""

import os
import sys
from typing import Any, Dict, Optional

from seven_ai_layers_robotics.config import config


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
}


WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(WORK_DIR, "..", "data")

try:
    IS_VARIABLE_REPORT_AVAILABLE = False

    try:
        from seven_ai_layers_robotics.generating.src.variable_reporting.single_report_prepare import PerovskiteAnalyzer
        from seven_ai_layers_robotics.generating.src.variable_reporting.single_report import ReportGenerator
        IS_VARIABLE_REPORT_AVAILABLE = True
    except ImportError as e:
        print(f"Warning: Unable to import Variable_Reporting module. Error: {e}")

except Exception as e:
    IS_VARIABLE_REPORT_AVAILABLE = False
    print(f"Warning: Unable to load Variable_Reporting module, report generation functionality will be unavailable. Error: {e}")



class VariableReportPipeline:
    """Variable Report Automated Data Processing Pipeline.
    
    This class provides an automated pipeline for fetching pending data from the database,
    generating reports, and saving to the data directory.
    """

    def __init__(self,
                 db_config: Optional[Dict[str, Any]] = None,
                 llm_config: Optional[Dict[str, Any]] = None,
                 work_dir: Optional[str] = None):
        """Initialize the variable report pipeline.
        
        Args:
            db_config: Database configuration dictionary. Uses built-in config if not provided.
            llm_config: LLM configuration dictionary. Uses built-in config if not provided.
            work_dir: Working directory path. Uses built-in config if not provided.
        """
        self.db_config = db_config if db_config else DB_CONFIG
        self.llm_config = llm_config if llm_config else LLM_CONFIG
        self.work_dir = work_dir if work_dir else WORK_DIR
        self.data_dir = DATA_DIR
        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def run(self, steps: str = 'all', rebuild_knowledge: bool = True, verbose: bool = True) -> bool:
        """Execute the report generation process.
        
        Args:
            steps: Steps to execute ('all', 'prepare', 'report').
            rebuild_knowledge: Whether to rebuild knowledge base (default True).
            verbose: Whether to print detailed logs.
            
        Returns:
            Success status of the pipeline execution.
        """
        if not IS_VARIABLE_REPORT_AVAILABLE:
            raise ImportError("Variable_Reporting module not found, unable to execute report generation.")

        try:
            if steps in ['all', 'prepare']:
                print(f"\n{'='*60}")
                print("Starting data preparation (mechanism analysis)...")
                print(f"{'='*60}")

                analyzer = PerovskiteAnalyzer()
                result = analyzer.run(rebuild_knowledge=rebuild_knowledge)

                if result.get('success') is False:
                    print(f"\nData preparation stage failed: {result.get('reason', 'Unknown reason')}")
                    return False

                if verbose:
                    print(f"\nData preparation completed!")
                    print(f"Statistics:")
                    print(f"   - Total tasks: {result.get('total_tasks', 0)}")
                    print(f"   - Success count: {result.get('success_count', 0)}")
                    print(f"   - Failed count: {result.get('failed_count', 0)}")
                    print(f"   - Dataset size: {result.get('dataset_size', 0)}")
                    print(f"   - Dataset path: {result.get('dataset_path', 'N/A')}")

            # Step 2: Report generation
            if steps in ['all', 'report']:
                print(f"\n{'='*60}")
                print("Starting Variable report generation...")
                print(f"{'='*60}")

                generator = ReportGenerator()
                stats = generator.run()

                if verbose:
                    print(f"\nReport generation completed!")
                    print(f"Statistics:")
                    print(f"   - Total tasks: {stats.get('total', 0)}")
                    print(f"   - Matched: {stats.get('matched', 0)}")
                    print(f"   - Missing data: {stats.get('missing', 0)}")
                    print(f"   - Skipped: {stats.get('skipped', 0)}")

            print("\nEntire process completed!")
            return True

        except Exception as e:
            print(f"Process interrupted: {e}")
            return False




if __name__ == "__main__":
    print("=" * 60)
    print("Variable Report Pipeline")
    print("=" * 60)

    pipeline = VariableReportPipeline()
    success = pipeline.run(steps='all', rebuild_knowledge=True, verbose=True)

    if not success:
        print("\nPipeline failed!")
        sys.exit(1)
    else:
        print("\nAll tasks completed!")
        
