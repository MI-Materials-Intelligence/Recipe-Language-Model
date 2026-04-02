import json
import os
import re
import sys
import threading
import traceback
from concurrent import futures
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to Python path
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))

# Add Evaluation src directory to Python path for recipe_recommendation module
evaluation_src = Path(__file__).resolve().parent.parent / "Evaluation" / "src"
sys.path.insert(0, str(evaluation_src))

import pandas as pd
import pymysql
import requests
from openai import OpenAI
from seven_ai_layers_robotics.config import config
from seven_ai_layers_robotics.reasoning.src.prompts import ReportPrompts
from seven_ai_layers_robotics.reasoning.src.totext_db import get_random_row_from_db, row_to_text, get_all_rows_from_db

class PerovskiteReportGenerator:
    """Perovskite solar cell report generator using large language models.

    This class generates scientific reports for perovskite solar cell research
    by analyzing material formulations and processing parameters.

    Attributes:
        base_url: Base URL for the local LLM API.
        dashscope_client: DashScope API client for fallback.
        db_config: Database configuration for input data.
        output_db_config: Database configuration for output storage.
        expected_fields: Expected field names for data processing.
    """

    @classmethod
    def from_config(cls):
        """Create an instance from app.config module.

        This method loads configuration from the project's central config,
        making it easy to manage settings without code changes.

        Returns:
            PerovskiteReportGenerator instance configured with app settings.

        Example:
            >>> generator = PerovskiteReportGenerator.from_config()
            >>> generator.run_once(total_runs=15)
        """
        # Load configuration from app.config
        db_config = {
            'host': config.reasoning_database.host,
            'user': config.reasoning_database.user,
            'password': config.reasoning_database.password,
            'database': config.reasoning_database.database,
            'port': config.reasoning_database.port,
            'table': config.reasoning_database.table
        }

        # Extract output database config
        output_db_config = {
            'host': config.reasoning_output_database.host,
            'user': config.reasoning_output_database.user,
            'password': config.reasoning_output_database.password,
            'database': config.reasoning_output_database.database,
            'port': config.reasoning_output_database.port,
        }

        # Extract LLM config
        base_url = config.reasoning_llm.base_url
        dashscope_api_key = config.reasoning_llm.dashscope_api_key

        return cls(
            base_url=base_url,
            dashscope_api_key=dashscope_api_key,
            db_config=db_config,
            output_db_config=output_db_config
        )

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        dashscope_api_key: str = "sk-your-api-key-here",
        db_config: Optional[Dict[str, Any]] = None,
        output_db_config: Optional[Dict[str, Any]] = None,
        expected_fields: Optional[List[str]] = None,
    ) -> None:
        """Initialize the PerovskiteReportGenerator.

        Args:
            base_url: Base URL for local LLM API service. Default: http://localhost:8000
            dashscope_api_key: API key for DashScope service. Default: sk-your-api-key-here
            db_config: Database configuration dict with host, user, password, database, port, table.
                      If None, uses default localhost settings.
            output_db_config: Output database configuration dict. If None, uses same as db_config.
            expected_fields: List of expected field names for data processing.
        """
        self.base_url = base_url.rstrip("/")
        self.dashscope_client = OpenAI(
            api_key=dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'exp_data',
            'port': 3306,
            'table': 'experiments_data_daily',
        }
        self.output_db_config = output_db_config or {
            'host': self.db_config['host'],
            'user': self.db_config['user'],
            'password': self.db_config['password'],
            'database': self.db_config['database'],
            'port': self.db_config['port'],
        }

        # Field definitions
        self.expected_fields = expected_fields or [
            "Formula PVK",
            "Concentration PVK",
            "Formula Additive 1",
            "Concentration Additive 1",
            "Formula Additive 2",
            "Concentration Additive 2",
            "Formula Additive 3",
            "Concentration Additive 3",
            "Formula SAM 1",
            "Concentration SAM 1",
            "Formula SAM 2",
            "Concentration SAM 2",
            "Formula SAM 3",
            "Concentration SAM 3",
            "Spin Coating Speed PVK 1",
            "Spin Coating Time PVK 1",
            "Spin Coating Speed PVK 2",
            "Spin Coating Time PVK 2",
            "Antisolvent Dropping Timing",
            "Antisolvent Volume (μL)",
            "Annealed Temperature PVK",
            "Annealed Time PVK",
            "Formula Passivator 1",
            "Concentration Passivator 1",
            "Formula Passivator 2",
            "Concentration Passivator 2",
            "Formula Passivator 3",
            "Concentration Passivator 3",
            "Spin Coating Speed Passivator",
            "Spin Coating Time Passivator",
            "Passivator Dropping Timing",
            "Passivator Volume (μL)",
            "Annealed Temperature Passivator",
            "Annealed Time Passivator",
            "PCE",
            "FF",
            "Voc",
            "Jsc",
        ]

    def _extract_content(self, text: str) -> Tuple[str, str]:
        """Extract reasoning and answer content from text with think/answer tags.

        This method robustly handles various tag completion scenarios including
        missing opening or closing tags.

        Args:
            text: Raw model output text potentially containing <think> and <answer> tags.

        Returns:
            A tuple of (reasoning_content, answer_content). If no tags found,
            returns (raw_text, "").
        """

        if text is None:
            return "", ""

        raw = text

        def _strip_tags(s: str) -> str:
            """Strip think/answer tags from text (case-insensitive)."""
            return re.sub(r"</?\s*(think|answer)\s*>", "", s, flags=re.IGNORECASE).strip()

        reasoning_content = ""
        answer_content = ""
        remaining = text

        # Extract THINK content (prefer standard closing tag)
        think_matches = re.findall(
            r"<think>(.*?)</think>", remaining, flags=re.DOTALL | re.IGNORECASE
        )
        if think_matches:
            reasoning_content = _strip_tags("".join(think_matches))
            # Remove all complete think sections to avoid interference with answer extraction
            remaining = re.sub(r"<think>.*?</think>", "", remaining, flags=re.DOTALL | re.IGNORECASE)
        else:
            # fallback A: only </think>
            m_close = re.search(r"</think>", remaining, flags=re.IGNORECASE)
            if m_close:
                reasoning_content = _strip_tags(remaining[:m_close.start()])
                remaining = remaining[m_close.end():]
            else:
                # fallback B: only <think>
                m_open = re.search(r"<think>", remaining, flags=re.IGNORECASE)
                if m_open:
                    reasoning_content = _strip_tags(remaining[m_open.end():])
                    remaining = remaining[:m_open.start()]

        # =========================
        # 2) Extract ANSWER (prefer standard closing tag)
        # =========================
        answer_matches = re.findall(r"<answer>(.*?)</answer>", remaining, flags=re.DOTALL | re.IGNORECASE)
        if answer_matches:
            answer_content = _strip_tags("".join(answer_matches))
        else:
            # fallback A: only </answer>
            m_close = re.search(r"</answer>", remaining, flags=re.IGNORECASE)
            if m_close:
                answer_content = _strip_tags(remaining[:m_close.start()])
            else:
                # fallback B: only <answer>
                m_open = re.search(r"<answer>", remaining, flags=re.IGNORECASE)
                if m_open:
                    answer_content = _strip_tags(remaining[m_open.end():])

        # =========================
        # 3) Fallback logic: if think is present but answer is empty, and remaining text has content, use remaining as answer
        # =========================
        if reasoning_content and not answer_content:
            leftover = _strip_tags(remaining)
            if leftover:
                answer_content = leftover

        # If nothing extracted, return original text with empty answer
        if not reasoning_content and not answer_content:
            return raw, ""

        return reasoning_content, answer_content

    def _call_model(self, system_prompt: str, user_prompt: str) -> str:
        """Call local LLM API to generate model response.

        Args:
            system_prompt: System instruction prompt.
            user_prompt: User query prompt.

        Returns:
            Model response content string.

        Raises:
            requests.RequestException: If API request fails.
        """
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
        }
        print(self.base_url)
        response = requests.post(
            f"{self.base_url}/v1/chat/completions", json=payload, timeout=120
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _run_with_extract(self, system_prompt: str, user_prompt: str) -> Tuple[str, str, str]:
        """Call model + parse <think>/<answer> tags.
        
        If local model fails (e.g., request exception, timeout, format error), 
        automatically fallback to DashScope API.
        
        Returns:
            (raw, reasoning, answer)
        """
        try:
            raw = self._call_model(system_prompt, user_prompt)
            reasoning, answer = self._extract_content(raw)
            if not answer.strip():
                answer = raw.strip()
            return raw, reasoning, answer
        except Exception as e:
            print(f"[WARN] Local model failed: {e}. Falling back to DashScope API...")
            try:
                answer_content, reasoning_content = self._api_get_answer_and_thinking(
                    system_prompt, user_prompt
                )
                # For consistency: (raw, reasoning, answer)
                # Use answer_content as raw since DashScope doesn't return unparsed content
                return answer_content, reasoning_content, answer_content
            except Exception as e2:
                print(f"[ERROR] Both local model and DashScope API failed: {e2}")
                # Final fallback: return empty strings
                return "", "", ""

    def _api_get_answer_and_thinking(self, system_prompt: str, user_prompt: str) -> Tuple[str, str]:
        """Use DashScope OpenAI-compatible API to call model with thinking capability.
        
        Returns:
            (answer_content, reasoning_content)

        - Prioritize streaming delta.reasoning_content as thinking process
        - If not available, parse from final content using <think></think>
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        completion = self.dashscope_client.chat.completions.create(
            model="qwen-plus",  # Can be changed to qwen3-235b-a22b-thinking-2507 etc.
            messages=messages,
            stream=True,
        )

        reasoning_content = ""
        answer_content = ""

        for chunk in completion:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            # Streaming reasoning content (some models use this field)
            if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
                reasoning_content += delta.reasoning_content

            # Visible response content
            if hasattr(delta, "content") and delta.content:
                answer_content += delta.content

        answer_content = answer_content.strip()
        reasoning_content = reasoning_content.strip()

        # If API has no dedicated reasoning_content field, parse from content using <think></think>
        if not reasoning_content:
            rc2, ans2 = self._extract_content(answer_content)
            if ans2.strip():
                return ans2.strip(), rc2.strip()
            else:
                return answer_content, ""

        return answer_content, reasoning_content

    def _process_single_text(
        self, data: str
    ) -> Tuple[Dict[str, Any], str, str, str, str, str]:
        """Process single text data through complete analysis pipeline.

        This method executes a multi-step analysis including:
        1. Formulation optimization analysis
        2. Result & Discussion extraction
        3. Material mechanism explanation
        4. Abstract generation
        5. Conclusion table generation
        6. JSON parameter extraction

        Args:
            data: Input text containing material formulation and processing information.

        Returns:
            A tuple containing:
            - report: Complete report dictionary with all sections
            - input_text: Original input text
            - user_prompt_analyze: Prompt used for analysis
            - optimized_fp_obj: Optimized formula parameters object
            - answer_content_analyze: Analysis result text
            - reasoning_content_analyze: Reasoning content from analysis
        """
        # Extract input_text and material from raw json
        input_text = data

        # material = sample_info.get("Change_Category", "")

        # Step 1: Formulation optimization analysis
        print("Step 1: Formulation optimization analysis")
        system_prompt_analyze, user_prompt_analyze = ReportPrompts.get_analyze_prompts(input_text)
        _, reasoning_content_analyze, answer_content_analyze = self._run_with_extract(
            system_prompt_analyze, user_prompt_analyze
        )
        print("Step 1 - Reasoning:", reasoning_content_analyze)

        # Step 2: Extract Result & Discussion
        system_prompt_rewrite, user_prompt_rewrite = ReportPrompts.get_rewrite_prompts(answer_content_analyze)

        # _, reasoning_content_rewrite, answer_content_rewrite = run_with_extract(
        #     system_prompt_rewrite, user_prompt_rewrite
        # )

        answer_content_rewrite, reasoning_content_rewrite = self._api_get_answer_and_thinking(
            system_prompt_rewrite, user_prompt_rewrite
        )

        # Step 3: Material mechanism explanation
        print("Step 3: Material mechanism explanation")
        system_prompt_material, user_prompt_material = ReportPrompts.get_material_prompts(answer_content_rewrite)
        _, reasoning_content_material, answer_content_material = self._run_with_extract(
            system_prompt_material, user_prompt_material
        )

        # Step 4: Abstract generation
        system_prompt_abstract, user_prompt_abstract = ReportPrompts.get_abstract_prompts(input_text, answer_content_analyze)

        # _, reasoning_content_abstract, answer_content_abstract = run_with_extract(
        #     system_prompt_abstract, user_prompt_abstract
        # )

        answer_content_abstract, reasoning_content_abstract = self._api_get_answer_and_thinking(
            system_prompt_abstract, user_prompt_abstract
        )

        # Step 5: Conclusion table generation
        print("Step 5: Conclusion table generation")
        system_prompt_table, user_prompt_table = ReportPrompts.get_table_prompts(answer_content_analyze)

        # _, reasoning_content_table, answer_content_table = run_with_extract(
        #     system_prompt_table, user_prompt_table
        # )

        answer_content_table, reasoning_content_table = self._api_get_answer_and_thinking(
            system_prompt_table, user_prompt_table
        )

        # Step 6: JSON parameter extraction
        system_prompt_json, user_prompt_json = ReportPrompts.get_json_prompts(input_text, answer_content_analyze)

        # _, reasoning_content_json, answer_content_json = run_with_extract(
        #     system_prompt_json, user_prompt_json
        # )

        answer_content_json, reasoning_content_json = self._api_get_answer_and_thinking(
            system_prompt_json, user_prompt_json
        )

        # Try to parse as JSON object, if fails keep original string
        try:
            optimized_fp_obj: Any = json.loads(answer_content_json)
        except Exception:
            optimized_fp_obj = answer_content_json

        # Build final report structure
        report = {
            "1_Abstract": answer_content_abstract,
            "2_Introduction": input_text,
            "3_Result_Discussion": answer_content_analyze,
            "4_Conclusion": {
                "4_1_Table": answer_content_table,
                "4_2_Optimized_Formula_Parameter": optimized_fp_obj,
            },
            "5_Supporting_Information": answer_content_material,
            # Debug reasoning can be enabled if needed:
            # "debug_reasoning": {
            #     "analyze": reasoning_content_analyze,
            #     "rewrite": reasoning_content_rewrite,
            #     "material": reasoning_content_material,
            #     "abstract": reasoning_content_abstract,
            #     "table": reasoning_content_table,
            #     "json": reasoning_content_json,
            # },
        }

        return report, input_text, user_prompt_analyze,optimized_fp_obj,answer_content_analyze,reasoning_content_analyze

    def _row_to_standard_dict(self, row: pd.Series) -> Dict[str, str]:
        """Convert pandas Series to standard dictionary with expected fields.

        This method ensures field names and order strictly follow EXPECTED_FIELDS,
        replacing missing or NaN values with empty strings.

        Args:
            row: Pandas Series containing experimental data.

        Returns:
            Standardized dictionary with all expected fields.
        """
        result = {}
        for field in self.expected_fields:
            # Check if field exists
            if field in row.index:
                val = row[field]
                # Handle NaN / None / empty values
                if pd.isna(val) or val is None or str(val).strip().lower() in (
                    "nan",
                    "none",
                    "n/a",
                    "",
                ):
                    result[field] = ""
                else:
                    result[field] = str(val).strip()
            else:
                result[field] = ""
        return result

    def _insert_final_record(
        self,
        ID: str,
        status: int,
        control_recipe_value: Dict[str, Any],
        reasoning_output: Dict[str, Any],
        control_recipe_text: str,
        question: str,
        recommend_value: Dict[str, Any],
        mechanism: str,
        mechanism_reasoning: str,
    ) -> None:
        """Insert final record into output database.

        Args:
            ID: Sample identifier.
            status: Record status code.
            control_recipe_value: Control recipe parameters dictionary.
            reasoning_output: Model reasoning output dictionary.
            control_recipe_text: Original control recipe text.
            question: Research question text.
            recommend_value: Recommended value dictionary.
            mechanism: Mechanism description text.
            mechanism_reasoning: Mechanism reasoning text.
        """
        # Convert to JSON string safely
        def safe_json(val: Any) -> str:
            if isinstance(val, (dict, list)):
                return json.dumps(val, ensure_ascii=False)
            else:
                return str(val) if val is not None else ""

        control_recipe_value_json = safe_json(control_recipe_value)
        reasoning_output_json = safe_json(reasoning_output)
        recommend_value_json = safe_json(recommend_value)

        # Build insert values (order must match SQL)
        values = [
            ID,
            status,
            control_recipe_value_json,  # JSON
            reasoning_output_json,      # JSON
            recommend_value_json,       # JSON
            control_recipe_text or "",
            question or "",
            mechanism or "",
            mechanism_reasoning or ""
        ]

        # SQL statement (field order must match values)
        sql = """
        INSERT INTO `report_optimised` (
            ID,
            status,
            control_recipe_value,
            reasoning_output,
            recommend_value,
            control_recipe_text,
            question,
            mechanism,
            mechanism_reasoning
        ) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s)
        """

        # Execute insert
        conn = None
        try:
            conn = pymysql.connect(**self.output_db_config)  # Note: 'table' not included
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()
            print("✅ Successfully inserted JSON data to database")
        except Exception as e:
            print("❌ Insert failed:", e)
        finally:
            if conn:
                conn.close()
    def _export_output_to_csv(self) -> str:
        """Export data from output database to CSV file.
        
        Exports all records from the report_optimised table to a timestamped CSV file
        in the reasoning/data directory.
        
        Returns:
            Path to the generated CSV file.
        """
        try:
            # Create data directory if it doesn't exist
            data_dir = Path(__file__).resolve().parent.parent / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Connect to output database
            conn = pymysql.connect(**self.output_db_config)
            
            # Read data from report_optimised table
            query = "SELECT * FROM report_optimised"
            df = pd.read_sql(query, conn)
            conn.close()
            
            # Generate timestamped filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"report_optimised_{timestamp}.csv"
            csv_path = data_dir / csv_filename
            
            # Export to CSV
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"✅ Successfully exported {len(df)} records to CSV: {csv_path}")
            return str(csv_path)
            
        except Exception as e:
            print(f"❌ CSV export failed: {e}")
            traceback.print_exc()
            return ""

    def _get_random_row_from_db(self, config: Dict) -> pd.Series:
        """Fetch random row from database using provided configuration.

        Args:
            config: Database configuration dict with host, user, password, database, port, table.

        Returns:
            Pandas Series containing random row data.

        Raises:
            ValueError: If table is empty.
        """
    def run_all(self, total_runs=5, max_workers=5):
        """
        读取数据库所有数据，并对每一条数据生成 total_runs 次报告
        """
        try:
            # 1. 获取所有数据
            print("📥 Fetching all data from database...")
            all_data_df = get_all_rows_from_db(self.db_config)
            total_rows = len(all_data_df)
            print(f"✅ Successfully fetched {total_rows} rows from database.")

            if total_rows == 0:
                print("❌ No data found to process.")
                return

            global_success_count = 0
            global_total_expected = total_rows * total_runs

            # 2. 遍历每一行数据
            for idx, row in all_data_df.iterrows():
                # 数据预处理
                row.index = row.index.str.strip()
                sample_id = row.get("sample_id")
                
                # 兼容处理：如果没有 sample_id，尝试使用索引或其他唯一标识
                if sample_id is None:
                    sample_id = f"row_{idx}" 
                    print(f"⚠️ Row {idx+1}/{total_rows} missing sample_id, using {sample_id}")
                
                print(f"\n🚀 Processing Row {idx+1}/{total_rows} (sample_id={sample_id})")

                try:
                    # 预处理：每条数据只执行一次文本生成和字典转换
                    output_text = row_to_text(row)
                    control_recipe_value = self._row_to_standard_dict(row)
                    
                    # 调试打印
                    # print(f"   ✅ Generated description text: {output_text[:50]}...")

                    # 3. 内层并发：对当前这条数据生成 total_runs 次报告
                    def _generate_and_insert(trial_idx: int) -> bool:
                        try:
                            # 线程标识
                            # tid = threading.get_ident()
                            print(f"   🔄 [Trial {trial_idx+1}/{total_runs}] Generating...")
                            
                            reasoning_output, control_recipe_text, question, recommend_value, mechanism, mechanism_reasoning = \
                                self._process_single_text(output_text)

                            self._insert_final_record(
                                ID=sample_id,
                                status=0,
                                control_recipe_value=control_recipe_value,
                                reasoning_output=reasoning_output,
                                control_recipe_text=control_recipe_text,
                                question=question,
                                recommend_value=recommend_value,
                                mechanism=mechanism,
                                mechanism_reasoning=mechanism_reasoning
                            )
                            # print(f"   ✅ Trial {trial_idx+1} inserted.")
                            return True
                        except Exception as e:
                            print(f"   ⚠️ Trial {trial_idx+1} failed: {e}")
                            return False

                    # 执行当前行的并发任务
                    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures_list = [
                            executor.submit(_generate_and_insert, i) for i in range(total_runs)
                        ]
                        results = [
                            future.result() for future in futures.as_completed(futures_list)
                        ]

                    success_count = sum(results)
                    global_success_count += success_count
                    print(f"   🎉 Row {idx+1} Completed: {success_count}/{total_runs} successes.")

                except Exception as row_err:
                    print(f"   ❌ Row {idx+1} (sample_id={sample_id}) processing failed: {row_err}")
                    traceback.print_exc()
                    # 继续处理下一行，不中断整个程序
                    continue

            print("\n" + "="*50)
            print(f"🏁 All Done!")
            print(f"📊 Total Rows: {total_rows}")
            print(f"📊 Total Expected Runs: {global_total_expected}")
            print(f"✅ Total Successful Outputs: {global_success_count}")
            print(f"📉 Success Rate: {global_success_count/global_total_expected:.2%}")
            print("="*50)
            
            # Export output database to CSV
            print("\n📤 Exporting results to CSV...")
            self._export_output_to_csv()

        except Exception as e:
            print("❌ run_all execution failed:", e)
            traceback.print_exc()





    def run_once(
        self, total_runs: int = 1, max_workers: Optional[int] = None
    ) -> None:
        """Read one record from database and generate reports in parallel.

        Args:
            total_runs: Number of reports to generate. Default: 1
            max_workers: Maximum concurrent threads. Default: total_runs
        """
        if max_workers is None:
            max_workers = total_runs

        try:
            # Read one record from database
            row = get_random_row_from_db(self.db_config)
            row.index = row.index.str.strip()
            sample_id = row.get("sample_id")
            if sample_id is None:
                raise ValueError("Row does not contain sample_id field")
            print(f"✅ Successfully read one original data (sample_id={sample_id})")

            # Preprocessing: execute only once
            output_text = row_to_text(row)
            control_recipe_value = self._row_to_standard_dict(row)
            print(
                "✅ Generated description text:",
                output_text[:100] + "..."
                if len(output_text) > 100
                else output_text,
            )

            # Generate total_runs reports concurrently with max_workers threads
            def _generate_and_insert(trial_idx: int) -> bool:
                try:
                    print(
                        f"🔄 [Thread {threading.get_ident()}] Generating trial {trial_idx+1}/{total_runs}..."
                    )
                    reasoning_output, control_recipe_text, question, recommend_value, mechanism, mechanism_reasoning = \
                        self._process_single_text(output_text)

                    self._insert_final_record(
                        ID=sample_id,
                        status=0,
                        control_recipe_value=control_recipe_value,
                        reasoning_output=reasoning_output,
                        control_recipe_text=control_recipe_text,
                        question=question,
                        recommend_value=recommend_value,
                        mechanism=mechanism,
                        mechanism_reasoning=mechanism_reasoning
                    )
                    print(f"✅ Trial {trial_idx+1} result successfully inserted to database")
                    return True
                except Exception as e:
                    print(f"⚠️ Trial {trial_idx+1} generation failed: {e}")
                    return False

            # Execute concurrently using ThreadPoolExecutor
            with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures_list = [
                    executor.submit(_generate_and_insert, i) for i in range(total_runs)
                ]
                results = [
                    future.result() for future in futures.as_completed(futures_list)
                ]

            success_count = sum(results)
            print(
                f"🎉 Completed: 1 input → {success_count}/{total_runs} outputs successfully generated and stored"
            )
            
            # Export output database to CSV
            print("\n📤 Exporting results to CSV...")
            self._export_output_to_csv()

        except Exception as e:
            print("❌ run_once execution failed:", e)
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    generator = PerovskiteReportGenerator.from_config()
    generator.run_once(total_runs=5, max_workers=5)
