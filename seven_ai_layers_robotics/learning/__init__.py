"""
Learning module - Automated data processing pipeline for robotic learning.

This module provides:
- Data extraction from database
- Data cleaning and deduplication
- Single variable matching algorithms
- Characterization, Edge, and Variable reporting pipelines
"""

from .src.variable_reporting_match import RoboticDataPipeline
from .src.edge_reporting_match import EdgeReportPipeline
from .src.characterisation_reporting_match import CharacterizationDataPipeline
from .src.extraction.data_extractor import DataExtractor

__all__ = [
    "RoboticDataPipeline",
    "EdgeReportPipeline",
    "CharacterizationDataPipeline",
    "DataExtractor",
]
