import os
import os.path as osp
import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import tomllib

# ===== Config Loader =====
def load_recipeqa_config():
    """Load RecipeQA configuration from config.toml"""
    try:
        # Project root: current file is in .../RecipeQA/src/, need to go back to OpenManus/
        # Path levels: src -> RecipeQA -> RLM -> tool -> app -> OpenManus (5 levels)
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
        config_path = project_root / "config" / "config.toml"

        if not config_path.exists():
            print(f"[WARN] Config file not found: {config_path}, using default values")
            return {}

        with config_path.open("rb") as f:
            config = tomllib.load(f)

        return config.get("recipeqa", {})
    except Exception as e:
        print(f"[WARN] Failed to load config: {e}, using default values")
        return {}

# Import two corpus generation modules
from .distillation.optimized import (
    get_tasks_from_db as optimized_get_tasks,
    read_json_file,
    read_files_by_extension,
    get_dataset,
    save_json_file,
    request_llm as optimized_request_llm,
    rebuild_mechanism_from_db
)
from .report_to_qa.single_v2_db import (
    get_tasks_from_db as single_get_tasks,
    read_json_file as single_read_json,
    read_files_by_extension as single_read_files,
    get_dataset as single_get_dataset,
    save_json_file as single_save_json,
    request_llm as single_request_llm,
    batch_update_status,
    rebuild_mechanism_from_db as single_rebuild_mechanism
)


class CorpusGenerator:
    """Unified Corpus Generation Coordinator"""

    def __init__(self, workspace_root: str = None):
        """
        Initialize corpus generator

        Args:
            workspace_root: Workspace root directory, default is RecipeQA directory
        """
        if workspace_root is None:
            # Default to use the project root directory where current file is located (RecipeQA)
            self.workspace_root = osp.dirname(osp.dirname(osp.abspath(__file__)))
        else:
            self.workspace_root = workspace_root

        self.data_dir = osp.join(self.workspace_root, "data")

        # Load database configuration from config file
        RECIPEQA_CONFIG = load_recipeqa_config()

        # Try to load from recipeqa configuration
        recipeqa_db = RECIPEQA_CONFIG.get("database", {})
        if recipeqa_db:
            self.db_config = recipeqa_db
        else:
            # Use main database configuration
            try:
                project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
                config_path = project_root / "config.toml"
                # print(f"[INFO] Config path111: {config_path}")
                if not config_path.exists():
                    # Try alternative path
                    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
                    config_path = project_root / "config" / "config.toml"
                
                if config_path.exists():
                    with config_path.open("rb") as f:
                        config = tomllib.load(f)
                    # First try recipeqa.database, then fallback to main database
                    recipeqa_db = config.get("recipeqa", {}).get("database", {})
                    if recipeqa_db:
                        self.db_config = recipeqa_db
                    else:
                        self.db_config = config.get("database", {})
            except Exception as e:
                print(f"[WARN] Failed to load config: {e}")
                pass

        # If still no configuration, use remote database default values
        if not hasattr(self, 'db_config') or not self.db_config:
            self.db_config = {
                'host': '223.76.236.170',
                'port': 13330,
                'user': 'root',
                'password': 'zkxjh800',
                'database': 'exp_data',
                'charset': 'utf8mb4'
            }

    async def generate_optimized_async(self, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate optimized formulation corpus - Async version

        Args:
            config: Optional configuration dictionary, can override default paths

        Returns:
            Generation result information
        """
        try:
            print(f"[INFO] Starting optimized corpus generation...")
            print(f"[INFO] Workspace root: {self.workspace_root}")

            # Configure paths
            mechanism_dir = osp.join(self.data_dir, "mechanism")
            task_save_path = osp.join(self.data_dir, "optimized_tasks_from_db.json")
            dist_save_root = osp.join(self.data_dir, "optimized")
            dataset_path = osp.join(self.data_dir, "dataset", "optimized_dataset.json")

            # Apply custom configuration (if any)
            if config:
                mechanism_dir = config.get("mechanism_dir", mechanism_dir)
                task_save_path = config.get("task_save_path", task_save_path)
                dist_save_root = config.get("dist_save_root", dist_save_root)
                dataset_path = config.get("dataset_path", dataset_path)

            # 0. Rebuild mechanism library from database
            print(f"[INFO] Rebuilding mechanism library from database...")
            rebuild_mechanism_from_db(mechanism_dir, self.db_config)
            
            # 1. Get tasks
            print(dist_save_root)
            all_record_ids = optimized_get_tasks(
                expert_data_root=mechanism_dir,
                save_path=task_save_path,
                num_thres=100,
                db_config=self.db_config
            )
            print(dist_save_root)

            # if not all_record_ids:
            #     msg = "[INFO] No tasks with status=0 for optimized corpus"
            #     print(msg)
            #     return msg

            # 2. Read tasks
            tasks = read_json_file(task_save_path)
            print(f"[INFO] tasks: {len(tasks)} | dist: {osp.abspath(dist_save_root)}")

            # 3. Async generation (direct await, don't use asyncio.run)
            success_ids = await optimized_request_llm(tasks, dist_save_root)

            # 4. Batch update status
            # batch_update_status(self.db_config, success_ids, status=1)
            # failed_ids = [rid for rid in all_record_ids if rid not in success_ids]
            # if failed_ids:
            #     batch_update_status(self.db_config, failed_ids, status=3)

            # 5. Build dataset
            dist_files = read_files_by_extension(dist_save_root, extensions=[".json"])
            print(f"[INFO] dist files: {len(dist_files)}")

            dataset = get_dataset(dist_save_root)
            save_json_file(dataset, dataset_path)
            print(f"[INFO] dataset size: {len(dataset)} -> {osp.abspath(dataset_path)}")

            return "Optimized corpus generated successfully"
        except Exception as e:
            error_msg = f"Error generating optimized corpus: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return error_msg

    async def generate_single_async(self, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate single variable corpus - Async version

        Args:
            config: Optional configuration dictionary, can override default paths

        Returns:
            Generation result information
        """
        try:
            print(f"[INFO] Starting single variable corpus generation...")
            print(f"[INFO] Workspace root: {self.workspace_root}")

            # Configure paths
            mechanism_dir = osp.join(self.data_dir, "mechanism")
            task_save_path = osp.join(self.data_dir, "tasks_from_db.json")
            dist_save_root = osp.join(self.data_dir, "..","..", "Generating", "data", "single")
            dataset_path = osp.join(self.data_dir, "single_var_dataset.json")

            # Apply custom configuration (if any)
            if config:
                mechanism_dir = config.get("mechanism_dir", mechanism_dir)
                task_save_path = config.get("task_save_path", task_save_path)
                dist_save_root = config.get("dist_save_root", dist_save_root)
                dataset_path = config.get("dataset_path", dataset_path)
            print(f"[INFO] Workspace1111 root: {dist_save_root}")
            
            # 0. Rebuild mechanism library from database
            print(f"[INFO] Rebuilding mechanism library from database...")
            single_rebuild_mechanism(mechanism_dir, self.db_config)
            
            # # 1. Get tasks
            # all_record_ids = single_get_tasks(
            #     expert_data_root=mechanism_dir,
            #     save_path=task_save_path,
            #     num_thres=100,
            #     db_config=self.db_config
            # )

            # if not all_record_ids:
            #     msg = "[INFO] No tasks with status=0 for single corpus"
            #     print(msg)
            #     return msg

            # # 2. Read tasks
            # tasks = single_read_json(task_save_path)
            # print(f"[INFO] tasks: {len(tasks)} | dist: {osp.abspath(dist_save_root)}")

            # # 3. Async generation (direct await, don't use asyncio.run)
            # success_ids = await single_request_llm(tasks, dist_save_root)

            # # 4. Batch update status
            # batch_update_status(self.db_config, success_ids, status=1)
            # failed_ids = [rid for rid in all_record_ids if rid not in success_ids]
            # if failed_ids:
            #     batch_update_status(self.db_config, failed_ids, status=3)

            # 5. Build dataset
            dist_files = single_read_files(dist_save_root, extensions=[".json"])
            print(f"[INFO] dist files: {len(dist_files)}")

            dataset = single_get_dataset(dist_save_root)
            single_save_json(dataset, dataset_path)
            print(f"[INFO] dataset size: {len(dataset)} -> {osp.abspath(dataset_path)}")

            return "Single variable corpus generated successfully"
        except Exception as e:
            error_msg = f"Error generating single variable corpus: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return error_msg

    async def generate_all_async(self, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate all corpora (optimized + single) - Async version

        Args:
            config: Optional configuration dictionary

        Returns:
            Generation result information
        """
        results = []

        # Generate optimized corpus and single corpus concurrently
        opt_task = self.generate_optimized_async(config)
        sng_task = self.generate_single_async(config)

        opt_result, sng_result = await asyncio.gather(opt_task, sng_task, return_exceptions=True)

        results.append(("Optimized", opt_result))
        results.append(("Single", sng_result))

        # Summarize results
        success_count = sum(1 for _, r in results if isinstance(r, str) and "successfully" in r.lower())
        total_count = len(results)

        summary = f"\n{'='*60}\n"
        summary += f"Corpus Generation Summary\n"
        summary += f"{'='*60}\n"
        for name, result in results:
            if isinstance(result, Exception):
                summary += f"❌ {name}: Error - {str(result)}\n"
            elif "successfully" in result.lower():
                summary += f"✅ {name}: {result}\n"
            else:
                summary += f"⚠️  {name}: {result}\n"
        summary += f"{'='*60}\n"
        summary += f"Total: {success_count}/{total_count} successful\n"

        return summary

    # Synchronous wrapper (for non-async environment)
    def generate_optimized(self, config: Optional[Dict[str, Any]] = None) -> str:
        """Synchronous version: Generate optimized formulation corpus"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is already running, create task and wait
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(self.generate_optimized_async(config), loop)
                return future.result(timeout=300)  # 5 minutes timeout
            else:
                return loop.run_until_complete(self.generate_optimized_async(config))
        except Exception as e:
            return f"Error generating optimized corpus: {str(e)}"

    def generate_single(self, config: Optional[Dict[str, Any]] = None) -> str:
        """Synchronous version: Generate single variable corpus"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(self.generate_single_async(config), loop)
                return future.result(timeout=300)
            else:
                return loop.run_until_complete(self.generate_single_async(config))
        except Exception as e:
            return f"Error generating single variable corpus: {str(e)}"

    def generate_all(self, config: Optional[Dict[str, Any]] = None) -> str:
        """Synchronous version: Generate all corpora"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(self.generate_all_async(config), loop)
                return future.result(timeout=600)  # 10 minutes timeout
            else:
                return loop.run_until_complete(self.generate_all_async(config))
        except Exception as e:
            return f"Error generating corpora: {str(e)}"


# Convenience function
def generate_corpora(corpora_type: str = "all", workspace_root: str = None,
                     config: Optional[Dict[str, Any]] = None) -> str:
    """
    Convenience function: Generate specified type of corpus

    Args:
        corpora_type: Corpus type ("optimized", "single", "all")
        workspace_root: Workspace root directory
        config: Optional configuration

    Returns:
        Generation result information
    """
    generator = CorpusGenerator(workspace_root)

    if corpora_type == "optimized":
        return generator.generate_optimized(config)
    elif corpora_type == "single":
        return generator.generate_single(config)
    elif corpora_type == "all":
        return generator.generate_all(config)
    else:
        return f"Unknown corpora type: {corpora_type}"
