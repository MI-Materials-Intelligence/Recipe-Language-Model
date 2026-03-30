# Optimized imports using __init__.py
from seven_ai_layers_robotics.learning import (
    RoboticDataPipeline,
    EdgeReportPipeline, 
    CharacterizationDataPipeline
)

# from seven_ai_layers_robotics.generating import (
#     VariableReportPipeline,
#     CharacterisationReportPipeline,
#     EdgeReportPipeline
# )
# from seven_ai_layers_robotics.recipeQA import CorpusGenerator
# import asyncio
# from seven_ai_layers_robotics.reasoning import PerovskiteReportGenerator

# from seven_ai_layers_robotics.evaluation import MIRecipeEvaluator
if __name__ == "__main__":
    pipeline1 = RoboticDataPipeline()
    pipeline1.run_full_process(table_name="data3000")

    # pipeline2 = EdgeReportPipeline()
    # pipeline2.run_full_process("data50764")

    # pipeline3 = CharacterizationDataPipeline()
    # pipeline3.run_full_process()
    # pipeline = VariableReportPipeline()
    # success = pipeline.run(steps='all', rebuild_knowledge=True, verbose=True)
    # print("VariableReportPipeline", success)

    # Run characterisation report generation pipeline
    # pipeline2 = CharacterisationReportPipeline()
    # success = pipeline2.run(report_type='all', verbose=True)
    # print("CharacterisationReportPipeline", success)

    # # Run edge report generation pipeline
    # pipeline3 = EdgeReportPipeline()
    # success = pipeline3.run(steps='all', verbose=True)
    # print("EdgeReportPipeline", success)

    # Use asyncio.run() to execute async function

    
    # Asynchronously call generate_all_async() to generate all corpora
    # generator = CorpusGenerator()
    # result = asyncio.run(generator.generate_all_async())


    # generator = PerovskiteReportGenerator.from_config()
    # print("✓ Successfully loaded configuration from config.toml")
    # print("\nStarting report generation...")
    # generator.run_once(total_runs=3, max_workers=3)
    # evaluator = MIRecipeEvaluator()
    # evaluator.run()
