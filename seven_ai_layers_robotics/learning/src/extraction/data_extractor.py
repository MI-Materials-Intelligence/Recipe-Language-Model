"""
Data Extractor
Responsible for exporting data from database and converting to Excel format
"""

import os
import csv
import pandas as pd
from typing import Dict, Any, Optional
import tomllib

from pathlib import Path
import sys

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]
PROJECT_PARENT = PROJECT_ROOT.parent
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))

from seven_ai_layers_robotics.config import config as app_config

def load_database_config() -> Dict[str, Any]:
    return {
        "host": app_config.learning_database.host,
        "port": app_config.learning_database.port,
        "user": app_config.learning_database.user,
        "password": app_config.learning_database.password,
        "database": app_config.learning_database.database,
        "charset": app_config.learning_database.charset,
    }


class DataExtractor:
    """Data Extractor - Handles database export and format conversion."""

    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """Initialize extractor.
        
        Args:
            db_config: Database configuration dictionary. If None, loads from config.toml.
        """
        self.db_config = db_config if db_config is not None else load_database_config()

    def export_table_to_csv_exclude_id(
        self, table_name: str, output_csv: str
    ) -> bool:
        """Export MySQL table to CSV (excluding id column).
        
        Args:
            table_name: Name of the database table to export.
            output_csv: Output CSV file path.
            
        Returns:
            True if successful, False if failed.
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
                print(f"Table `{table_name}` is empty.")
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
            print(f"Table `{table_name}` exported to `{output_csv}` ({row_count} rows, excluding 'id' column)")
            return True

        except Error as e:
            print(f"Export failed: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                if cursor: cursor.close()
                conn.close()

    def csv_to_xlsx(self, csv_path: str, xlsx_path: str) -> bool:
        """Convert CSV file to XLSX format.
        
        Args:
            csv_path: Input CSV file path.
            xlsx_path: Output XLSX file path.
            
        Returns:
            True if successful, False if failed.
        """
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            df.to_excel(xlsx_path, index=False, engine='openpyxl')
            print(f"Converted to Excel: {xlsx_path}")
            return True
        except Exception as e:
            print(f"CSV to XLSX conversion failed: {e}")
            return False

    def extract_and_convert(
        self, table_name: str, output_csv: str, output_xlsx: str
    ) -> bool:
        """Execute complete extraction and conversion workflow.
        
        Args:
            table_name: Database table name to extract.
            output_csv: Output CSV file path.
            output_xlsx: Output XLSX file path.
            
        Returns:
            True if successful.
            
        Raises:
            Exception: If export or conversion fails.
        """
        print("Exporting data from database...")
        if not self.export_table_to_csv_exclude_id(table_name, output_csv):
            raise Exception("Export failed")

        print("Converting to Excel format...")
        if not self.csv_to_xlsx(output_csv, output_xlsx):
            raise Exception("Conversion failed")

        return True
