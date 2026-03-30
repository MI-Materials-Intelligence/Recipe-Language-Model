# -*- coding: utf-8 -*-
"""
Edge Report 数据自动化处理流水线
支持：DB 导出 -> 清洗去重 -> 结果回写 DB

使用方式:
    1. 直接运行：python this_script.py
    2. 外部调用：from this_script import EdgeReportPipeline; pipeline = EdgeReportPipeline(); pipeline.run_full_process(src_table="data50764", target_table="data50764_select")
"""

import os
import sys
from typing import Optional, Dict, Any

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
# 内置配置 (无需外部传入)
# ==============================

# 工作目录 (默认为当前脚本所在路径)
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据输出目录 (与 src 平级)
DATA_DIR = os.path.join(WORK_DIR, "..", "data")

# ==============================
# 导入 extractor
# ==============================

try:
    # 使用相对导入避免多进程环境下的路径问题
    from .extraction.edge_report_extractor import EdgeReportExtractor
    EXTRACTOR_AVAILABLE = True
except ImportError as e:
    EXTRACTOR_AVAILABLE = False
    print(f"⚠️ 警告：无法导入 EdgeReportExtractor，数据提取功能将不可用。错误：{e}")

# ==============================
# 核心类封装
# ==============================

class EdgeReportPipeline:
    """Edge Report 数据自动化处理流水线"""

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
        os.makedirs(self.work_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

        # 初始化数据提取器
        if EXTRACTOR_AVAILABLE:
            self.data_extractor = EdgeReportExtractor(self.db_config)

    def run_full_process(self, src_table: str) -> bool:
        """
        执行完整流程：导出 -> 清洗去重 -> 回写
        :param src_table: 源数据库表名
        :param target_table: 目标数据库表名
        :return: 是否成功
        """
        if not EXTRACTOR_AVAILABLE:
            raise ImportError("EdgeReportExtractor 模块未找到，无法执行数据提取。")

        try:
            # 使用 EdgeReportExtractor 进行完整处理，所有输出到 data 目录
            target_table = "data50764_select"
            self.data_extractor.extract_and_process(src_table, target_table, self.data_dir)

            print("\n🎉 全流程执行完毕！")
            return True

        except Exception as e:
            print(f"🛑 流程中断：{e}")
            return False


# ==============================
# 主入口 (脚本直接运行)
# ==============================

if __name__ == "__main__":
    print("=" * 60)
    print("📊 Edge Report 数据自动化处理流水线")
    print("=" * 60)
    print(f"📁 工作目录：{WORK_DIR}")
    print(f"🗄️  数据库：{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 60)

    # 初始化并执行
    pipeline = EdgeReportPipeline()
    success = pipeline.run_full_process(src_table="data50764", target_table="data50764_select")

    if not success:
        print("\n❌ 流程执行失败，请检查日志。")
        sys.exit(1)
    else:
        print("\n✅ 所有任务完成！")
