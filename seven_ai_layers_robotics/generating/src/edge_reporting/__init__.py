"""
Edge reporting module for generating experimental edge reports.

This module provides functionality for:
- Edge mechanism analysis
- Automatic report generation from database records
- Template-based paragraph construction
"""

from .edge_report_generator import EdgeReportGenerator
from .edge_mechanism_analyzer import EdgeMechanismAnalyzer

__all__ = [
    "EdgeReportGenerator",
    "EdgeMechanismAnalyzer",
]