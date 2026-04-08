# -*- coding: utf-8 -*-
"""
Characterisation Report Automated Processing Pipeline
Supports: Fetching pending data from the database -> Generating reports -> Saving to the data directory

Usage:
    1. Direct execution: python this_script.py
    2. External import: from this_script import CharacterisationReportPipeline; pipeline = CharacterisationReportPipeline(); pipeline.run()
"""

import os
import sys
from typing import Any, Dict, Optional


_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)


from seven_ai_layers_robotics.config import config


WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(WORK_DIR, "..", "data")


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

try:
   
    REPORT_GENERATORS = {}


    try:
        from characterization_reporting.sam_report import run_sam_report
        REPORT_GENERATORS['sam'] = run_sam_report
    except ImportError as e:
        print(f" Warning: Unable to import SAM report generator. Error: {e}")

  
    try:
        from characterization_reporting.add_report import run_add_report
        REPORT_GENERATORS['additive'] = run_add_report
    except ImportError as e:
        print(f"Warning: Unable to import Additive report generator. Error: {e}")

    
    try:
        from characterization_reporting.pass_report import run_pass_report
        REPORT_GENERATORS['passivator'] = run_pass_report
    except ImportError as e:
        print(f"Warning: Unable to import Passivator report generator. Error: {e}")

    
    try:
        from characterization_reporting.process_report import run_process_report
        REPORT_GENERATORS['process'] = run_process_report
    except ImportError as e:
        print(f"Warning: Unable to import Process report generator. Error: {e}")

    ARE_GENERATORS_AVAILABLE = len(REPORT_GENERATORS) > 0

except Exception as e:
    ARE_GENERATORS_AVAILABLE = False
    print(f"Warning: Unable to load report generators, report generation functionality will be unavailable. Error: {e}")



class CharacterisationReportPipeline:
    """Characterisation Report Automated Processing Pipeline.
    
    This class provides an automated pipeline for fetching pending data from the database,
    generating reports, and saving to the data directory.
    """

    def __init__(self,
                 db_config: Optional[Dict[str, Any]] = None,
                 llm_config: Optional[Dict[str, Any]] = None,
                 work_dir: Optional[str] = None):
        """Initialize the characterisation report pipeline.
        
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

    def run(self, report_type: str = 'all', verbose: bool = True) -> bool:
        """Execute the report generation process.
        
        Args:
            report_type: Report type ('sam', 'additive', 'passivator', 'process', or 'all').
            verbose: Whether to print detailed logs.
            
        Returns:
            bool: Success status of the pipeline execution.
        """
        if not ARE_GENERATORS_AVAILABLE:
            raise ImportError("Report generator modules not found, unable to execute report generation.")

        try:
            if report_type == 'all':
                
                for gen_type, generator_func in REPORT_GENERATORS.items():
                    print(f"\n{'='*60}")
                    print(f"Starting to generate {gen_type.upper()} type report...")
                    print(f"{'='*60}")

                    try:
                        generator_func(verbose=verbose)
                        print(f"{gen_type.upper()} type report generation completed!")
                    except Exception as e:
                        print(f"{gen_type.upper()} type report generation failed: {e}")
                        continue
            else:
                
                if report_type not in REPORT_GENERATORS:
                    raise ValueError(f"Unsupported report type: {report_type}, available types: {list(REPORT_GENERATORS.keys())}")

                print(f"\n{'='*60}")
                print(f"Starting to generate {report_type.upper()} type report...")
                print(f"{'='*60}")

                REPORT_GENERATORS[report_type](verbose=verbose)
                print(f"{report_type.upper()} type report generation completed!")

            print("\nEntire process completed!")
            return True

        except Exception as e:
            print(f"Process interrupted: {e}")
            import traceback
            traceback.print_exc()
            return False



if __name__ == "__main__":
    print("=" * 60)
    print("Characterisation Report Automated Processing Pipeline")
    print("=" * 60)
    print(f"Working Directory: {WORK_DIR}")
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"Data Output Directory: {DATA_DIR}")
    print("=" * 60)
    print(f"Available Report Generators: {list(REPORT_GENERATORS.keys())}")
    print("=" * 60)

    
    pipeline = CharacterisationReportPipeline()
    success = pipeline.run(report_type='all', verbose=True)

    if not success:
        print("\nProcess execution failed, please check logs.")
        sys.exit(1)
    else:
        print("\nAll tasks completed!")
