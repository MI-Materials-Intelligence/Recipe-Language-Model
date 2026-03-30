# Single Formula Function Module
# """
# Single-Variable Perovskite Formula Analysis Module

# Main Classes:
#     SingleReportPipeline: Main entry class, providing complete data cleaning, report generation, and mechanism analysis workflow

# Example Usage:
#     >>> from app.tool.RLM.generate.single_formula_function import SingleReportPipeline
#     >>> pipeline = SingleReportPipeline()
#     >>> pipeline.run_all()
# """

# from .src.single_report import SingleReportPipeline as _SingleReportPipeline

# # Maintain backward compatibility: support both import methods
# class SingleReportPipeline(_SingleReportPipeline):
#     """Backward-compatible wrapper class"""
#     pass

# __all__ = ["SingleReportPipeline"]
