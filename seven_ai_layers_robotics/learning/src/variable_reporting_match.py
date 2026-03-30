# -*- coding: utf-8 -*-
"""
机器人学习数据自动化处理流水线
支持：DB 导出 -> Excel 转换 -> 算法匹配 -> 结果回写 DB -> 清理

使用方式:
    1. 直接运行：python this_script.py
    2. 外部调用：from this_script import RoboticDataPipeline; pipeline = RoboticDataPipeline(); pipeline.run_full_process(table_name="xxx")
"""

import os
import sys
import csv
import json
import shutil
import pandas as pd
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any

# ==============================
# 内置配置 (无需外部传入)
# ==============================

# 数据库配置
DB_CONFIG = {
    'host': '',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': '',
    'charset': 'utf8mb4'
}

# 工作目录 (默认为当前脚本所在路径的父目录)
WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据输出目录
DATA_DIR = os.path.join(WORK_DIR, "data")

# ==============================
# 导入 pipeline 函数和提取器
# ==============================

try:
    # 使用相对导入，避免多进程环境下的路径问题
    from .matching.single_var_matching_pipeline import run as single_var_matching_pipeline
    PIPELINE_AVAILABLE = True
except ImportError as e:
    PIPELINE_AVAILABLE = False
    print(f"⚠️ 警告：无法导入 single_var_matching_pipeline，匹配功能将不可用。错误：{e}")
except Exception as e:
    PIPELINE_AVAILABLE = False
    print(f"⚠️ 警告：无法加载 single_var_matching_pipeline，匹配功能将不可用。错误：{e}")

try:
    from .extraction.data_extractor import DataExtractor
    EXTRACTOR_AVAILABLE = True
except ImportError as e:
    EXTRACTOR_AVAILABLE = False
    print(f"⚠️ 警告：无法导入 DataExtractor，数据提取功能将不可用。错误：{e}")


# ==============================
# 核心类封装
# ==============================

class RoboticDataPipeline:
    """机器人学习数据自动化处理流水线"""

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
            self.data_extractor = DataExtractor(self.db_config)



    def run_matching_pipeline(self, xlsx_filename: str) -> bool:
        """执行外部匹配算法 Pipeline"""
        if not PIPELINE_AVAILABLE:
            raise ImportError("single_var_matching_pipeline 模块未找到，无法执行匹配。")
        try:
            print("🚀 启动 single_var_matching_pipeline...")
            # 在 data 目录中执行匹配
            single_var_matching_pipeline(self.data_dir, xlsx_filename)
            return True
        except Exception as e:
            print(f"❌ Pipeline 执行失败：{e}")
            return False

    # ==============================
    # JSON 处理内部方法
    # ==============================

    @staticmethod
    def _extract_id_from_sample_field(s: str) -> str:
        if not s or not isinstance(s, str):
            return ""
        return s.split(",")[0].strip()

    def _record_exists(self, cursor, sid1, sid2, reverse_diff_class, analysis_type) -> bool:
        query = """
        SELECT 1 FROM match_pair_copy1
        WHERE sample_id_1 = %s AND sample_id_2 = %s
          AND reverse_diff_class = %s AND analysis_type = %s
        LIMIT 1
        """
        cursor.execute(query, (sid1, sid2, reverse_diff_class, analysis_type))
        return cursor.fetchone() is not None

    def _insert_record(self, cursor, analysis_type, reverse_diff_class, sid1, sid2, ctrl_fab, tgt_fab, file_path, meta_info):
        query = """
        INSERT INTO match_pair_copy1
        (analysis_type, reverse_diff_class, sample_id_1, sample_id_2,
         control_device_fabrication, target_device_fabrication, json_file_path, meta_info)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        meta_json_str = json.dumps(meta_info, ensure_ascii=False)
        cursor.execute(query, (analysis_type, reverse_diff_class, sid1, sid2, ctrl_fab, tgt_fab, file_path, meta_json_str))

    def _process_json_file(self, file_path, cursor, stats):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ JSON 解析失败：{file_path} - {e}")
            return

        reverse_diff_class = data.get("reverse_diff_class", "")
        json_data = data.get("data", {})

        for pair_key, content in json_data.items():
            meta = content.get("Meta Info", {})
            inputs = content.get("Input", {})
            analysis_type = meta.get("Analysis_Type", "")
            raw_sid1 = meta.get("Sample_ID_1", "")
            raw_sid2 = meta.get("Sample_ID_2", "")

            sid1 = self._extract_id_from_sample_field(raw_sid1)
            sid2 = self._extract_id_from_sample_field(raw_sid2)

            if not sid1.isdigit() or not sid2.isdigit():
                continue

            ctrl_fab = inputs.get("control_device_fabrication", "").strip()
            tgt_fab = inputs.get("target_device_fabrication", "").strip()

            if self._record_exists(cursor, sid1, sid2, reverse_diff_class, analysis_type):
                stats['skipped'] += 1
            else:
                self._insert_record(cursor, analysis_type, reverse_diff_class, sid1, sid2, ctrl_fab, tgt_fab, file_path, meta)
                stats['inserted'] += 1

    def ingest_json_to_db(self, json_folder_path: Optional[str] = None, do_cleanup: bool = True) -> Dict[str, int]:
        """
        扫描 JSON 文件夹并插入数据库
        :param json_folder_path: JSON 结果目录，默认为 data_dir/fp/tasks
        :param do_cleanup: 是否在处理完成后清理中间文件
        :return: 统计字典 {'inserted': int, 'skipped': int}
        """
        if json_folder_path is None:
            json_folder_path = os.path.join(self.data_dir, "fp", "tasks")

        conn = None
        cursor = None
        stats = {'inserted': 0, 'skipped': 0}
        total_files = 0

        try:
            print("🔌 连接数据库...")
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            print(f"📂 开始扫描文件夹：{json_folder_path}")
            if not os.path.exists(json_folder_path):
                print(f"⚠️ 目录不存在：{json_folder_path}")
                return stats

            for root, _, files in os.walk(json_folder_path):
                for file in files:
                    if file.lower().endswith('.json'):
                        full_path = os.path.join(root, file)
                        total_files += 1
                        print(f"📄 处理：{full_path}")
                        self._process_json_file(full_path, cursor, stats)

            conn.commit()
            print("\n" + "="*50)
            print(f"✅ 扫描完成 {total_files} 个 JSON 文件")
            print(f"📊 实际插入新记录：{stats['inserted']}")
            print(f"⏭️  跳过重复记录：{stats['skipped']}")
            print("="*50)

            if do_cleanup:
                self.cleanup_intermediate_files()

            return stats

        except Error as e:
            print(f"❌ 数据库错误：{e}")
            if conn: conn.rollback()
            raise e
        except Exception as e:
            print(f"💥 其他错误：{e}")
            if conn: conn.rollback()
            raise e
        finally:
            if conn and conn.is_connected():
                if cursor: cursor.close()
                conn.close()
                print("🔌 数据库连接已关闭。")

    def cleanup_intermediate_files(self):
        """删除 data 目录中的中间文件和 fp 目录"""
        deleted = []

        # 删除 data 目录下的 fp 和 formula 目录
        fp_dir = os.path.join(self.data_dir, "fp")
        fp_dir2 = os.path.join(self.data_dir, "formula")
        if os.path.exists(fp_dir):
            try:
                shutil.rmtree(fp_dir)
                shutil.rmtree(fp_dir2)
                deleted.append(f"📁 删除目录：{fp_dir}")
                deleted.append(f"📁 删除目录：{fp_dir2}")
            except Exception as e:
                print(f"⚠️ 无法删除目录：{e}")

        # 删除 data 目录中的中间 CSV 文件
        intermediate_csvs = [
            "re_formula_remove_abnormal.csv",
            "re_formula_dedup.csv",
            "re_fp_dedup.csv",
            "re_no_dedup.csv",
            "temp_export.csv"
        ]

        for csv_file in intermediate_csvs:
            csv_path = os.path.join(self.data_dir, csv_file)
            if os.path.exists(csv_path):
                try:
                    os.remove(csv_path)
                    deleted.append(f"🗑️  删除文件：{csv_path}")
                except Exception as e:
                    print(f"⚠️ 无法删除 {csv_file}: {e}")

        # 删除生成的 Excel 文件（如果需要）
        # 注意：这里不删除输入的 xlsx 文件，只删除中间过程文件

        if deleted:
            print("\n🧹 清理完成:")
            for msg in deleted:
                print(f"  {msg}")
        else:
            print("ℹ️ 无中间文件需要清理。")

    def run_full_process(self, table_name: str, output_xlsx_name: Optional[str] = None) -> bool:
        """
        执行完整流程：导出 -> 转换 -> 匹配 -> 回写 -> 清理
        :param table_name: 源数据库表名
        :param output_xlsx_name: 输出的 Excel 文件名 (可选，默认使用表名.xlsx)
        :return: 是否成功
        """
        if not EXTRACTOR_AVAILABLE:
            raise ImportError("DataExtractor 模块未找到，无法执行数据提取。")

        if output_xlsx_name is None:
            output_xlsx_name = f"{table_name}.xlsx"

        # 所有中间文件都输出到 data 目录
        csv_file = os.path.join(self.data_dir, "temp_export.csv")
        xlsx_file = os.path.join(self.data_dir, output_xlsx_name)

        try:
            # Step 1 & 2: 使用 DataExtractor 进行导出和转换
            self.data_extractor.extract_and_convert(table_name, csv_file, xlsx_file)

            # Step 3: Pipeline
            if not self.run_matching_pipeline(output_xlsx_name):
                raise Exception("Pipeline 执行失败")

            # Step 4: Ingest
            json_folder = os.path.join(self.data_dir, "fp", "tasks")
            if os.path.exists(json_folder):
                print("\n📥 开始将 JSON 结果写入数据库...")
                self.ingest_json_to_db(json_folder_path=json_folder, do_cleanup=True)
            else:
                print(f"⚠️ JSON 结果目录不存在：{json_folder}")

            self.cleanup_intermediate_files()

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
    print("🤖 机器人学习数据自动化处理流水线")
    print("=" * 60)
    print(f"📁 工作目录：{WORK_DIR}")
    print(f"🗄️  数据库：{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 60)

    # 获取用户输入的表名
    # table_name = input("\n📋 请输入要处理的数据库表名：").strip()

    # if not table_name:
    #     print("❌ 表名不能为空，退出。")
    #     sys.exit(1)

    # 初始化并执行
    pipeline = RoboticDataPipeline()
    success = pipeline.run_full_process(table_name="data3000")

    if not success:
        print("\n❌ 流程执行失败，请检查日志。")
        sys.exit(1)
    else:
        print("\n✅ 所有任务完成！")
