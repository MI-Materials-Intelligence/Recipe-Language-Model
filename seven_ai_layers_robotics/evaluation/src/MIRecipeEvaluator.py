import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from sqlalchemy import create_engine, text

from seven_ai_layers_robotics.config import config
from seven_ai_layers_robotics.evaluation.src.evaluation.evaluation_custom import calculate_evaluation_custom, get_required_params
from seven_ai_layers_robotics.evaluation.src.recipe_recommendation.recipe_recommendation import calculate_recipe_recommendation


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

        self.db_config = {
            "host": db.host,
            "user": db.user,
            "password": db.password,
            "database": db.database,
            "port": db.port,
            "table": "report_optimised"
        }

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
            print(f"Total {len(df)} pending records loaded (status = 0).")
            return df.to_dict('records')
        except Exception as e:
            print("Failed to load database records:", e)
            return []


    def get_evaluation_score(self, db_record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build evaluation payload from database record and call local evaluation functions.

        Args:
            db_record: Database record containing recipe and reasoning data.

        Returns:
            Dictionary with 'index', 'predicted_pce', and 'score' keys, or None if evaluation fails.
        """
        try:
            control_fp = json.loads(db_record["control_recipe_value"])
            optimized_fp = json.loads(db_record["recommend_value"])

            recipe_recommendation_result = calculate_recipe_recommendation(optimized_fp, control_fp)
            predicted_pce = json.dumps(recipe_recommendation_result, ensure_ascii=False)

            eval_input = {
                "control_fp": control_fp,
                "optimized_fp": optimized_fp,
                "mechanism": str(db_record["mechanism"]),
                "substance": json.loads(db_record["reasoning_output"]).get("5_Supporting_Information", None),
                "evaluation_custom": {
                    "indicator_weight": {
                        "recipe_integrity": 0.05,
                        "formula_rationality": 0.05,
                        "parameter_rationality": 0.05,
                        "performance_rationality": 0,
                        "recipe_recommendation": 0.35,
                        "experimental_validation": 0,
                        "domain_knowledge": 0.1,
                        "mechanism_integrity": 0.1,
                        "mechanism_interpretation": 0.1,
                        "mechanism_comprehensiveness": 0.1,
                        "mechanism_coherence": 0.1
                    }
                }
            }

            optimize, control, to_evaluate, substance, ground, indicator_weight = get_required_params(eval_input)
            score_result = calculate_evaluation_custom(optimize, control, to_evaluate, substance, ground, indicator_weight)

            print(f"Local evaluation completed - predicted_pce: {predicted_pce}, overall_score: {score_result.get('score', {}).get('overall', None)}")

            return {
                "index": db_record["index"],
                "predicted_pce": predicted_pce,
                "score": score_result
            }
        except Exception as e:
            print(" Failed to get score:", e)
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

            print(f"Successfully updated Score, predicted_pce and status=1 for index={result['index']}")
            return True
        except Exception as e:
            print(f"Database update failed (index={result['index']}): {e}")
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
            print("No data to process (status = 0).")
            return

        for db_record in pending:
            print("\n============================")
            print(f"Starting to process index = {db_record['index']}")
            print("============================")

            result = self.get_evaluation_score(db_record)
            self.update_score_to_db(result)

        print("\nAll records with status = 0 have been processed!")


if __name__ == '__main__':
    evaluator = MIRecipeEvaluator()
    evaluator.run()


