"""Characterization data processing pipeline.

This module orchestrates:
1. PL SAM pair extraction
2. Image Process pair extraction
3. Additive XRD pair extraction
4. Passivator XRD pair extraction
5. Pair insertion into the characterization match table
"""

import os
import sys
from typing import Any, Dict, Optional

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
    print(f"WARNING: Failed to load config, using empty database configuration. Error: {e}")
    DB_CONFIG = {
        'host': '',
        'port': 3306,
        'user': 'root',
        'password': '',
        'database': '',
        'charset': 'utf8mb4'
    }

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(WORK_DIR, "..", "data")

try:
    from .matching.characterisation_pl_sam import run_characterisation_pl_sam
    from .matching.characterisation_image_pvk import run_characterisation_image_pvk
    from .matching.additive_xrd import run_additive_xrd
    from .matching.passivator_xrd import run_passivator_xrd
    from .matching.insert_characterization_pairs import run as insert_pairs

    characterisation_pl_sam_AVAILABLE = True
    characterisation_image_pvk_AVAILABLE = True
    ADDITIVE_XRD_AVAILABLE = True
    PASSIVATOR_XRD_AVAILABLE = True
    INSERT_PAIRS_AVAILABLE = True

except ImportError as e:
    print(f"WARNING: Unable to import characterization data processing modules. Error: {e}")
    characterisation_pl_sam_AVAILABLE = False
    characterisation_image_pvk_AVAILABLE = False
    ADDITIVE_XRD_AVAILABLE = False
    PASSIVATOR_XRD_AVAILABLE = False
    INSERT_PAIRS_AVAILABLE = False


class CharacterizationDataPipeline:
    """Pipeline orchestrator for characterization data processing."""

    def __init__(
        self,
        db_config: Optional[Dict[str, Any]] = None,
        work_dir: Optional[str] = None,
    ):
        """Initialize the pipeline instance.

        Args:
            db_config: Database configuration. Defaults to ``DB_CONFIG``.
            work_dir: Working directory path. Defaults to ``WORK_DIR``.
        """
        self.db_config = db_config if db_config else DB_CONFIG
        self.work_dir = work_dir if work_dir else WORK_DIR
        self.data_dir = DATA_DIR

        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        self.module_status = {
            'characterisation_pl_sam': characterisation_pl_sam_AVAILABLE,
            'characterisation_image_pvk': characterisation_image_pvk_AVAILABLE,
            'additive_xrd': ADDITIVE_XRD_AVAILABLE,
            'passivator_xrd': PASSIVATOR_XRD_AVAILABLE,
            'insert_pairs': INSERT_PAIRS_AVAILABLE,
        }

    def check_module_status(self) -> Dict[str, bool]:
        """Return availability status for each processing module.

        Returns:
            A mapping from module name to availability flag.
        """
        return self.module_status.copy()

    def run_characterisation_pl_sam_pipeline(self, verbose: bool = True) -> bool:
        """Run the PL SAM extraction pipeline.

        Args:
            verbose: Whether to print progress logs.

        Returns:
            ``True`` if execution succeeds, otherwise ``False``.
        """
        if not characterisation_pl_sam_AVAILABLE:
            print(" PL SAM module not available")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print(" Starting PL SAM data processing...")
                print("="*60)

            run_characterisation_pl_sam(verbose=verbose)

            if verbose:
                print("PL SAM data processing completed\n")

            return True

        except Exception as e:
            print(f"PL SAM processing failed: {e}")
            return False

    def run_characterisation_image_pvk_pipeline(self, verbose: bool = True) -> bool:
        """Run the Image Process extraction pipeline.

        Args:
            verbose: Whether to print progress logs.

        Returns:
            ``True`` if execution succeeds, otherwise ``False``.
        """
        if not characterisation_image_pvk_AVAILABLE:
            print(" Image Process module not available")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print(" Starting Image Process data processing...")
                print("="*60)

            run_characterisation_image_pvk(verbose=verbose)

            if verbose:
                print("Image Process data processing completed\n")

            return True

        except Exception as e:
            print(f"Image Process processing failed: {e}")
            return False

    def run_additive_xrd_pipeline(self, verbose: bool = True) -> bool:
        """Run the Additive XRD extraction pipeline.

        Args:
            verbose: Whether to print progress logs.

        Returns:
            ``True`` if execution succeeds, otherwise ``False``.
        """
        if not ADDITIVE_XRD_AVAILABLE:
            print(" Additive XRD module not available")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print(" Starting Additive XRD data processing...")
                print("="*60)

            run_additive_xrd(verbose=verbose)

            if verbose:
                print("Additive XRD data processing completed\n")

            return True

        except Exception as e:
            print(f"Additive XRD processing failed: {e}")
            return False

    def run_passivator_xrd_pipeline(self, verbose: bool = True) -> bool:
        """Run the Passivator XRD extraction pipeline.

        Args:
            verbose: Whether to print progress logs.

        Returns:
            ``True`` if execution succeeds, otherwise ``False``.
        """
        if not PASSIVATOR_XRD_AVAILABLE:
            print(" Passivator XRD module not available")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print(" Starting Passivator XRD data processing...")
                print("="*60)

            run_passivator_xrd(verbose=verbose)

            if verbose:
                print("Passivator XRD data processing completed\n")

            return True

        except Exception as e:
            print(f"Passivator XRD processing failed: {e}")
            return False

    def run_database_insertion(self, verbose: bool = True) -> bool:
        """Run database insertion for generated characterization pairs.

        Args:
            verbose: Whether to print progress logs.

        Returns:
            ``True`` if execution succeeds, otherwise ``False``.
        """
        if not INSERT_PAIRS_AVAILABLE:
            print(" Database insertion module not available")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print(" Starting characterization data pair insertion to database...")
                print("="*60)

            insert_pairs(verbose=verbose)

            if verbose:
                print("Database insertion completed\n")

            return True

        except Exception as e:
            print(f"Database insertion failed: {e}")
            return False

    def run_full_process(self) -> bool:
        """Run the full workflow.

        The workflow includes all extraction steps and database insertion.

        Returns:
            ``True`` if all enabled steps succeed, otherwise ``False``.
        """
        try:
            results = self.run_all(
                include_characterisation_pl_sam=True,
                include_characterisation_image_pvk=True,
                include_additive_xrd=True,
                include_passivator_xrd=True,
                include_db_insertion=True,
                verbose=True
            )

            if all(results.values()):
                print("\nFull workflow completed successfully!")
                return True
            else:
                print("\nSome tasks failed, please check logs.")
                return False

        except Exception as e:
            print(f"Workflow interrupted: {e}")
            return False

    def run_all(
        self,
        include_characterisation_pl_sam: bool = True,
        include_characterisation_image_pvk: bool = True,
        include_additive_xrd: bool = True,
        include_passivator_xrd: bool = True,
        include_db_insertion: bool = True,
        verbose: bool = True,
    ) -> Dict[str, bool]:
        """Run selected workflow steps and return per-step results.

        Args:
            include_characterisation_pl_sam: Whether to run PL SAM processing.
            include_characterisation_image_pvk: Whether to run Image Process processing.
            include_additive_xrd: Whether to run Additive XRD processing.
            include_passivator_xrd: Whether to run Passivator XRD processing.
            include_db_insertion: Whether to run database insertion.
            verbose: Whether to print detailed logs.

        Returns:
            A mapping from step name to execution result.
        """
        if verbose:
            print("\n" + "="*80)
            print("Characterization Data Automated Processing Pipeline Starting")
            print("="*80)
            print(f"Working Directory: {self.work_dir}")
            print(f"Database: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
            print("="*80)

        results = {}

        if include_characterisation_pl_sam:
            results['characterisation_pl_sam'] = self.run_characterisation_pl_sam_pipeline(verbose=verbose)

        if include_characterisation_image_pvk:
            results['characterisation_image_pvk'] = self.run_characterisation_image_pvk_pipeline(verbose=verbose)

        if include_additive_xrd:
            results['additive_xrd'] = self.run_additive_xrd_pipeline(verbose=verbose)

        if include_passivator_xrd:
            results['passivator_xrd'] = self.run_passivator_xrd_pipeline(verbose=verbose)

        if include_db_insertion:
            results['database_insertion'] = self.run_database_insertion(verbose=verbose)

        if verbose:
            print("\n" + "="*80)
            print("Execution Results Summary")
            print("="*80)

            for step, success in results.items():
                status = "Success" if success else "Failed"
                print(f"{status} - {step}")

            all_success = all(results.values())
            print("="*80)

            if all_success:
                print("All tasks completed!")
            else:
                print("Some tasks failed, please check logs.")
            print("="*80 + "\n")

        return results


if __name__ == "__main__":
    print("=" * 80)
    print("Characterization Data Automated Processing Pipeline")
    print("=" * 80)
    print(f"Working Directory: {WORK_DIR}")
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 80)

    pipeline = CharacterizationDataPipeline()
    success = pipeline.run_full_process()

    if not success:
        print("\nWorkflow execution failed, please check logs.")
        sys.exit(1)
    else:
        print("\nAll tasks completed!")
