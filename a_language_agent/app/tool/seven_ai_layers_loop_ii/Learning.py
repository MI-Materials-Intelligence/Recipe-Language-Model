from pathlib import Path
import os
import sys
import asyncio
import aiohttp
from app.tool.base import BaseTool
from app.config import config

# Add Learning module's parent directory to path to ensure correct import of src package
learning_dir = os.path.dirname(os.path.abspath(__file__))
learning_parent_dir = os.path.dirname(learning_dir)
if learning_parent_dir not in sys.path:
    sys.path.insert(0, learning_parent_dir)

from app.tool.seven_ai_layers_loop_ii.learning.src.variable_reporting_match import RoboticDataPipeline
from app.tool.seven_ai_layers_loop_ii.learning.src.edge_reporting_match import EdgeReportPipeline
from app.tool.seven_ai_layers_loop_ii.learning.src.characterisation_reporting_match import CharacterizationDataPipeline



class Learning(BaseTool):
    name: str = "learning"
    description: str = "Download literature or obtain experimental results to learn knowledge from them"
    parameters: dict = {
        "type": "object",
        "properties": {
            "LearningType": {
                "type": "string",
                "description": "(required) Types of learning",
                "enum": ["LLearning", "RLearning"],
                "default": "LLearning"
            }
        },
        "required": ["LearningType"],
    }

    async def execute(self, LearningType: str) -> str:
        if LearningType == "LLearning":
            return await l_learning()
        elif LearningType == "RLearning":
            pipeline1 = RoboticDataPipeline()
            pipeline1.run_full_process(table_name="data3000")

            pipeline2 = EdgeReportPipeline()
            pipeline2.run_full_process("data50764")

            pipeline3 = CharacterizationDataPipeline()
            pipeline3.run_full_process()
            return "🔍 Learning task completed"
        return "✅ Learning task completed"
