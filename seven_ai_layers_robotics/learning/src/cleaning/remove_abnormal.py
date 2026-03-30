import re

import pandas as pd

def parse_formula_column(df: pd.DataFrame, column_name: str = "Formula PVK") -> pd.DataFrame:
    """
    Parses a chemical formula column in the format <Element><Value> (e.g., Cs0.08MA0.22...)
    and extracts the values of six specific elements (Cs, MA, FA, Pb, I, Br) into new columns.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame containing the formula column.
        column_name (str): Name of the column containing the formula strings.
    
    Returns:
        pd.DataFrame: The original DataFrame with six new columns added for each element.
    """
    # Define the target elements
    target_elements = ['Cs', 'MA', 'FA', 'Pb', 'I', 'Br']
    
    # Compile a regex pattern to match element-value pairs
    pattern = re.compile(r'(Cs|MA|FA|Pb|I|Br)([0-9.]+)')
    
    # Function to extract element values from a formula string
    def extract_elements(formula: str) -> dict:
        matches = pattern.findall(formula)
        element_dict = {elem: float(val) for elem, val in matches}
        # Ensure all elements are present, fill missing with 0
        for elem in target_elements:
            element_dict.setdefault(elem, 0.0)
        return element_dict
    
    # Apply extraction to each row and create a new DataFrame
    element_data = df[column_name].apply(extract_elements).apply(pd.Series)
    
    # Concatenate original DataFrame with new element columns
    result_df = pd.concat([df, element_data[target_elements]], axis=1)
    
    return result_df


def load_data_with_encoding_fallback(file_path):
    """
    Load data file with multiple encoding attempts to avoid UnicodeDecodeError.
    
    Args:
        file_path (str): Path to the data file
        
    Returns:
        pd.DataFrame: Loaded dataframe
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    last_error = None
    
    for encoding in encodings:
        try:
            return pd.read_excel(file_path)
        except UnicodeDecodeError as e:
            last_error = e
    
    raise last_error


def create_validation_mask_by_sample_no(df):
    """
    Create validation masks for different sample No ranges based on specific criteria.
    
    Args:
        df (pd.DataFrame): Input dataframe containing the data
        
    Returns:
        tuple: Tuple containing the validation mask and individual range masks
    """
    # Define validation criteria for different No ranges
    validation_criteria = [
        {
            'range': (0, 7680),
            'pce_range': (10, 18),
            'ff_range': (50, 90),
            'voc_range': (0.9, 1.15),
            'jsc_range': (15, 24)
        },
        {
            'range': (7681, 32960),
            'pce_range': (10, 23.5),
            'ff_range': (50, 90),
            'voc_range': (0.9, 1.19),
            'jsc_range': (15, 25.5)
        },
        {
            'range': (32961, 42420),
            'pce_range': (10, 25.56),
            'ff_range': (50, 90),
            'voc_range': (0.9, 1.19),
            'jsc_range': (15, 26.5)
        },
        {
            'range': (42421, 50764),
            'pce_range': (10, 27.0),
            'ff_range': (50, 90),
            'voc_range': (0.9, 1.22),
            'jsc_range': (15, 26.7)
        }
    ]
    
    # Initialize masks
    validation_mask = pd.Series(False, index=df.index)
    range_masks = {}
    
    for criteria in validation_criteria:
        range_start, range_end = criteria['range']
        pce_min, pce_max = criteria['pce_range']
        ff_min, ff_max = criteria['ff_range']
        voc_min, voc_max = criteria['voc_range']
        jsc_min, jsc_max = criteria['jsc_range']
        
        # Create mask for current range
        range_mask = (
            (df["No"] >= range_start) & (df["No"] <= range_end) &
            (df["PCE"] > pce_min) & (df["PCE"] < pce_max) &
            (df["FF"] > ff_min) & (df["FF"] < ff_max) &
            (df["Voc"] > voc_min) & (df["Voc"] < voc_max) &
            (df["Jsc"] > jsc_min) & (df["Jsc"] < jsc_max)
        )
        
        range_masks[f"range_{range_start}_{range_end}"] = range_mask
        validation_mask = validation_mask | range_mask
    
    return validation_mask, range_masks

def remove_abnormal(input_path: str, output_path: str):
    """
    Remove abnormal samples from the dataset based on predefined criteria.
    
    Args:
        input_path (str): Path to the input data file
        output_path (str): Path to save the filtered data file
    """
    df = load_data_with_encoding_fallback(input_path)
    
    # Store original row count
    original_rows = len(df)
    
    # === 2. Create validation masks based on No ranges ===
    validation_mask, range_masks = create_validation_mask_by_sample_no(df)
    
    # === 3. Apply filtering ===
    df_filtered = df[validation_mask].copy()
    filtered_rows = len(df_filtered)
    removed_rows = original_rows - filtered_rows
    
    # === 4. Calculate statistics for each range ===
    range_stats = {}
    for range_name, mask in range_masks.items():
        range_stats[range_name] = mask.sum()
    
    # === 5. Print statistics ===
    print("✅ Filtering Statistics:")
    print(f"📊 Original dataset rows: {original_rows}")
    print(f"✅ Valid samples after filtering: {filtered_rows}")
    print(f"❌ Removed samples: {removed_rows}")
    print("\n📈 Samples by No range:")
    
    for range_name, count in range_stats.items():
        # Format range name for better readability
        clean_range_name = range_name.replace('range_', 'No ').replace('_', '-')
        print(f"   {clean_range_name}: {count} samples")

    # === 6. Parse chemical formula column and add element columns ===
    df_filtered = parse_formula_column(df_filtered, column_name="Formula PVK")
    
    # === 7. Save results ===
    df_filtered.to_csv(output_path, index=False)
    print(f"\n💾 Filtered data saved to: {output_path}")


def main():
    """Main function to process and filter the dataset."""
    # === 1. Load data ===
    input_path = r"/data/sunyao/Workspace/Projects/Reasoning/data/src/latest_50764/50764-qiyuan.xlsx"
    df = load_data_with_encoding_fallback(input_path)
    
    # Store original row count
    original_rows = len(df)
    
    # === 2. Create validation masks based on No ranges ===
    validation_mask, range_masks = create_validation_mask_by_sample_no(df)
    
    # === 3. Apply filtering ===
    df_filtered = df[validation_mask].copy()
    filtered_rows = len(df_filtered)
    removed_rows = original_rows - filtered_rows
    
    # === 4. Calculate statistics for each range ===
    range_stats = {}
    for range_name, mask in range_masks.items():
        range_stats[range_name] = mask.sum()
    
    # === 5. Print statistics ===
    print("✅ Filtering Statistics:")
    print(f"📊 Original dataset rows: {original_rows}")
    print(f"✅ Valid samples after filtering: {filtered_rows}")
    print(f"❌ Removed samples: {removed_rows}")
    print("\n📈 Samples by No range:")
    
    for range_name, count in range_stats.items():
        # Format range name for better readability
        clean_range_name = range_name.replace('range_', 'No ').replace('_', '-')
        print(f"   {clean_range_name}: {count} samples")

    # === 6. Parse chemical formula column and add element columns ===
    df_filtered = parse_formula_column(df_filtered, column_name="Formula PVK")
    
    # === 7. Save results ===
    output_path = '/data/sunyao/Workspace/Projects/Reasoning/data/src/latest_50764/re_formula_remove_abnormal.csv'
    df_filtered.to_csv(output_path, index=False)
    print(f"\n💾 Filtered data saved to: {output_path}")


if __name__ == "__main__":
    main()