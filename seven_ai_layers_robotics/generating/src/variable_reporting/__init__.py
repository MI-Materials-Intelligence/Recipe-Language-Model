# Single Report Module
"""
Single-Variable Perovskite Report Generation Module

Main Classes:
    PerovskiteAnalyzer: Perovskite mechanism analyzer
    ReportGenerator: Report generator

Example Usage:
    >>> from app.tool.RLM.generate.single_report_module import PerovskiteAnalyzer, ReportGenerator
    >>> analyzer = PerovskiteAnalyzer()
    >>> result = await analyzer.run_async()
    >>> generator = ReportGenerator()
    >>> stats = generator.run()
"""

from .single_report_prepare import PerovskiteAnalyzer
from .single_report import ReportGenerator, ReportConfig

__all__ = [
    "PerovskiteAnalyzer",
    "ReportGenerator",
    "ReportConfig"
]