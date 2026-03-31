"""
Learning module - Automated data processing pipeline for robotic learning.

This module provides:
- Data extraction from database
- Data cleaning and deduplication  
- Single variable matching algorithms
- Characterization, Edge, and Variable reporting pipelines
"""

# Re-export main components for easy import
from .src.perovskite_report_generator import PerovskiteReportGenerator 


__all__ = [
    # Main Pipeline Classes
    "PerovskiteReportGenerator "
]
