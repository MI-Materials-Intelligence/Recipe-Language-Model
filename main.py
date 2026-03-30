"""
RLM-Agent Main Program - Seven-Layer Pipeline
Execution Order: Learning → Generating → RecipeQA → Fine-Tuning → Reasoning → Evaluation → Optimization
"""

import sys
from pathlib import Path

# Add seven_layers to path
seven_layers_root = Path(__file__).parent / "R_Seven_AI_Layers"
sys.path.insert(0, str(seven_layers_root))


def run_learning_layer():
    """Layer 1: Learning Layer - Data Cleaning, Matching, Feature Extraction"""
    print("\n" + "="*60)
    print("Running Layer 1: Learning Layer")
    print("="*60)
    
    try:
        from Learning.src.cleaning import preprocess, remove_abnormal
        from Learning.src.matching import run, run_cleaning, run_matching
        from Learning.src.extraction.data_extractor import DataExtractor
        
        # Run complete matching pipeline
        results = run(data_source="database")
        print(f"✅ Learning Layer completed. Processed {len(results)} records.")
        return True
    except Exception as e:
        print(f"❌ Learning Layer failed: {e}")
        return False


def run_generating_layer():
    """Layer 2: Generating Layer - Characterization, Edge, and Single-Variable Report Generation"""
    print("\n" + "="*60)
    print("Running Layer 2: Generating Layer")
    print("="*60)
    
    try:
        from Generating.src.characterisation_reporting_main import run_batch as run_char_batch
        from Generating.src.edge_reporting_main import run as run_edge
        from Generating.src.variable_reporting_main import run as run_var
        
        # Run three types of report generation
        run_char_batch(data_source="database", limit=100)
        run_edge()
        run_var()
        
        print("✅ Generating Layer completed.")
        return True
    except Exception as e:
        print(f"❌ Generating Layer failed: {e}")
        return False


def run_recipeqa_layer():
    """Layer 3: RecipeQA Layer - Recipe QA Corpus Generation"""
    print("\n" + "="*60)
    print("Running Layer 3: RecipeQA Layer")
    print("="*60)
    
    try:
        from RecipeQA.src.corpus_coordinator import CorpusGenerator
        
        generator = CorpusGenerator()
        
        # Generate all types of corpora
        result = generator.generate_all()
        print(f"✅ RecipeQA Layer completed. {result}")
        return True
    except Exception as e:
        print(f"❌ RecipeQA Layer failed: {e}")
        return False


def run_fine_tuning_layer():
    """Layer 4: Fine-Tuning Layer - Model Fine-Tuning"""
    print("\n" + "="*60)
    print("Running Layer 4: Fine-Tuning Layer")
    print("="*60)
    
    try:
        import requests
        from datetime import datetime
        from pathlib import Path
        
        BASE_URL = "http://localhost:8000"
        MERGED_JSON_PATH = seven_layers_root / "Generating" / "data" / "sft_pairs.json"
        ITEM_NAME = f"ft_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Check if corpus file exists
        if not MERGED_JSON_PATH.exists():
            print(f"⚠️  SFT pairs not found, skipping Fine-Tuning Layer")
            return True
        
        # 1. Prepare training data
        with open(MERGED_JSON_PATH, "rb") as f:
            files = [("corpora_info", ("merged_sft_pairs.json", f, "application/json"))]
            data = {"item_name": ITEM_NAME}
            response = requests.post(f"{BASE_URL}/prepare-training", files=files, data=data)
        
        if response.status_code != 200:
            raise RuntimeError(f"Prepare training failed: {response.text}")
        
        # 2. Start training
        response = requests.post(
            f"{BASE_URL}/run-training",
            json={"item_name": ITEM_NAME, "gpu_ids": [0]}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Run training failed: {response.text}")
        
        print("✅ Fine-Tuning Layer started. Training in progress...")
        return True
    except Exception as e:
        print(f"❌ Fine-Tuning Layer failed: {e}")
        return False


def run_reasoning_layer():
    """Layer 5: Reasoning Layer - Scientific Report Generation and Mechanistic Reasoning"""
    print("\n" + "="*60)
    print("Running Layer 5: Reasoning Layer")
    print("="*60)
    
    try:
        from Reasoning.src.perovskite_report_generator import PerovskiteReportGenerator
        
        generator = PerovskiteReportGenerator()
        
        # Batch generate reports
        record_ids = []  # Get pending record IDs from database
        reports = []
        
        for rid in record_ids:
            try:
                report = generator.generate_report(record_id=rid)
                reports.append(report)
            except Exception as e:
                print(f"Failed to generate report for {rid}: {e}")
        
        print(f"✅ Reasoning Layer completed. Generated {len(reports)} reports.")
        return True
    except Exception as e:
        print(f"❌ Reasoning Layer failed: {e}")
        return False


def run_evaluation_layer():
    """Layer 6: Evaluation Layer - Model Output Evaluation"""
    print("\n" + "="*60)
    print("Running Layer 6: Evaluation Layer")
    print("="*60)
    
    try:
        from Evaluation.src.MIRecipeEvaluator import MIRecipeEvaluator
        
        evaluator = MIRecipeEvaluator()
        
        # Batch evaluation
        recipes = []  # Get recipes to evaluate from database or file
        results = evaluator.batch_evaluate(
            recipes=recipes,
            batch_size=50,
            save_intermediate=True
        )
        
        print(f"✅ Evaluation Layer completed. Evaluated {len(results)} recipes.")
        return True
    except Exception as e:
        print(f"❌ Evaluation Layer failed: {e}")
        return False


def run_optimization_layer():
    """Layer 7: Optimization Layer - DPO Optimization"""
    print("\n" + "="*60)
    print("Running Layer 7: Optimization Layer")
    print("="*60)
    
    try:
        import requests
        from pathlib import Path
        from datetime import datetime
        
        BASE_URL = "http://localhost:8000"
        CSV_FILE = seven_layers_root / "Evaluation" / "data" / "evaluation_scores.csv"
        ITEM_NAME = f"dpo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Check if evaluation file exists
        if not CSV_FILE.exists():
            print(f"⚠️  Evaluation scores not found, skipping Optimization Layer")
            return True
        
        # 1. Prepare DPO training data
        with open(CSV_FILE, "rb") as f:
            files = [("corpora_info", ("scores.csv", f, "text/csv"))]
            data = {
                "item_name": ITEM_NAME,
                "base_model_path": "/path/to/base/model",
                "SFT_adapter_path": "/path/to/sft/adapter"
            }
            response = requests.post(f"{BASE_URL}/prepare-training", files=files, data=data)
        
        if response.status_code != 200:
            raise RuntimeError(f"Prepare training failed: {response.text}")
        
        # 2. Start DPO training
        response = requests.post(
            f"{BASE_URL}/run-training",
            json={"item_name": ITEM_NAME, "gpu_ids": [0, 1]}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Run training failed: {response.text}")
        
        print("✅ Optimization Layer started. DPO training in progress...")
        return True
    except Exception as e:
        print(f"❌ Optimization Layer failed: {e}")
        return False


def main():
    """Main program: Run 7 layers in sequence"""
    print("\n" + "="*60)
    print("RLM-Agent Seven-Layer Pipeline")
    print("="*60)
    print("Order: Learning → Generating → RecipeQA → Fine-Tuning → Reasoning → Evaluation → Optimization")
    print("="*60)
    
    # Run 7 layers
    layers = [
        ("Learning", run_learning_layer),
        ("Generating", run_generating_layer),
        ("RecipeQA", run_recipeqa_layer),
        ("Fine-Tuning", run_fine_tuning_layer),
        ("Reasoning", run_reasoning_layer),
        ("Evaluation", run_evaluation_layer),
        ("Optimization", run_optimization_layer)
    ]
    
    results = {}
    for layer_name, layer_func in layers:
        success = layer_func()
        results[layer_name] = success
        
        # If a layer fails, choose whether to continue
        if not success:
            print(f"\n⚠️  {layer_name} layer failed. Continue to next layer? (y/n)")
            # Auto continue to next layer
            continue
    
    # Summary
    print("\n" + "="*60)
    print("Pipeline Execution Summary")
    print("="*60)
    for layer_name, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"{layer_name}: {status}")
    
    total_success = sum(1 for s in results.values() if s)
    print(f"\nTotal: {total_success}/{len(layers)} layers completed successfully.")
    print("="*60)


if __name__ == "__main__":
    main()