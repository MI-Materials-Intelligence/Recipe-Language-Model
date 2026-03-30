"""
Seven AI Layers Robotics - Advanced robotic learning and reasoning framework.

This package provides:
- Learning: Data extraction, cleaning, matching, and reporting pipelines
- Reasoning: Automated reasoning and analysis
- Generating: Report and content generation
- Evaluation: Model and result evaluation
- Optimization: Parameter and process optimization
- RecipeQA: Question answering for recipe domain
- Fine-tuning: Model fine-tuning utilities
"""

__version__ = "1.0.0"
__author__ = "Recipe Language Model Team"

# Import main modules for convenient access
# Note: Only import modules that don't cause circular imports
from . import learning
# from . import reasoning  # Uncomment if needed and no circular imports
# from . import generating  # Uncomment if needed and no circular imports
# from . import evaluation  # Uncomment if needed and no circular imports
# from . import optimization  # Uncomment if needed and no circular imports
# from . import recipeqa  # Causes circular import - commented out
# from . import fine_tuning  # Uncomment if needed and no circular imports

# Re-export most commonly used classes (commented out to avoid circular imports)
# Users can import directly from learning module if needed
# from .learning import RoboticDataPipeline, EdgeReportPipeline, CharacterizationDataPipeline, DataExtractor

__all__ = [
    # Version info
    "__version__",
    
    # Main modules (only those without circular imports)
    "learning",
    # Add other modules here once circular import issues are resolved
    "generating",
    "evaluation",
    "optimization",
    "recipeQA",
    "fine_tuning"
]
