"""
Learning module for robotic learning data processing.
Provides data extraction, cleaning, matching, and reporting pipelines.
"""

# Import main pipeline classes for easy access
from .variable_reporting_match import RoboticDataPipeline
from .edge_reporting_match import EdgeReportPipeline
from .characterisation_reporting_match import CharacterizationDataPipeline

# Import utility functions
from .cleaning.preprocess import preprocess
from .cleaning.remove_abnormal import remove_abnormal
from .matching.single_var_matching_pipeline import run as run_matching_pipeline
from .extraction.data_extractor import DataExtractor

__all__ = [
    # Main Pipeline Classes
    "RoboticDataPipeline",
    "EdgeReportPipeline", 
    "CharacterizationDataPipeline",
    
    # Utility Functions
    "preprocess",
    "remove_abnormal",
    "run_matching_pipeline",
    
    # Extractor
    "DataExtractor"
]
