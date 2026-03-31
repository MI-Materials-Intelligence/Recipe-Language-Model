from app.tool.base import BaseTool
import time
import random
import os
import os.path as osp
import json
import re
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import AsyncOpenAI
from app.config import config
from pathlib import Path
import urllib.request
import requests

from app.tool.seven_ai_layers_loop_ii.recipeQA.src.corpus_coordinator import CorpusGenerator



class RecipeQA(BaseTool):
    name: str = "FP_corpora"
    description: str = """FP_corpora"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "FP_corpora_Type": {
                "type": "string",
                "description": "(required) Types of FP_corpora",
                "enum": ["L_FP_corpora", "R_FP_corpora"],
                "default": "R_FP_corpora",
            }
        },
        "required": ["FP_corpora_Type"],
    }

    async def execute(self, FP_corpora_Type: str) -> str:
        workspace_path = Path(config.workspace_root) / "FP"
        expert_data_root = Path(workspace_path) / "all_expert_data_2025-10-20T07-45-08"
        single_var_match_root = Path(workspace_path) / "single_var_match"
        task_save_path = Path(workspace_path) / "to_process_tasks.json"
        dist_save_root = Path(workspace_path) / "dist"
        dataset_path = Path(workspace_path) / "single_var_dataset.json"

        if FP_corpora_Type == "L_FP_corpora":
            return "Corpus generation and upload successful"
        elif FP_corpora_Type == "R_FP_corpora":
            # Use new corpus generation coordinator
            try:
                generator = CorpusGenerator()
                # Asynchronously call generate_all_async() to generate all corpora
                result = await generator.generate_all_async()
                print(result)

                # If only specific types are needed, you can use:
                # result = await generator.generate_optimized_async()
                # result = await generator.generate_single_async()

            except Exception as e:
                print(f"[ERROR] Corpus generation failed: {e}")
                return f"Corpus generation failed: {str(e)}"

        return f"FP_corpora finished"
