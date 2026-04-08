# -*- coding: utf-8 -*-
"""Edge Report Automated Data Processing Pipeline.

This module provides an automated pipeline for data cleaning, generating experimental
description reports, and calling DeepSeek for mechanism analysis.
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
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(WORK_DIR, "..", "data")

STEP_MODULES = {}
ARE_MODULES_AVAILABLE = False

try:
    from seven_ai_layers_robotics.generating.src.edge_reporting import edge_report_generator
    STEP_MODULES['step2'] = edge_report_generator
except ImportError as e:
    print(f"Warning: Unable to import edge_report_generator module. Error: {e}")

try:
    from seven_ai_layers_robotics.generating.src.edge_reporting import edge_mechanism_analyzer
    STEP_MODULES['step3'] = edge_mechanism_analyzer
except ImportError as e:
    print(f"Warning: Unable to import edge_mechanism_analyzer module. Error: {e}")

ARE_MODULES_AVAILABLE = len(STEP_MODULES) > 0

DEFAULT_DB_URI = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4"


class EdgeReportPipeline:
    """Edge Report Automated Data Processing Pipeline.
    
    This class provides an automated pipeline for data cleaning, generating experimental
    description reports, and calling DeepSeek for mechanism analysis.
    """

    def __init__(self,
                 db_uri: Optional[str] = None,
                 db_config: Optional[Dict[str, Any]] = None,
                 json_root_dir: Optional[str] = None,
                 work_dir: Optional[str] = None):
        """Initialize the edge report pipeline.
        
        Args:
            db_uri: Database URI string. Uses built-in config if not provided.
            db_config: Database configuration dictionary. Uses built-in config if not provided.
            json_root_dir: JSON root directory path. Uses built-in config if not provided.
            work_dir: Working directory path. Uses built-in config if not provided.
        """
        self.db_uri = db_uri if db_uri else DEFAULT_DB_URI
        self.db_config = db_config if db_config else DB_CONFIG
        self.json_root_dir = json_root_dir if json_root_dir else WORK_DIR
        self.work_dir = work_dir if work_dir else WORK_DIR
        self.data_dir = DATA_DIR

        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        self._setup_step2()
        self._setup_step3()

    def _setup_step2(self):
        """Configure Step 2 module"""
        if 'step2' not in STEP_MODULES:
            return

        s2 = STEP_MODULES['step2']
        s2.DB_URI = self.db_uri
        s2.DB_CONFIG = self.db_config

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
        s3.JSON_ROOT_DIR = os.path.join(self.data_dir)
        if hasattr(s3, 'API_URL'):
            s3.API_URL = s3.API_URL.strip()

    def run_step2(self, verbose: bool = True) -> None:
        """Execute Step 2 to generate experimental description report.
        
        Args:
            verbose: Whether to print detailed logs. Defaults to True.
        """
        if 'step2' not in STEP_MODULES:
            raise ImportError("edge_report_generator module not found")

        if verbose:
            print("Step 2: Generating experimental description report")

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

    def run_step3(self, verbose: bool = True) -> None:
        """Execute Step 3 to call DeepSeek for mechanism analysis.
        
        Args:
            verbose: Whether to print detailed logs. Defaults to True.
        """
        if 'step3' not in STEP_MODULES:
            raise ImportError("edge_mechanism_analyzer module not found")

        if verbose:
            print("Step 3: Calling DeepSeek to generate mechanism analysis")

        s3 = STEP_MODULES['step3']
        s3.main()

    def run(self, steps: str = 'all', verbose: bool = True) -> bool:
        """Execute the report generation pipeline.
        
        Args:
            steps: Steps to execute ('all', 'step1', 'step2', 'step3', or combinations like 'step1,step2').
            verbose: Whether to print detailed logs. Defaults to True.
            
        Returns:
            bool: True if pipeline executed successfully, False otherwise.
        """
        if not ARE_MODULES_AVAILABLE:
            raise ImportError("Step modules not found, unable to execute report generation.")

        try:
            if steps == 'all':
                step_list = ['step2', 'step3']
            else:
                step_list = [s.strip() for s in steps.split(',')]

            for step_name in step_list:
                if step_name == 'step2':
                    self.run_step2(verbose=verbose)
                elif step_name == 'step3':
                    self.run_step3(verbose=verbose)
                else:
                    print(f"Skipping unknown step: {step_name}")

            if verbose:
                print("\nEntire process completed!")
            return True

        except Exception as e:
            print(f"Process interrupted: {e}")
            return False


if __name__ == "__main__":
    print("=" * 60)
    print("Edge Report Automated Data Processing Pipeline")
    print("=" * 60)
    print(f"Working Directory: {WORK_DIR}")
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"Data Output Directory: {DATA_DIR}")
    print("=" * 60)
    print(f"Available Step Modules: {list(STEP_MODULES.keys())}")
    print("=" * 60)

    # Initialize and execute
    pipeline = EdgeReportPipeline()
    success = pipeline.run(steps='all', verbose=True)

    if not success:
        print("\nProcess execution failed, please check logs.")
        sys.exit(1)
    else:
        print("\nAll tasks completed!")
        