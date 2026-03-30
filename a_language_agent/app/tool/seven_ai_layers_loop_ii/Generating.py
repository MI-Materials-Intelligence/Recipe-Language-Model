from pathlib import Path

from app.config import config
from app.tool.base import BaseTool
from app.tool.seven_ai_layers_loop_ii.generating.src.characterisation_reporting_main import CharacterisationReportPipeline
from app.tool.seven_ai_layers_loop_ii.generating.src.edge_reporting_main import EdgeReportPipeline
from app.tool.seven_ai_layers_loop_ii.generating.src.variable_reporting_main import VariableReportPipeline

class Generating(BaseTool):
    name: str = "generating"
    description: str = """Generates perovskite solar cell research reports using expert data and variable matching"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "GeneratingType": {
                "type": "string",
                "description": "(required) Types of Generating",
                "enum": ["LGenerating", "RGenerating"],
                "default": "RGenerating",
            }
        },
        "required": ["GeneratingType"],
    }

    async def execute(self, GeneratingType: str) -> str:

        if GeneratingType == "LGenerating":
            return f"Generating completed"

        elif GeneratingType == "RGenerating":

            # Run variable report generation pipeline
            pipeline = VariableReportPipeline()
            success = pipeline.run(steps='all', rebuild_knowledge=True, verbose=True)
            print("VariableReportPipeline", success)

            # Run characterisation report generation pipeline
            pipeline2 = CharacterisationReportPipeline()
            success = pipeline2.run(report_type='all', verbose=True)
            print("CharacterisationReportPipeline", success)

            # Run edge report generation pipeline
            pipeline3 = EdgeReportPipeline()
            success = pipeline3.run(steps='all', verbose=True)
            print("EdgeReportPipeline", success)

            return f"Generating completed"
