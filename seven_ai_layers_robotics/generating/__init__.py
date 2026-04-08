"""
Learning module - Automated data processing pipeline for robotic learning.

This module provides:
- Data extraction from database
- Data cleaning and deduplication  
- Single variable matching algorithms
- Characterization, Edge, and Variable reporting pipelines
"""

# Re-export main components for easy import
from .src.characterisation_reporting_main import CharacterisationReportPipeline

from .src.edge_reporting_main import EdgeReportPipeline
from .src.variable_reporting_main import VariableReportPipeline

__all__ = [
    "EdgeReportPipeline",
    "CharacterisationReportPipeline",
    "VariableReportPipeline",
]
