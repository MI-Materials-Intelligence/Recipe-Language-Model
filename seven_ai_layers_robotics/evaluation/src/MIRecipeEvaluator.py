import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from sqlalchemy import create_engine, text

# Add the src directory to sys.path for relative imports
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from seven_ai_layers_robotics.config import config

# Import local evaluation functions
from evaluation.evaluation_custom import calculate_evaluation_custom, get_required_params
from recipe_recommendation.recipe_recommendation import calculate_recipe_recommendation



class MIRecipeEvaluator:
    """
    A evaluator for perovskite solar cell recipe recommendations.

    This class loads pending evaluation records from database, calls
    scoring API to get evaluation scores, and updates results back to database.

    Attributes:
        db_config: Database configuration dictionary.
        api_url: URL of the evaluation API endpoint.
        timeout: HTTP request timeout in seconds.
        engine: SQLAlchemy database engine.
    """
    def __init__(self) -> None:
        """
        Initialize the evaluator with database and API configurations.

        Loads configuration from app.config and initializes database connection.
        """
        db = config.database
        # svc = config.services

        self.db_config = {
            "host": db.host,
            "user": db.user,
            "password": db.password,
            "database": db.database,
            "port": db.port,
            "table": "MIRecipe"
        }
        # self.api_url = svc.evaluation_api_url
        # self.timeout = svc.http_timeout_sec

        self.engine = create_engine(
            f"mysql+pymysql://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}?charset={db.charset}",
            pool_pre_ping=True
        )

    def load_pending_records(self) -> List[Dict[str, Any]]:
        """
        Load all pending records from database where status equals 0.

        Returns:
            A list of dictionaries containing pending evaluation records.
            Returns empty list if no records found or error occurs.
        """
        try:
            sql = f"SELECT * FROM `{self.db_config['table']}` WHERE status = 0;"
            df = pd.read_sql(sql, self.engine)
            print(f"📌 Total {len(df)} pending records loaded (status IS NULL).")
            return df.to_dict('records')
        except Exception as e:
            print("❌ Failed to load database records:", e)
            return []

    def send_to_http_api(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send evaluation data to HTTP API and get response.

        Args:
            data: Evaluation payload as dictionary.

        Returns:
            JSON response from API as dictionary, or None if request fails.
        """
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(self.api_url, json=data, timeout=300)
            response.raise_for_status()
            print(f"✅ Score API called successfully")
            return response.json()
        except Exception as e:
            print(f"❌ Failed to call score API: {e}")
            return None

    def get_evaluation_score(self, db_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build evaluation payload from database record and call local evaluation functions.

        Args:
            db_data: Database record containing recipe and reasoning data.

        Returns:
            Dictionary with 'index', 'predicted_pce', and 'score' keys, or None if evaluation fails.
        """
        try:
            # 1. Build recipe data
            control_fp = json.loads(db_data["control_recipe_value"])
            optimized_fp = json.loads(db_data["recommend_value"])

            # 2. Call calculate_recipe_recommendation to calculate recipe recommendation results
            recipe_recommendation_result = calculate_recipe_recommendation(optimized_fp, control_fp)
            predicted_pce = json.dumps(recipe_recommendation_result, ensure_ascii=False)  # Save complete calculation result as JSON string

            # 3. Build input for evaluation_custom
            eval_input = {
                "control_FP": control_fp,
                "optimized_FP": optimized_fp,
                "mechanism": str(db_data["mechanism"]),
                "substance": json.loads(db_data["reasoning_output"]).get("5_Supporting_Information", None),
                "evaluation_custom": {
                    "indicator_weight": {
                        "recipe_integrity": 0.05,
                        "formula_rationality": 0.05,
                        "parameter_rationality": 0.05,
                        "performance_rationality": 0,
                        "recipe_recommendation": 0,
                        "experimental_validation": 0.35,
                        "domain_knowledge": 0.1,
                        "mechanism_integrity": 0.1,
                        "mechanism_interpretation": 0.1,
                        "mechanism_comprehensiveness": 0.1,
                        "mechanism_coherence": 0.1
                    }
                }
            }


            print("eval_input:", eval_input)

            # 4. Call evaluation_custom to calculate Score
            optimize, control, to_evaluate, substance, ground, indicator_weight = get_required_params(eval_input)
            score_result = calculate_evaluation_custom(optimize, control, to_evaluate, substance, ground, indicator_weight)

            print(f"✅ Local evaluation completed - predicted_pce: {predicted_pce}, overall_score: {score_result.get('score', {}).get('overall', None)}")

            return {
                "index": db_data["index"],
                "predicted_pce": predicted_pce,
                "score": score_result
            }
        except Exception as e:
            print("❌ Failed to get score:", e)
            import traceback
            traceback.print_exc()
            return None

    def update_score_to_db(self, result: Dict[str, Any]) -> bool:
        """
        Update evaluation score, predicted_pce and status in database.

        Args:
            result: Evaluation result dictionary containing 'index', 'predicted_pce' and 'score'.

        Returns:
            True if update successful, False otherwise.
        """
        if not result:
            return False

        try:
            with self.engine.connect() as conn:
                sql_update = f"""
                    UPDATE `{self.db_config["table"]}`
                    SET Score = :score, predicted_pce = :predicted_pce, status = 1
                    WHERE `index` = :index
                """
                conn.execute(
                    text(sql_update),
                    {
                        "score": json.dumps(result["score"], ensure_ascii=False),
                        "predicted_pce": result.get("predicted_pce"),
                        "index": result["index"]
                    }
                )
                conn.commit()

            print(f"✅ Successfully updated Score, predicted_pce and status=1 for index={result['index']}")
            return True
        except Exception as e:
            print(f"❌ Database update failed (index={result['index']}): {e}")
            return False

    def run(self) -> None:
        """
        Main execution flow: load pending records, evaluate them, and update results.

        Processes all records with status=0 from database. For each record:
        1. Build evaluation payload
        2. Call scoring API
        3. Update database with score and set status=1
        """
        pending = self.load_pending_records()
        if not pending:
            print("⚠️ No data to process (status IS NULL).")
            return

        # for record in pending[:1]:
        for record in pending:
            print("\n============================")
            print(f"▶️ Starting to process index = {record['index']}")
            print("============================")

            result = self.get_evaluation_score(record)
            self.update_score_to_db(result)

        print("\n🎉 All records with status IS NULL have been processed!")


# ============================================================================
# Example usage (no parameters needed)
# ============================================================================
if __name__ == '__main__':
    evaluator = MIRecipeEvaluator()
    evaluator.run()


