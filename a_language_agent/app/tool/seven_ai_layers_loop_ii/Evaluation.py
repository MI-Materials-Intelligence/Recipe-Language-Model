from app.tool.base import BaseTool
import os
import sys
import json
import requests
import re
from app.tool.seven_ai_layers_loop_ii.evaluation.src.MIRecipeEvaluator import MIRecipeEvaluator
class Evaluation(BaseTool):
    name: str = "Evaluator"
    description: str = """Evaluator"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "Evaluator_type": {
                "type": "string",
                "description": "(required) Types of Evaluator_type",
                "enum": ["LEvaluator", "REvaluator"],
                "default": "REvaluator",
            }
        },
        "required": ["Evaluator_type"],
    }

    async def execute(self, Evaluator_type: str) -> str:
        print(f"Starting evaluation with {Evaluator_type}")
        if Evaluator_type == "LEvaluator":
            evaluator = MIRecipeEvaluator()
            evaluator.run()
            return "Evaluation completed"
        elif Evaluator_type == "REvaluator":
            evaluator = MIRecipeEvaluator()
            evaluator.run()
            return "Evaluation completed"
        return "Evaluation failed"
