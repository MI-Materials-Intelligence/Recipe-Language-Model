import os.path as osp
from typing import Optional

from .generating_single_var import generate_single_var
from .get_single_var_diff_class import get_single_var_diff_class
from .merge_results import merge_results
from ..cleaning.preprocess import preprocess
from ..cleaning.remove_abnormal import remove_abnormal


def run_cleaning(process_root: str, src_file_name: str = "") -> dict:
    """Data Cleaning Stage: Remove abnormal samples and perform deduplication.
    
    Args:
        process_root: Processing directory path.
        src_file_name: Source file name (default: empty string).
        
    Returns:
        Dictionary containing file paths:
            - formula_dedup_path: Path to formula-deduplicated CSV
            - fp_dedup_path: Path to full-process-deduplicated CSV
            - no_dedup_path: Path to non-deduplicated CSV with group IDs
    """
    src_file = osp.join(process_root, src_file_name)
    output_file = osp.join(process_root, "re_formula_remove_abnormal.csv")
    remove_abnormal(src_file, output_file)
    print("Remove abnormal finished")

    formula_dedup_path = osp.join(process_root, "re_formula_dedup.csv")
    fp_dedup_path = osp.join(process_root, "re_fp_dedup.csv")
    no_dedup_path = osp.join(process_root, "re_no_dedup.csv")
    preprocess(output_file, formula_dedup_path, fp_dedup_path, no_dedup_path)
    print("Preprocess finished")

    return {
        "formula_dedup_path": formula_dedup_path,
        "fp_dedup_path": fp_dedup_path,
        "no_dedup_path": no_dedup_path
    }


def run_matching(process_root: str, cleaning_result: Optional[dict] = None) -> None:
    """Matching and Classification Stage: Generate single variable matching pairs and classify differences.
    
    Args:
        process_root: Processing directory path.
        cleaning_result: Optional dictionary containing dedup file paths from cleaning stage.
                       If None, uses default paths.
                       
    Returns:
        None
    """
    if cleaning_result is None:
        formula_dedup_path = osp.join(process_root, "re_formula_dedup.csv")
        fp_dedup_path = osp.join(process_root, "re_fp_dedup.csv")
    else:
        formula_dedup_path = cleaning_result["formula_dedup_path"]
        fp_dedup_path = cleaning_result["fp_dedup_path"]

    formula_output_dir = osp.join(process_root, "formula", "date")
    fp_output_dir = osp.join(process_root, "fp", "date")
    generate_single_var(
        fp_dedup_path, formula_dedup_path, fp_output_dir, formula_output_dir
    )
    print("Generate single var finished")

    merge_results(osp.join(process_root, "formula"), osp.join(process_root, "fp"))
    print("Merge results finished")

    get_single_var_diff_class(
        osp.join(process_root, "formula"), osp.join(process_root, "fp")
    )
    print("Get single var diff class finished")


def run(process_root: str, src_file_name: str = "") -> None:
    """Complete Workflow: Execute cleaning and matching stages sequentially.
    
    Args:
        process_root: Processing directory path.
        src_file_name: Source file name (default: empty string).
        
    Returns:
        None
    """
    print("=" * 50)
    print("Stage 1: Data Cleaning")
    print("=" * 50)
    cleaning_result = run_cleaning(process_root, src_file_name)

    print("\n" + "=" * 50)
    print("Stage 2: Matching and Classification")
    print("=" * 50)
    run_matching(process_root, cleaning_result)



