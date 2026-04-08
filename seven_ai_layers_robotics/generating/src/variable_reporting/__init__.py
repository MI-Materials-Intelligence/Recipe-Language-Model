# -*- coding: utf-8 -*-
"""Variable Reporting Module for Perovskite Solar Cell Analysis.

This module provides tools for generating single-variable perovskite reports,
including mechanism analysis and automated report generation.

Main Classes:
    PerovskiteAnalyzer: Perovskite mechanism analyzer for analyzing experimental data.
    ReportGenerator: Automated report generator with configurable templates.
    ReportConfig: Configuration class for report generation parameters.

Example Usage:
    >>> from seven_ai_layers_robotics.generating.src.variable_reporting import (
    ...     PerovskiteAnalyzer,
    ...     ReportGenerator,
    ...     ReportConfig
    ... )
    >>> analyzer = PerovskiteAnalyzer()
    >>> result = await analyzer.run_async()
    >>> config = ReportConfig()
    >>> generator = ReportGenerator(config=config)
    >>> stats = generator.run()
"""

from .single_report_prepare import PerovskiteAnalyzer
from .single_report import ReportGenerator, ReportConfig

__all__ = [
    "PerovskiteAnalyzer",
    "ReportGenerator",
    "ReportConfig",
]