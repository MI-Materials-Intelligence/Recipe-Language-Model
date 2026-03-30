import os
import os.path as osp
import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import tomllib

# ===== Config Loader =====
def load_recipeqa_config():
    """从 config.toml 加载 RecipeQA 配置"""
    try:
        # 项目根目录：当前文件位于 .../RecipeQA/src/，需要回到 OpenManus/
        # 路径层级：src -> RecipeQA -> RLM -> tool -> app -> OpenManus (5 层)
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

# 导入两个语料生成模块
from .distillation.optimized import (
    get_tasks_from_db as optimized_get_tasks,
    read_json_file,
    read_files_by_extension,
    get_dataset,
    save_json_file,
    request_llm as optimized_request_llm
)
from .report_to_qa.single_v2_db import (
    get_tasks_from_db as single_get_tasks,
    read_json_file as single_read_json,
    read_files_by_extension as single_read_files,
    get_dataset as single_get_dataset,
    save_json_file as single_save_json,
    request_llm as single_request_llm,
    batch_update_status
)


class CorpusGenerator:
    """统一语料生成协调器"""

    def __init__(self, workspace_root: str = None):
        """
        初始化语料生成器

        Args:
            workspace_root: 工作空间根目录，默认为 RecipeQA 目录
        """
        if workspace_root is None:
            # 默认使用当前文件所在项目的根目录（RecipeQA）
            self.workspace_root = osp.dirname(osp.dirname(osp.abspath(__file__)))
        else:
            self.workspace_root = workspace_root

        self.data_dir = osp.join(self.workspace_root, "data")

        # 从配置文件加载数据库配置
        RECIPEQA_CONFIG = load_recipeqa_config()

        # 尝试从 recipeqa 配置加载
        recipeqa_db = RECIPEQA_CONFIG.get("database", {})
        if recipeqa_db:
            self.db_config = recipeqa_db
        else:
            # 使用主数据库配置
            try:
                project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
                config_path = project_root / "config" / "config.toml"

                if config_path.exists():
                    with config_path.open("rb") as f:
                        config = tomllib.load(f)
                    self.db_config = config.get("database", {})
            except:
                pass

        # 如果还是没有配置，使用默认值
        if not hasattr(self, 'db_config') or not self.db_config:
            self.db_config = {
                'host': '',
                'port': 13330,
                'user': 'root',
                'password': '',
                'database': '',
                'charset': 'utf8mb4'
            }

    async def generate_optimized_async(self, config: Optional[Dict[str, Any]] = None) -> str:
        """
        生成优化配方语料（optimized corpus）- 异步版本

        Args:
            config: 可选的配置字典，可覆盖默认路径

        Returns:
            生成结果信息
        """
        try:
            print(f"[INFO] Starting optimized corpus generation...")
            print(f"[INFO] Workspace root: {self.workspace_root}")

            # 配置路径
            mechanism_dir = osp.join(self.data_dir, "mechanism")
            task_save_path = osp.join(self.data_dir, "optimized_tasks_from_db.json")
            dist_save_root = osp.join(self.data_dir, "optimized")
            dataset_path = osp.join(self.data_dir, "dataset", "optimized_dataset.json")

            # 应用自定义配置（如果有）
            if config:
                mechanism_dir = config.get("mechanism_dir", mechanism_dir)
                task_save_path = config.get("task_save_path", task_save_path)
                dist_save_root = config.get("dist_save_root", dist_save_root)
                dataset_path = config.get("dataset_path", dataset_path)

            # 1. 获取任务
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

            # 2. 读取任务
            tasks = read_json_file(task_save_path)
            print(f"[INFO] tasks: {len(tasks)} | dist: {osp.abspath(dist_save_root)}")

            # 3. 异步生成（直接 await，不使用 asyncio.run）
            success_ids = await optimized_request_llm(tasks, dist_save_root)

            # 4. 批量更新状态
            # batch_update_status(self.db_config, success_ids, status=1)
            # failed_ids = [rid for rid in all_record_ids if rid not in success_ids]
            # if failed_ids:
            #     batch_update_status(self.db_config, failed_ids, status=3)

            # 5. 构建数据集
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
        生成单变量语料（single variable corpus）- 异步版本

        Args:
            config: 可选的配置字典，可覆盖默认路径

        Returns:
            生成结果信息
        """
        try:
            print(f"[INFO] Starting single variable corpus generation...")
            print(f"[INFO] Workspace root: {self.workspace_root}")

            # 配置路径
            mechanism_dir = osp.join(self.data_dir, "mechanism")
            task_save_path = osp.join(self.data_dir, "tasks_from_db.json")
            dist_save_root = osp.join(self.data_dir, "..","..", "Generating", "data", "single")
            dataset_path = osp.join(self.data_dir, "single_var_dataset.json")

            # 应用自定义配置（如果有）
            if config:
                mechanism_dir = config.get("mechanism_dir", mechanism_dir)
                task_save_path = config.get("task_save_path", task_save_path)
                dist_save_root = config.get("dist_save_root", dist_save_root)
                dataset_path = config.get("dataset_path", dataset_path)
            print(f"[INFO] Workspace1111 root: {dist_save_root}")
            # # 1. 获取任务
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

            # # 2. 读取任务
            # tasks = single_read_json(task_save_path)
            # print(f"[INFO] tasks: {len(tasks)} | dist: {osp.abspath(dist_save_root)}")

            # # 3. 异步生成（直接 await，不使用 asyncio.run）
            # success_ids = await single_request_llm(tasks, dist_save_root)

            # # 4. 批量更新状态
            # batch_update_status(self.db_config, success_ids, status=1)
            # failed_ids = [rid for rid in all_record_ids if rid not in success_ids]
            # if failed_ids:
            #     batch_update_status(self.db_config, failed_ids, status=3)

            # 5. 构建数据集
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
        生成所有语料（optimized + single）- 异步版本

        Args:
            config: 可选的配置字典

        Returns:
            生成结果信息
        """
        results = []

        # 并发生成 optimized corpus 和 single corpus
        opt_task = self.generate_optimized_async(config)
        sng_task = self.generate_single_async(config)

        opt_result, sng_result = await asyncio.gather(opt_task, sng_task, return_exceptions=True)

        results.append(("Optimized", opt_result))
        results.append(("Single", sng_result))

        # 汇总结果
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

    # 同步包装器（用于非异步环境）
    def generate_optimized(self, config: Optional[Dict[str, Any]] = None) -> str:
        """同步版本：生成优化配方语料"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已经在运行，创建任务并等待
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(self.generate_optimized_async(config), loop)
                return future.result(timeout=300)  # 5 分钟超时
            else:
                return loop.run_until_complete(self.generate_optimized_async(config))
        except Exception as e:
            return f"Error generating optimized corpus: {str(e)}"

    def generate_single(self, config: Optional[Dict[str, Any]] = None) -> str:
        """同步版本：生成单变量语料"""
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
        """同步版本：生成所有语料"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                future = asyncio.run_coroutine_threadsafe(self.generate_all_async(config), loop)
                return future.result(timeout=600)  # 10 分钟超时
            else:
                return loop.run_until_complete(self.generate_all_async(config))
        except Exception as e:
            return f"Error generating corpora: {str(e)}"


# 便捷函数
def generate_corpora(corpora_type: str = "all", workspace_root: str = None,
                     config: Optional[Dict[str, Any]] = None) -> str:
    """
    便捷函数：生成指定类型的语料

    Args:
        corpora_type: 语料类型 ("optimized", "single", "all")
        workspace_root: 工作空间根目录
        config: 可选配置

    Returns:
        生成结果信息
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
