# -*- coding: utf-8 -*-
"""
数据提取器
负责从数据库导出数据并转换为 Excel 格式
"""

import os
import csv
import pandas as pd
from typing import Dict, Any, Optional
import tomllib


def load_database_config() -> Dict[str, Any]:
    """
    从项目根目录的 config/config.toml 加载数据库配置

    Returns:
        Dict[str, Any]: 数据库配置字典
    """
    # 获取当前模块所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = None

    # 向上查找项目根目录的 config.toml
    for _ in range(5):
        potential_config = os.path.join(current_dir, '..', '..', '..', '..', 'config', 'config.toml')
        if os.path.exists(potential_config):
            config_path = potential_config
            break
        current_dir = os.path.dirname(current_dir)

    if not config_path or not os.path.exists(config_path):
        raise FileNotFoundError(
            "未找到 config/config.toml 配置文件。请确保文件存在于项目根目录的 config 目录下。"
        )

    with open(config_path, 'rb') as f:
        config = tomllib.load(f)

    return config.get('database', {})


class DataExtractor:
    """数据提取器 - 处理数据库导出和格式转换"""

    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """
        初始化提取器
        :param db_config: 数据库配置字典，如果为 None 则从 config.toml 加载
        """
        self.db_config = db_config if db_config is not None else load_database_config()

    def export_table_to_csv_exclude_id(self, table_name: str, output_csv: str) -> bool:
        """
        导出 MySQL 表为 CSV（排除 id 列）
        :param table_name: 表名
        :param output_csv: 输出 CSV 文件路径
        :return: 成功返回 True，失败返回 False
        """
        output_dir = os.path.dirname(output_csv)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        conn = None
        cursor = None
        try:
            import mysql.connector
            from mysql.connector import Error
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()

            if not rows:
                print(f"⚠️ 表 `{table_name}` 为空。")
                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                columns_info = cursor.fetchall()
                all_columns = [col['Field'] for col in columns_info]
            else:
                all_columns = list(rows[0].keys())

            data_columns = [col for col in all_columns if col.lower() != 'id']

            with open(output_csv, "w", encoding="utf-8", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data_columns, extrasaction='ignore')
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)

            row_count = len(rows) if rows else 0
            print(f"✅ 表 `{table_name}` 已导出为 `{output_csv}`（{row_count} 行，不含 'id' 列）")
            return True

        except Error as e:
            print(f"❌ 导出失败：{e}")
            return False
        finally:
            if conn and conn.is_connected():
                if cursor: cursor.close()
                conn.close()

    def csv_to_xlsx(self, csv_path: str, xlsx_path: str) -> bool:
        """
        将 CSV 转换为 XLSX
        :param csv_path: CSV 文件路径
        :param xlsx_path: XLSX 文件路径
        :return: 成功返回 True，失败返回 False
        """
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            df.to_excel(xlsx_path, index=False, engine='openpyxl')
            print(f"✅ 已转换为 Excel: {xlsx_path}")
            return True
        except Exception as e:
            print(f"❌ CSV 转 XLSX 失败：{e}")
            return False

    def extract_and_convert(self, table_name: str, output_csv: str, output_xlsx: str) -> bool:
        """
        执行完整的提取和转换流程
        :param table_name: 表名
        :param output_csv: CSV 输出路径
        :param output_xlsx: XLSX 输出路径
        :return: 成功返回 True，失败抛出异常
        """
        print("📤 正在从数据库导出数据...")
        if not self.export_table_to_csv_exclude_id(table_name, output_csv):
            raise Exception("导出失败")

        print("🔄 正在转换为 Excel 格式...")
        if not self.csv_to_xlsx(output_csv, output_xlsx):
            raise Exception("转换失败")

        return True
