import os.path as osp

from .generating_single_var import generate_single_var
from .get_single_var_diff_class import get_single_var_diff_class
from .merge_results import merge_results
from ..cleaning.preprocess import preprocess
from ..cleaning.remove_abnormal import remove_abnormal


def run_cleaning(process_root: str, src_file_name: str = ""):
    """
    数据清洗阶段：去除异常样本并进行去重处理

    Args:
        process_root (str): 处理目录路径
        src_file_name (str): 源文件名

    Returns:
        dict: 清洗后生成的文件路径信息
    """
    # Step 1: 去除异常样本
    src_file = osp.join(process_root, src_file_name)
    output_file = osp.join(process_root, "re_formula_remove_abnormal.csv")
    remove_abnormal(src_file, output_file)
    print("Remove abnormal finished")

    # Step 2: 去重处理
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


def run_matching(process_root: str, cleaning_result: dict = None):
    """
    匹配与分类阶段：生成单变量匹配对并进行差异分类

    Args:
        process_root (str): 处理目录路径
        cleaning_result (dict, optional): 清洗阶段的结果，包含 dedup 文件路径
                                       如果为 None，则使用默认路径
    """
    # 如果未提供清洗结果，使用默认路径
    if cleaning_result is None:
        formula_dedup_path = osp.join(process_root, "re_formula_dedup.csv")
        fp_dedup_path = osp.join(process_root, "re_fp_dedup.csv")
    else:
        formula_dedup_path = cleaning_result["formula_dedup_path"]
        fp_dedup_path = cleaning_result["fp_dedup_path"]

    # Step 3: 生成单变量匹配对
    formula_output_dir = osp.join(process_root, "formula", "date")
    fp_output_dir = osp.join(process_root, "fp", "date")
    generate_single_var(
        fp_dedup_path, formula_dedup_path, fp_output_dir, formula_output_dir
    )
    print("Generate single var finished")

    # Step 4: 合并结果
    merge_results(osp.join(process_root, "formula"), osp.join(process_root, "fp"))
    print("Merge results finished")

    # Step 5: 获取差异分类
    get_single_var_diff_class(
        osp.join(process_root, "formula"), osp.join(process_root, "fp")
    )
    print("Get single var diff class finished")


def run(process_root: str, src_file_name: str = ""):
    """
    完整流程：依次执行清洗和匹配两个阶段

    Args:
        process_root (str): 处理目录路径
        src_file_name (str): 源文件名
    """
    # 阶段 1: 数据清洗
    print("=" * 50)
    print("阶段 1: 数据清洗")
    print("=" * 50)
    cleaning_result = run_cleaning(process_root, src_file_name)

    # 阶段 2: 匹配与分类
    print("\n" + "=" * 50)
    print("阶段 2: 匹配与分类")
    print("=" * 50)
    run_matching(process_root, cleaning_result)


if __name__ == "__main__":
    work_dir = "D:\\pycharmpro\\1027manus\\OpenManus\\app\\tool\\WIT\\learning\\robotic_learning\\single_var_matching"
    src_file_name = "50764.xlsx"
    run(work_dir, src_file_name)
