"""
Learning module for robotic learning data processing.
"""

from .cleaning import preprocess, remove_abnormal
from .matching import run, run_cleaning, run_matching
from .extraction.data_extractor import DataExtractor

__all__ = [
    # Curation
    "preprocess",
    "remove_abnormal",
    # Matching
    "run",
    "run_cleaning",
    "run_matching",
    # Extraction
    "DataExtractor"
]
