"""
Edge reporting module for generating experimental edge reports.

This module provides functionality for:
- Edge mechanism analysis
- Automatic report generation from database records
- Template-based paragraph construction
"""

from . import edge_report_generator
from . import edge_mechanism_analyzer

__all__ = [
    "edge_report_generator",
    "edge_mechanism_analyzer",
]