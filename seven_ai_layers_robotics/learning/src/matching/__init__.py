"""
Matching module for single variable matching and classification.
"""

from .generating_single_var import generate_single_var
from .get_single_var_diff_class import get_single_var_diff_class
from .merge_results import merge_results
from .single_var_matching_pipeline import run, run_cleaning, run_matching

__all__ = [
    "generate_single_var",
    "get_single_var_diff_class",
    "merge_results",
    "run",
    "run_cleaning",
    "run_matching",
]
