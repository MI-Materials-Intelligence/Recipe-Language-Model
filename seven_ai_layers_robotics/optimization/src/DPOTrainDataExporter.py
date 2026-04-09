"""DPO training data exporter for optimization layer.

This module provides functionality to export report_optimised records from database
with status filtering and time-based filtering for DPO training dataset preparation.
"""

import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Any, Union

import pymysql
import requests
from seven_ai_layers_robotics.config import config


class DPOTrainDataExporter:
    """DPO training data exporter for optimization layer.
    
    This class exports report_optimised records from database with status filtering
    and time-based filtering for DPO training dataset preparation.
    
    Attributes:
        db_config: Database configuration dictionary.
        table_name: Source table name for export.
        output_dir: Default output directory for CSV files.
    """
    
    def __init__(
        self,
        table_name: str = "report_optimised",
        output_dir: Optional[str] = None,
    ) -> None:
        """Initialize the DPOTrainDataExporter.
        
        Args:
            table_name: Source table name. Default: report_optimised
            output_dir: Output directory for CSV files. Default: optimization/data
        """
        # Validate table_name against whitelist
        allowed_tables = {"report_optimised"}
        if table_name not in allowed_tables:
            raise ValueError(f"Invalid table_name: {table_name}. Allowed: {allowed_tables}")
        
        self.db_config = {
            'host': config.database.host,
            'port': config.database.port,
            'user': config.database.user,
            'password': config.database.password,
            'database': config.database.database,
            'charset': config.database.charset,
        }
        self.table_name = table_name
        self.output_dir = output_dir or str(Path(__file__).resolve().parent.parent / "data")
        
        # LLM API configuration (loaded from config.toml)
        self.llm_api_url = config.optimization_llm.base_url
        self.llm_model_name = config.optimization_llm.model
        self.llm_temperature = config.optimization_llm.temperature
        
        # Optimization API configuration (loaded from config.toml)
        self.optimization_api_base_url = config.optimization_api.base_url
        self.optimization_api_timeout = config.optimization_api.timeout
        
        # Training paths (loaded from config.toml)
        self.base_model_path = config.optimization_api.base_model_path
        self.dpo_train_config_template = config.optimization_api.dpo_train_config_template
        self.inference_config_template = config.optimization_api.inference_config_template

    @staticmethod
    def safe_json_loads(s: str) -> Optional[Any]:
        """Safely parse JSON string.
        
        Args:
            s: JSON string to parse.
            
        Returns:
            Parsed JSON object or None if invalid.
        """
        if not s or s.strip() == '':
            return None
        try:
            return json.loads(s)
        except (json.JSONDecodeError, TypeError):
            return None
    
    @staticmethod
    def safe_get(obj: Any, *keys: str) -> Any:
        """Safely get nested dictionary value.
        
        Args:
            obj: Dictionary object.
            *keys: Sequence of keys to traverse.
            
        Returns:
            Value at the nested key path or None if not found.
        """
        for key in keys:
            if isinstance(obj, dict) and key in obj:
                obj = obj[key]
            else:
                return None
        return obj

    def _process_row(self, row: Tuple) -> Tuple:
        """Process a single database row for export.
        
        Args:
            row: Database row tuple (ID, index, status, uploadtime, Score, question, mechanism, mechanism_reasoning).
            
        Returns:
            Processed row tuple (ID, Index, status, upload_time, Question, Score, Mechanism).
        """
        id_val, index_val, status_val, uploadtime_val, score_str, question, mechanism, mechanism_reasoning = row
        
        score_obj = self.safe_json_loads(score_str)
        overall_score = self.safe_get(score_obj, 'score', 'overall')
        
        combined_mechanism = f"<think>{mechanism_reasoning or ''}</think><answer>{mechanism or ''}</answer>"
        
        return (id_val, index_val, status_val, uploadtime_val, question, overall_score, combined_mechanism)

    def _prepare_training(
        self,
        csv_path: str,
        item_name: str = "test1",
        base_model_path: Optional[str] = None,
        dpo_train_config_template: Optional[str] = None,
        inference_config_template: Optional[str] = None,
    ) -> Optional[dict]:
        """Call training preparation API with exported CSV file.
        
        Args:
            csv_path: Path to the CSV file to upload.
            item_name: Training job identifier. Default: test1
            base_model_path: Path to base model on server. Default: None (uses config)
            dpo_train_config_template: Path to DPO training config template. Default: None (uses config)
            inference_config_template: Path to inference config template. Default: None (uses config)
            
        Returns:
            API response JSON if successful, None if failed.
        """
        # Use default configuration (can be overridden if needed)
        if base_model_path is None:
            base_model_path = self.base_model_path
        if dpo_train_config_template is None:
            dpo_train_config_template = self.dpo_train_config_template
        if inference_config_template is None:
            inference_config_template = self.inference_config_template
        
        # Build API URL
        api_url = f"{self.optimization_api_base_url}/prepare-training"
        
        if not os.path.exists(csv_path):
            return None
        
        data = {
            "item_name": item_name,
            "base_model_path": base_model_path,
            "DPO_train_config_template": dpo_train_config_template,
            "inference_config_template": inference_config_template
        }
        
        with open(csv_path, "rb") as f:
            files = {
                "corpora_info": ("report_optimised.csv", f, "text/csv")
            }
            
            try:
                response = requests.post(
                    api_url,
                    files=files,
                    data=data,
                    timeout=self.optimization_api_timeout,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, Exception):
                return None
    
    @staticmethod
    def extract_content(text: str) -> Tuple[str, str]:
        """Extract reasoning and answer content from text with think/answer tags.
        
        Args:
            text: Raw model output text.
            
        Returns:
            (reasoning_content, answer_content) tuple.
        """
        if text is None:
            return "", ""
        
        def _strip_tags(s: str) -> str:
            return re.sub(r"</?\s*(think|answer)\s*>", "", s, flags=re.IGNORECASE).strip()
        
        reasoning_content = ""
        answer_content = ""
        remaining = text
        
        # Extract think content
        think_matches = re.findall(r"<think>(.*?)</think>", remaining, flags=re.DOTALL | re.IGNORECASE)
        if think_matches:
            reasoning_content = _strip_tags("".join(think_matches))
            remaining = re.sub(r"<think>.*?</think>", "", remaining, flags=re.DOTALL | re.IGNORECASE)
        elif re.search(r"</think>", remaining, flags=re.IGNORECASE):
            m_close = re.search(r"</think>", remaining, flags=re.IGNORECASE)
            reasoning_content = _strip_tags(remaining[:m_close.start()])
            remaining = remaining[m_close.end():]
        elif re.search(r"<think>", remaining, flags=re.IGNORECASE):
            m_open = re.search(r"<think>", remaining, flags=re.IGNORECASE)
            reasoning_content = _strip_tags(remaining[m_open.end():])
            remaining = remaining[:m_open.start()]
        
        # Extract answer content
        answer_matches = re.findall(r"<answer>(.*?)</answer>", remaining, flags=re.DOTALL | re.IGNORECASE)
        if answer_matches:
            answer_content = _strip_tags("".join(answer_matches))
        elif re.search(r"</answer>", remaining, flags=re.IGNORECASE):
            m_close = re.search(r"</answer>", remaining, flags=re.IGNORECASE)
            answer_content = _strip_tags(remaining[:m_close.start()])
        elif re.search(r"<answer>", remaining, flags=re.IGNORECASE):
            m_open = re.search(r"<answer>", remaining, flags=re.IGNORECASE)
            answer_content = _strip_tags(remaining[m_open.end():])
        
        # If only reasoning exists, use remaining as answer
        if reasoning_content and not answer_content:
            leftover = _strip_tags(remaining)
            if leftover:
                answer_content = leftover
        
        # If both are empty, return raw text as reasoning
        if not reasoning_content and not answer_content:
            return text, ""
        
        return reasoning_content, answer_content
    
    def call_llm_api(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        timeout: int = 120
    ) -> Optional[str]:
        """Call LLM API to get response.
        
        Args:
            prompt: User prompt.
            model: Model name. Uses default if None.
            temperature: Temperature. Uses default if None.
            timeout: Request timeout in seconds.
            
        Returns:
            Model response content or None if failed.
        """
        model = model if model is not None else self.llm_model_name
        temperature = temperature if temperature is not None else self.llm_temperature
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(
                self.llm_api_url,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return content
            else:
                return None
                
        except requests.exceptions.Timeout:
            print(f"LLM API request timeout")
            return None
        except requests.exceptions.ConnectionError:
            print(f"LLM API connection error: Check if {self.llm_api_url} is reachable")
            return None
        except Exception as e:
            print(f"LLM API unknown error: {type(e).__name__}: {e}")
            return None
    
    def run_with_extract(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, str, str]:
        """Call LLM and parse think/answer tags.
        
        Args:
            system_prompt: System prompt.
            user_prompt: User prompt.
            model: Model name.
            temperature: Temperature.
            
        Returns:
            (raw_response, reasoning_content, answer_content) tuple.
        """
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        raw = self.call_llm_api(full_prompt, model=model, temperature=temperature)
        
        if raw is None:
            return "", "", ""
        
        reasoning, answer = self.extract_content(raw)
        
        if not answer.strip():
            answer = raw.strip()
        
        return raw, reasoning, answer
    
    def get_pending_questions(self, limit: int = 10) -> list:
        """Get pending questions from database.
        
        Args:
            limit: Maximum number of records to retrieve.
            
        Returns:
            List of (ID, question) tuples.
        """
        conn = None
        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            sql = """
            SELECT ID, question
            FROM report_optimised
            WHERE status = 2
              AND question IS NOT NULL
              AND question != ''
              AND (opt_mechanism IS NULL OR opt_mechanism = '')
            LIMIT %s
            """
            
            cursor.execute(sql, limit)
            rows = cursor.fetchall()
            
            return rows
            
        except Exception as e:
            print(f"Failed to read database: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def update_optimization_result(
        self,
        record_id: int,
        opt_mechanism: str,
        opt_mechanism_reasoning: str
    ) -> bool:
        """Update optimization results to database.
        
        Args:
            record_id: Record ID.
            opt_mechanism: Optimization answer (answer part).
            opt_mechanism_reasoning: Optimization reasoning (think part).
            
        Returns:
            True if successful, False otherwise.
        """
        conn = None
        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Convert text to valid JSON string
            opt_mechanism_json = json.dumps(opt_mechanism, ensure_ascii=False)
            opt_mechanism_reasoning_json = json.dumps(opt_mechanism_reasoning, ensure_ascii=False)
            
            sql = """
            UPDATE report_optimised
            SET opt_mechanism = %s,
                opt_mechanism_reasoning = %s
            WHERE ID = %s
            """
            
            cursor.execute(sql, (opt_mechanism_json, opt_mechanism_reasoning_json, record_id))
            conn.commit()
            
            return True
            
        except Exception as e:
            print(f"Failed to update database: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def process_single_question(
        self,
        record: dict,
        system_prompt: str = "You are an expert in perovskite materials."
    ) -> bool:
        """Process a single question record.
        
        Args:
            record: Dictionary containing ID and question.
            system_prompt: System prompt for LLM.
            
        Returns:
            True if successful, False otherwise.
        """
        record_id = record.get('ID')
        question = record.get('question', '')
        
        if not question:
            return False
        
        user_prompt = question
        
        raw_response, reasoning, answer = self.run_with_extract(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        if not raw_response:
            return False
        
        success = self.update_optimization_result(record_id, answer, reasoning)
        
        return success
    
    def optimize_questions(
        self,
        total_records: int = 10,
        system_prompt: str = "You are an expert in perovskite materials."
    ) -> int:
        """Batch optimize question records.
        
        Args:
            total_records: Maximum number of records to process.
            system_prompt: System prompt for LLM.
            
        Returns:
            Number of successfully processed records.
        """
        records = self.get_pending_questions(limit=total_records)
        
        if not records:
            return 0
        
        success_count = 0
        for record in records:
            success = self.process_single_question(record, system_prompt=system_prompt)
            if success:
                success_count += 1
        
        return success_count
    
    def run_pipeline(
        self,
        item_name: str = "api_test",
        call_training: bool = False,
        optimize_questions: bool = False,
        optimization_limit: int = 10,
        system_prompt: str = "You are an expert in perovskite materials."
    ) -> Optional[Path]:
        """Run complete optimization pipeline.
        
        Args:
            item_name: Item identifier for tracking and training job.
            call_training: Whether to call training preparation API.
            optimize_questions: Whether to optimize questions and write back to database.
            optimization_limit: Maximum number of questions to optimize.
            system_prompt: System prompt for LLM optimization.
            
        Returns:
            CSV file path if export successful, None otherwise.
        """
        csv_path = None
        
        # Step 1: Export data
        try:
            csv_path = self.export_data()
        except (ValueError, RuntimeError):
            return None
        
        if csv_path is None or not csv_path.exists():
            return None
        
        # Step 2: Call training preparation API
        if call_training:
            self._prepare_training(
                csv_path=csv_path,
                item_name=item_name
            )
        
        # Step 3: Optimize questions and write back to database
        if optimize_questions:
            self.optimize_questions(
                total_records=optimization_limit,
                system_prompt=system_prompt
            )
        
        return csv_path
    def export_data(
        self,
        min_export_count: int = 1,
        start_time: Optional[str] = None
    ) -> Optional[Path]:
        """Export report_optimised records with status=1, supporting time-based filtering.
        
        Args:
            min_export_count: Minimum record count required for export. Default: 1
            start_time: Filter records with uploadtime >= this value (ISO format). Default: None
            
        Returns:
            Path to exported CSV file if successful, None otherwise.
            
        Raises:
            ValueError: If record count is insufficient for export.
            Exception: If database operation fails.
        """
        raw_columns = ['`ID`', '`index`', '`status`', '`uploadtime`', '`Score`', '`question`', '`mechanism`', '`mechanism_reasoning`']
        new_headers = ['ID', 'Index', 'status', 'upload_time', 'Question', 'Score', 'Mechanism']
        
        # Validate table_name to prevent SQL injection
        allowed_tables = {"report_optimised"}
        if self.table_name not in allowed_tables:
            raise ValueError(f"Invalid table name: {self.table_name}")
        
        conn = None
        try:
            conn = pymysql.connect(**self.db_config)
            try:
                with conn.cursor() as cursor:
                    if start_time:
                        cursor.execute(
                            f"SELECT COUNT(*) FROM `{self.table_name}` WHERE `status` = %s AND `uploadtime` >= %s",
                            (1, start_time)
                        )
                    else:
                        cursor.execute(
                            f"SELECT COUNT(*) FROM `{self.table_name}` WHERE `status` = %s",
                            (1,)
                        )
                    count = cursor.fetchone()[0]
                    
                    if count < min_export_count:
                        raise ValueError(f"Insufficient records: {count} < {min_export_count}")
                    
                    # Define allowed columns to prevent SQL injection
                    allowed_columns = {
                        'ID': '`ID`',
                        'index': '`index`',
                        'status': '`status`',
                        'uploadtime': '`uploadtime`',
                        'Score': '`Score`',
                        'question': '`question`',
                        'mechanism': '`mechanism`',
                        'mechanism_reasoning': '`mechanism_reasoning`'
                    }
                    cols = ', '.join(allowed_columns[col.replace('`', '')] for col in raw_columns)
                    
                    if start_time:
                        sql = f"SELECT {cols} FROM `{self.table_name}` WHERE `status` = %s AND `uploadtime` >= %s"
                        cursor.execute(sql, (1, start_time))
                    else:
                        sql = f"SELECT {cols} FROM `{self.table_name}` WHERE `status` = %s"
                        cursor.execute(sql, (1,))
                    rows = cursor.fetchall()
                    
                processed = [self._process_row(r) for r in rows]
            finally:
                if conn:
                    conn.close()
            
            os.makedirs(self.output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = Path(self.output_dir) / f"status1_export_{timestamp}.csv"
            
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(new_headers)
                writer.writerows(processed)
            
            return csv_path
            
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to export data: {e}") from e


if __name__ == "__main__":
    exporter = DPOTrainDataExporter()
    
    csv_path = exporter.run_pipeline(
        item_name="test1",
        call_training=True,
        optimize_questions=True,
        optimization_limit=10,
        system_prompt="You are an expert in perovskite materials."
    )
    
    if csv_path:
        print(f"Pipeline completed: {csv_path}")
    else:
        print("Pipeline failed")
