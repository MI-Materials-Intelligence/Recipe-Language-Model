# -*- coding: utf-8 -*-
"""
表征数据自动化处理流水线
支持：PL SAM、Image Process、Additive XRD、Passivator XRD 数据提取 -> JSON 生成 -> 数据库插入

使用方式:
    1. 直接运行：python this_script.py
    2. 外部调用：from this_script import CharacterizationDataPipeline; pipeline = CharacterizationDataPipeline(); pipeline.run_all()
"""

import os
import sys
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import sys
import os

# ==============================
# 导入配置
# ==============================
# 从 app.config 加载数据库配置
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
# 内置配置
# ==============================

# 工作目录 (默认为当前脚本所在路径)
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据输出目录
DATA_DIR = os.path.join(WORK_DIR, "..", "data")

# ==============================
# 导入各个表征数据处理模块
# ==============================

try:
    # 使用绝对导入而非相对导入，避免多进程环境下的路径问题
    from .matching.pl_sam import run_pl_sam
    from .matching.image_process import run_image_process
    from .matching.additive_xrd import run_additive_xrd
    from .matching.passivator_xrd import run_passivator_xrd
    from .matching.insert_characterization_pairs import run as insert_pairs

    PL_SAM_AVAILABLE = True
    IMAGE_PROCESS_AVAILABLE = True
    ADDITIVE_XRD_AVAILABLE = True
    PASSIVATOR_XRD_AVAILABLE = True
    INSERT_PAIRS_AVAILABLE = True

except ImportError as e:
    print(f"⚠️ 警告：无法导入表征数据处理模块。错误：{e}")
    PL_SAM_AVAILABLE = False
    IMAGE_PROCESS_AVAILABLE = False
    ADDITIVE_XRD_AVAILABLE = False
    PASSIVATOR_XRD_AVAILABLE = False
    INSERT_PAIRS_AVAILABLE = False


# ==============================
# 核心类封装
# ==============================

class CharacterizationDataPipeline:
    """表征数据自动化处理流水线"""

    def __init__(self,
                 db_config: Optional[Dict[str, Any]] = None,
                 work_dir: Optional[str] = None):
        """
        初始化流水线
        :param db_config: 数据库配置 (可选，不传则使用内置配置)
        :param work_dir: 工作目录 (可选，不传则使用内置配置)
        """
        self.db_config = db_config if db_config else DB_CONFIG
        self.work_dir = work_dir if work_dir else WORK_DIR
        self.data_dir = DATA_DIR

        # 确保目录存在
        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        # 模块可用性状态
        self.module_status = {
            'pl_sam': PL_SAM_AVAILABLE,
            'image_process': IMAGE_PROCESS_AVAILABLE,
            'additive_xrd': ADDITIVE_XRD_AVAILABLE,
            'passivator_xrd': PASSIVATOR_XRD_AVAILABLE,
            'insert_pairs': INSERT_PAIRS_AVAILABLE,
        }

    def check_module_status(self) -> Dict[str, bool]:
        """检查各模块的可用性状态"""
        return self.module_status.copy()

    def run_pl_sam_pipeline(self, verbose: bool = True) -> bool:
        """执行 PL SAM 数据提取流程"""
        if not PL_SAM_AVAILABLE:
            print("❌ PL SAM 模块不可用")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print("🔬 开始处理 PL SAM 数据...")
                print("="*60)

            run_pl_sam(verbose=verbose)

            if verbose:
                print("✅ PL SAM 数据处理完成\n")

            return True

        except Exception as e:
            print(f"❌ PL SAM 处理失败：{e}")
            return False

    def run_image_process_pipeline(self, verbose: bool = True) -> bool:
        """执行 Image Process 数据提取流程"""
        if not IMAGE_PROCESS_AVAILABLE:
            print("❌ Image Process 模块不可用")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print("🖼️ 开始处理 Image Process 数据...")
                print("="*60)

            run_image_process(verbose=verbose)

            if verbose:
                print("✅ Image Process 数据处理完成\n")

            return True

        except Exception as e:
            print(f"❌ Image Process 处理失败：{e}")
            return False

    def run_additive_xrd_pipeline(self, verbose: bool = True) -> bool:
        """执行 Additive XRD 数据提取流程"""
        if not ADDITIVE_XRD_AVAILABLE:
            print("❌ Additive XRD 模块不可用")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print("🧪 开始处理 Additive XRD 数据...")
                print("="*60)

            run_additive_xrd(verbose=verbose)

            if verbose:
                print("✅ Additive XRD 数据处理完成\n")

            return True

        except Exception as e:
            print(f"❌ Additive XRD 处理失败：{e}")
            return False

    def run_passivator_xrd_pipeline(self, verbose: bool = True) -> bool:
        """执行 Passivator XRD 数据提取流程"""
        if not PASSIVATOR_XRD_AVAILABLE:
            print("❌ Passivator XRD 模块不可用")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print("🛡️ 开始处理 Passivator XRD 数据...")
                print("="*60)

            run_passivator_xrd(verbose=verbose)

            if verbose:
                print("✅ Passivator XRD 数据处理完成\n")

            return True

        except Exception as e:
            print(f"❌ Passivator XRD 处理失败：{e}")
            return False

    def run_database_insertion(self, verbose: bool = True) -> bool:
        """执行数据库插入流程"""
        if not INSERT_PAIRS_AVAILABLE:
            print("❌ 数据库插入模块不可用")
            return False

        try:
            if verbose:
                print("\n" + "="*60)
                print("💾 开始将表征数据对插入数据库...")
                print("="*60)

            insert_pairs(verbose=verbose)

            if verbose:
                print("✅ 数据库插入完成\n")

            return True

        except Exception as e:
            print(f"❌ 数据库插入失败：{e}")
            return False

    def run_full_process(self) -> bool:
        """
        执行完整流程：所有表征数据处理 + 数据库插入
        :return: 是否成功
        """
        try:
            # 执行所有表征数据处理流程和数据库插入
            results = self.run_all(
                include_pl_sam=True,
                include_image_process=True,
                include_additive_xrd=True,
                include_passivator_xrd=True,
                include_db_insertion=True,
                verbose=True
            )

            # 检查是否所有步骤都成功
            if all(results.values()):
                print("\n🎉 全流程执行完毕！")
                return True
            else:
                print("\n⚠️ 部分任务失败，请检查日志。")
                return False

        except Exception as e:
            print(f"🛑 流程中断：{e}")
            return False

    def run_all(self,
                include_pl_sam: bool = True,
                include_image_process: bool = True,
                include_additive_xrd: bool = True,
                include_passivator_xrd: bool = True,
                include_db_insertion: bool = True,
                verbose: bool = True) -> Dict[str, bool]:
        """
        执行完整的数据处理和入库流程
        :param include_pl_sam: 是否包含 PL SAM 处理
        :param include_image_process: 是否包含 Image Process 处理
        :param include_additive_xrd: 是否包含 Additive XRD 处理
        :param include_passivator_xrd: 是否包含 Passivator XRD 处理
        :param include_db_insertion: 是否包含数据库插入
        :param verbose: 是否打印详细日志
        :return: 各步骤执行结果字典
        """
        if verbose:
            print("\n" + "="*80)
            print("🚀 表征数据自动化处理流水线启动")
            print("="*80)
            print(f"📁 工作目录：{self.work_dir}")
            print(f"🗄️  数据库：{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
            print("="*80)

        results = {}

        # 执行各个表征数据处理流程
        if include_pl_sam:
            results['pl_sam'] = self.run_pl_sam_pipeline(verbose=verbose)

        if include_image_process:
            results['image_process'] = self.run_image_process_pipeline(verbose=verbose)

        if include_additive_xrd:
            results['additive_xrd'] = self.run_additive_xrd_pipeline(verbose=verbose)

        if include_passivator_xrd:
            results['passivator_xrd'] = self.run_passivator_xrd_pipeline(verbose=verbose)

        # 执行数据库插入
        if include_db_insertion:
            results['database_insertion'] = self.run_database_insertion(verbose=verbose)

        # 汇总结果
        if verbose:
            print("\n" + "="*80)
            print("📊 执行结果汇总")
            print("="*80)

            for step, success in results.items():
                status = "✅ 成功" if success else "❌ 失败"
                print(f"{status} - {step}")

            all_success = all(results.values())
            print("="*80)

            if all_success:
                print("🎉 所有任务完成！")
            else:
                print("⚠️ 部分任务失败，请检查日志。")
            print("="*80 + "\n")

        return results




# ==============================
# 主入口 (脚本直接运行)
# ==============================

if __name__ == "__main__":
    print("=" * 80)
    print("🤖 表征数据自动化处理流水线")
    print("=" * 80)
    print(f"📁 工作目录：{WORK_DIR}")
    print(f"🗄️  数据库：{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 80)

    # 初始化并执行
    pipeline = CharacterizationDataPipeline()
    success = pipeline.run_full_process()

    if not success:
        print("\n❌ 流程执行失败，请检查日志。")
        sys.exit(1)
    else:
        print("\n✅ 所有任务完成！")
