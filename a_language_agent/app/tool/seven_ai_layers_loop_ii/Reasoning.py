import asyncio
import json
import random
import re
from app.tool.base import BaseTool
from app.tool.seven_ai_layers_loop_ii.reasoning.src.perovskite_report_generator import PerovskiteReportGenerator 
class Reasoning(BaseTool):
    name: str = "Reasoning"
    description: str = """Reasoning(Output perovskite formula and mechanism)"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "Reasoning_Type": {
                "type": "string",
                "description": "(required) Types of Reasoning",
                "enum": ["RReasoning", "LReasoning"],
                "default": "RReasoning"
            }
        },
        "required": ["Reasoning_Type"],
    }

    async def execute(self, Reasoning_Type: str) -> str:
        if Reasoning_Type == "RReasoning":
            generator = PerovskiteReportGenerator.from_config()
            print("✓ Successfully loaded configuration from config.toml")
            print("\nStarting report generation...")
            generator.run_once(total_runs=100, max_workers=10)
            return "Reasoning completed"
        elif Reasoning_Type == "LReasoning":
            generator = PerovskiteReportGenerator.from_config()
            print("✓ Successfully loaded configuration from config.toml")
            print("\nStarting report generation...")
            generator.run_once(total_runs=100, max_workers=10)
            return "Reasoning completed"
        return f"Reasoning completed"


