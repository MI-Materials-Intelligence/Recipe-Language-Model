#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recipe Language Model - Main Entry Point

A seven-layer AI architecture for perovskite solar cell research:
- Learning: Data cleaning, extraction, and matching
- Generating: Characterization, edge, and variable report generation
- RecipeQA: Knowledge Q&A construction
- Fine-tuning: LoRA fine-tuning framework
- Reasoning: Mechanism reasoning and report generation
- Evaluation: Numerical and semantic evaluation
- Optimization: DPO optimization API

Usage:
    python main.py learning              # Run variable learning data pipeline
    python main.py generating            # Run all report generation pipelines
    python main.py recipeqa              # Generate all corpora
    python main.py reasoning             # Generate perovskite reports
    python main.py evaluation            # Run MIRecipe evaluation
    
    # Specific pipeline examples:
    python main.py learning --pipeline variable      # variable data pipeline
    python main.py learning --pipeline edge         # Edge report pipeline
    python main.py learning --pipeline characterization  # Characterization pipeline
    python main.py generating --report variable     # Variable reports
    python main.py generating --report characterisation  # Characterisation reports
    python main.py generating --report edge         # Edge reports
"""

import argparse
import sys
import warnings
from typing import Optional

# Suppress RequestsDependencyWarning for urllib3/chardet version mismatch
warnings.filterwarnings("ignore", category=DeprecationWarning, module="requests")
warnings.filterwarnings("ignore", message=".*urllib3.*chardet.*charset_normalizer.*")

# Optimized imports using __init__.py
from seven_ai_layers_robotics.learning import (
    RoboticDataPipeline,
    EdgeReportPipeline, 
    CharacterizationDataPipeline
)

from seven_ai_layers_robotics.generating import (
    VariableReportPipeline,
    CharacterisationReportPipeline,
    EdgeReportPipeline as GeneratingEdgeReportPipeline
)
from seven_ai_layers_robotics.recipeQA import CorpusGenerator
import asyncio
from seven_ai_layers_robotics.reasoning import PerovskiteReportGenerator

from seven_ai_layers_robotics.evaluation import MIRecipeEvaluator
from seven_ai_layers_robotics.optimization import DPOTrainDataExporter
from seven_ai_layers_robotics.fine_tuning import SFTTrainDataExporter

def run_learning_pipeline(args):
    """Execute learning module pipelines"""
    pipeline_type = args.pipeline.lower()
    
    if pipeline_type == 'variable':
        print("\n Running Variable Learning Data Pipeline...")
        pipeline = RoboticDataPipeline()
        success = pipeline.run_full_process(table_name="experiments_data")
        return success
        
    elif pipeline_type == 'edge':
        print("\n Running Edge Report Pipeline...")
        pipeline = EdgeReportPipeline()
        success = pipeline.run_full_process("experiments_data")
        return success
        
    elif pipeline_type == 'characterization':
        print("\n Running Characterization Data Pipeline...")
        pipeline = CharacterizationDataPipeline()
        success = pipeline.run_full_process()
        return success
        
    else:
        print(f" Unknown learning pipeline type: {pipeline_type}")
        print("Available types:variable, edge, characterization")
        return False


def run_generating_pipeline(args):
    """Execute generating module pipelines"""
    report_type = args.report.lower()
    
    if report_type == 'variable':
        print("\n Running Variable Report Pipeline...")
        pipeline = VariableReportPipeline()
        success = pipeline.run(steps='report', rebuild_knowledge=args.rebuild_knowledge, verbose=True)
        print("VariableReportPipeline", success)
        return success
        
    elif report_type == 'characterisation':
        print("\n Running Characterisation Report Pipeline...")
        pipeline = CharacterisationReportPipeline()
        success = pipeline.run(report_type='all', verbose=True)
        print("CharacterisationReportPipeline", success)
        return success
        
    elif report_type == 'edge':
        print("\n Running Edge Report Pipeline...")
        pipeline = GeneratingEdgeReportPipeline()
        success = pipeline.run(steps='all', verbose=True)
        print("EdgeReportPipeline", success)
        return success
        
    else:
        print(f" Unknown generating report type: {report_type}")
        print("Available types: variable, characterisation, edge")
        return False


def run_recipeqa(args):
    """Execute RecipeQA corpus generation"""
    print("\n Running RecipeQA Corpus Generation...")
    generator = CorpusGenerator()
    
    try:
        result = asyncio.run(generator.generate_all_async())
        print(result)
        return True
    except Exception as e:
        print(f" Error generating corpora: {e}")
        return False


def run_reasoning(args):
    """Execute reasoning module report generation"""
    print("\n Running Perovskite Report Generator...")
    
    try:
        generator = PerovskiteReportGenerator.from_config()
        print("Successfully loaded configuration from config.toml")
        print("\nStarting report generation...")
        generator.run_all(total_runs=args.total_runs, max_workers=args.max_workers)
        print("Report generation completed")
        return True
    except Exception as e:
        print(f"Error in reasoning: {e}")
        return False


def run_evaluation(args):
    """Execute evaluation module"""
    print("\n Running MIRecipe Evaluation...")
    
    try:
        evaluator = MIRecipeEvaluator()
        evaluator.run()
        return True
    except Exception as e:
        print(f"Error in evaluation: {e}")
        return False


def run_optimization(args):
    """Execute optimization module - DPO training data export and preparation"""
    print("\n Running DPO Training Data Exporter...")
    
    try:
        exporter = DPOTrainDataExporter()
        
    
        csv_path = exporter.run_pipeline(
            item_name=args.item_name,
            call_training=True,
            optimize_questions=True,
            optimization_limit=10,
            system_prompt="You are an expert in perovskite materials."
        )
        
        if csv_path:
            print(f"\n Optimization completed.")
            return True
        else:
            print("\n Optimization failed.")
            return False
            
    except Exception as e:
        print(f"Error in optimization: {e}")
        return False


def run_fine_tuning(args):
    """Execute fine-tuning module - SFT training data export and pipeline"""
    print("\n Running SFT Training Data Exporter...")
    
    try:
        exporter = SFTTrainDataExporter()
        
        results = exporter.run_pipeline(
            item_name=args.item_name,
            launch_training=False,
            launch_inference=False,
            max_wait_minutes=60,
            check_interval=20
        )
        
        if results:
            print(f"\n Fine-tuning pipeline completed.")
            print(f"Item name: {results['item_name']}")
            print(f"Prepare training: {results['prepare_training']}")
            print(f"Training: {results['training']}")
            print(f"Training status: {results['training_status']}")
            print(f"Inference: {results['inference']}")
            return True
        else:
            print("\n Fine-tuning pipeline failed.")
            return False
            
    except Exception as e:
        print(f"Error in fine-tuning: {e}")
        return False


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Recipe Language Model - Seven-Layer AI Architecture for Perovskite Research',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s learning --pipeline robotic
  %(prog)s generating --report variable
  %(prog)s recipeqa
  %(prog)s reasoning --total-runs 15
  %(prog)s evaluation
  %(prog)s optimization --item-name test1
  %(prog)s fine-tuning --item-name test1
        """
    )
    
    # Create subparsers for each module
    subparsers = parser.add_subparsers(dest='module', help='Module to execute')
    
    # Learning module
    learning_parser = subparsers.add_parser('learning', help='Learning module - Data processing pipeline')
    learning_parser.add_argument(
        '--pipeline', '-p',
        type=str,
        default='variable',
        choices=['variable', 'edge', 'characterization'],
        help='Pipeline type to run (default: robotic)'
    )
    learning_parser.set_defaults(func=run_learning_pipeline)
    
    # Generating module
    generating_parser = subparsers.add_parser('generating', help='Generating module - Report generation')
    generating_parser.add_argument(
        '--report', '-r',
        type=str,
        default='variable',
        choices=['variable', 'characterisation', 'edge'],
        help='Report type to generate (default: variable)'
    )
    generating_parser.add_argument(
        '--rebuild-knowledge',
        action='store_true',
        help='Rebuild knowledge base before generation'
    )
    generating_parser.set_defaults(func=run_generating_pipeline)
    
    # RecipeQA module
    recipeqa_parser = subparsers.add_parser('recipeqa', help='RecipeQA module - Corpus generation')
    recipeqa_parser.set_defaults(func=run_recipeqa)
    
    # Reasoning module
    reasoning_parser = subparsers.add_parser('reasoning', help='Reasoning module - Mechanism reasoning')
    reasoning_parser.add_argument(
        '--total-runs', '-n',
        type=int,
        default=15,
        help='Number of reports to generate (default: 15)'
    )
    reasoning_parser.add_argument(
        '--max-workers', '-w',
        type=int,
        default=10,
        help='Maximum concurrent workers (default: 10)'
    )
    reasoning_parser.set_defaults(func=run_reasoning)
    
    # Evaluation module
    evaluation_parser = subparsers.add_parser('evaluation', help='Evaluation module - Recipe evaluation')
    evaluation_parser.set_defaults(func=run_evaluation)
    
    # Optimization module
    optimization_parser = subparsers.add_parser('optimization', help='Optimization module - DPO training data export')
    optimization_parser.add_argument(
        '--item-name',
        type=str,
        default='api_test',
        help='Item identifier for tracking (default: api_test)'
    )
    optimization_parser.set_defaults(func=run_optimization)
    
    # Fine-tuning module
    fine_tuning_parser = subparsers.add_parser('fine-tuning', help='Fine-tuning module - SFT training data export')
    fine_tuning_parser.add_argument(
        '--item-name',
        type=str,
        default='sft_test',
        help='Item identifier for training job (default: sft_test)'
    )
    fine_tuning_parser.set_defaults(func=run_fine_tuning)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the selected module
    if args.module is None:
        parser.print_help()
        print("\n Please specify a module to run (learning, generating, recipeqa, reasoning, or evaluation)")
        sys.exit(1)
    
    # Run the selected function
    success = args.func(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
