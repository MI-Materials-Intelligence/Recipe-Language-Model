import json
import os
import re
from typing import Any, Dict, List, Optional, Union


def get_immediate_subdirectories(path: str) -> List[str]:
    """Returns a list of immediate subdirectories for the given path.

    This function lists all directories that are directly under the specified
    path (i.e., one level deep). It does not recurse into subdirectories.

    Args:
        path (str): The absolute or relative path to the directory.

    Returns:
        List[str]: A list of names of immediate subdirectories.

    Raises:
        FileNotFoundError: If the specified path does not exist.
        NotADirectoryError: If the specified path is not a directory.
        PermissionError: If the program lacks permissions to access the path.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"The path '{path}' does not exist.")
    if not os.path.isdir(path):
        raise NotADirectoryError(f"The path '{path}' is not a directory.")

    try:
        return [entry.name for entry in os.scandir(path) if entry.is_dir()]
    except PermissionError as e:
        raise PermissionError(f"Permission denied: {e.filename}") from e


def clean_text(text: str) -> str:
    """
    Removes all bold markdown patterns (**...**) and colons from the input text.

    Args:
        text (str): The input string.

    Returns:
        str: Cleaned string with **<content>** and colons removed.
    """
    text = re.sub(r"\*\*.*?\*\*", "", text)
    text = text.replace(":", "")
    return text.strip()


def read_jsonl(file_path: str) -> List[Dict]:
    """
    Reads a JSON Lines (.jsonl) file and returns a list of dictionaries.

    Args:
        file_path (str): Path to the .jsonl file.

    Returns:
        List[Dict]: A list of dictionaries, each representing a JSON object from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If any line in the file is not valid JSON.
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Error parsing JSON on line {line_number}: {e.msg}",
                        e.doc,
                        e.pos,
                    )
    return data


ITEM_FIELDS = {
    "Title",
    "Field",
    "Parameter",
    "Baseline Value",
    "Optimized Value",
    "\u0394 (delta)",
    "mechanism chain",
}


def item_format_check(data: dict) -> Optional[dict | bool]:
    data_keys = data.keys()
    if set(data_keys).intersection(ITEM_FIELDS) != ITEM_FIELDS:
        return False

    mechanism_chain = data["mechanism chain"]

    if len(mechanism_chain) not in [3, 4]:
        return False

    result_mc = []
    for m_sen in mechanism_chain:
        cleaned_text = clean_text(m_sen)
        if clean_text:
            result_mc.append(cleaned_text)

    if len(result_mc) in [3, 4]:
        return {
            "different_item": data["Title"],
            "field": data["Field"],
            "parameter": data["Parameter"],
            "baseline_value": data["Baseline Value"],
            "optimized_value": data["Optimized Value"],
            "\u0394_(delta)": data["\u0394 (delta)"],
            "mechanism_chain": result_mc,
        }
    else:
        return False


def parse_output_content(text):
    # Extract content inside <output> tags
    match = re.search(r"<output>(.*?)</output>", text, re.DOTALL)
    if not match:
        return []

    content = match.group(1).strip()

    # Split into paragraphs (by double newlines)
    sections = [section.strip() for section in content.split("\n\n") if section.strip()]

    result = []

    for section in sections:
        lines = section.splitlines()
        if not lines:
            continue

        # If "### mechanism chain", process mechanism descriptions
        if lines[0].startswith("###"):
            mechanism_title = lines[0].replace("###", "").strip()
            mechanism_points = []
            for line in lines[1:]:
                line = line.strip("- ").strip()
                if line:
                    mechanism_points.append(line)

            # Add to the last entry
            if result:
                result[-1][mechanism_title] = mechanism_points
                # If starts with ##, indicates a new paragraph
        elif lines[0].startswith("##"):
            entry = {"Title": lines[0].replace("##", "").strip()}

            # Parse subsequent fields
            for line in lines[1:]:
                field_match = re.match(r"-\s+\*\*(.+?)\*\*:\s+(.+)", line)
                if field_match:
                    key = field_match.group(1).strip()
                    value = field_match.group(2).strip()
                    entry[key] = value

            result.append(entry)

    return result


def extract_markdown_blocks(
    text: str, first_only: bool = False
) -> list[str] | str | None:
    """
    Extracts content inside ```markdown ... ``` blocks from the given text.

    Args:
        text (str): The input text.
        first_only (bool): If True, return only the first markdown block as a string.
                           If False, return a list of all markdown blocks.

    Returns:
        str | list[str] | None: Extracted markdown content(s), or None if not found.
    """
    # Regex pattern to match ```markdown ... ```
    pattern = r"<answer>\s*(.*?)\s*<answer>"

    # Use re.DOTALL to match newlines inside the block
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        return None

    return matches[0] if first_only else matches


def parse_markdown_table(markdown: str):
    """
    Parses a markdown table into a list of dictionaries.

    Args:
        markdown (str): The markdown table as a string.

    Returns:
        list[dict]: List of rows as dictionaries.
    """
    lines = [line.strip() for line in markdown.strip().split("\n") if line.strip()]

    # Find header line (first line starting and ending with '|')
    header_line = next(
        (line for line in lines if line.startswith("|") and line.endswith("|")), None
    )
    if not header_line:
        raise ValueError("No valid markdown table header found.")

    headers = [h.strip() for h in header_line.strip("|").split("|")]

    # Skip header and separator line
    start_idx = lines.index(header_line) + 2
    data_lines = lines[start_idx:]

    table = []
    for line in data_lines:
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        # Pad cells if some are missing
        while len(cells) < len(headers):
            cells.append("")
        row = dict(zip(headers, cells))
        table.append(row)

    return table


def markdown_to_json(md_text):
    lines = md_text.strip().splitlines()
    data = {"differences": [], "mechanism_analysis": {}}

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Parse Differences table
        if line.lower().startswith("## differences"):
            # Skip header and separator lines
            i += 3
            while i < len(lines) and lines[i].strip():
                row = [cell.strip() for cell in lines[i].split("|")[1:-1]]
                data["differences"].append(
                    {
                        "field": row[0],
                        "parameter": row[1],
                        "baseline_value": row[2],
                        "optimized_value": row[3],
                        "delta": row[4],
                    }
                )
                i += 1

        # Parse Mechanism Analysis
        elif line.lower().startswith("## mechanism analysis"):
            i += 1
            while i < len(lines):
                line = lines[i].strip()
                # Detect subsection title
                if line.startswith("### "):
                    section_title = line[4:].strip()
                    mechanism_list = []
                    i += 1
                    while i < len(lines) and lines[i].strip().startswith(
                        tuple("123456789")
                    ):
                        # Remove list number and dot
                        item = re.sub(r"^\d+\.\s*", "", lines[i].strip())
                        mechanism_list.append(item)
                        i += 1
                    data["mechanism_analysis"][section_title] = mechanism_list
                else:
                    i += 1
        else:
            i += 1

    return data


def save_txt(content: str, file_path: str, encoding: str = "utf-8") -> None:
    """
    Save a string to a .txt file.

    Args:
        content (str): The string content to save.
        file_path (str): The path to the output .txt file.
        encoding (str): Text encoding (default is 'utf-8').

    Returns:
        None
    """
    try:
        with open(file_path, "w", encoding=encoding) as file:
            file.write(content)
        print(f"Content successfully saved to '{file_path}'")
    except Exception as e:
        print(f"Failed to save file: {e}")


def contains_target_expression(
    text: str, patterns: Optional[List[str]] = None, case_sensitive: bool = False
) -> bool:
    """
    Check whether the input text contains any of the target expressions.

    Args:
        text (str): The input string to search in.
        patterns (Optional[List[str]]): A list of target expressions to match.
            Defaults to ["Experiment 1", "Experiment 2", "SAM1", "SAM2"].
        case_sensitive (bool): Whether the match should be case-sensitive.
            Defaults to False.

    Returns:
        bool: True if any of the target expressions are found in the text, False otherwise.

    Example:
        >>> contains_target_expression("We ran Experiment 2 yesterday.")
        True

        >>> contains_target_expression("we tested sam1", case_sensitive=False)
        True

        >>> contains_target_expression("We tested Sam3")
        False
    """
    if patterns is None:
        patterns = [
            "Experiment 1",
            "Experiment 2",
            "SAM1",
            "SAM2",
            "SAM 2",
            "SAM 1",
            "Experiment1",
            "Experiment2",
        ]

    flags = 0 if case_sensitive else re.IGNORECASE

    for pattern in patterns:
        # Escape special characters and use word boundaries
        escaped = re.escape(pattern)
        if re.search(rf"\b{escaped}\b", text, flags=flags):
            return True
    return False


def sort_json_files_by_number(file_paths: List[str]) -> List[str]:
    """
    Sort a list of JSON file paths based on the numeric value in the filename.

    Assumes filenames are in the form of '<number>.json', e.g., '0.json', '10.json'.

    Args:
        file_paths (List[str]): List of JSON file paths.

    Returns:
        List[str]: Sorted list of file paths based on numeric filename.
    """

    def extract_number(file_path: str) -> int:
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        return int(name_without_ext)

    return sorted(file_paths, key=extract_number)


def get_formatted_result(data: Dict, meta_info: Dict) -> List[Dict]:
    result = []

    if "mechanism_analysis" not in data:
        return result

    for chain_name, chain in data["mechanism_analysis"].items():

        state_validation = True
        for statement in chain:
            if contains_target_expression(statement):
                state_validation = False

        if state_validation:

            result.append(
                {
                    "answer": " ".join(chain),
                    "meta_data": {"chain_name": chain_name, **meta_info},
                }
            )
    return result


def save_list_to_jsonl(
    data: List[Union[Dict, list]], output_path: str, ensure_ascii: bool = False
) -> None:
    """
    Save a list of dictionaries or lists to a .jsonl (JSON Lines) file.

    Args:
        data (List[Union[Dict, list]]): A list where each item is a JSON-serializable object (dict or list).
        output_path (str): The file path where the .jsonl file will be saved.
        ensure_ascii (bool): Whether to escape non-ASCII characters. Default is False (UTF-8).

    Returns:
        None
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for item in data:
            json_line = json.dumps(item, ensure_ascii=ensure_ascii)
            f.write(json_line + "\n")


def get_all_json_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Get a list of all .json files in the specified directory.

    Args:
        directory (str): The path to the directory to search in.
        recursive (bool): Whether to search subdirectories recursively. Default is True.

    Returns:
        List[str]: A list of full paths to .json files.
    """
    json_files = []

    if recursive:
        # Walk through directory tree
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".json"):
                    full_path = os.path.join(root, file)
                    json_files.append(full_path)
    else:
        # List files in the top-level directory only
        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path) and file.lower().endswith(".json"):
                json_files.append(full_path)

    return json_files


def read_json(file_path: str) -> Union[list | dict]:
    """
    Read json file and return its content.

    Args:
        file_path (str): file path of json file.

    Returns:
        dict | list: data from json file.

    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error occurred when reading json: {e}")
        return None


def convert_list_to_dict(data: list):
    result = []

    for i, d in enumerate(data):
        result.append({"id": str(i), "content": d})
    return result


def list_to_markdown_table(data_list: list) -> str:
    """
    Convert data list into string of markdown format.

    Args:
        data_list (list): the list contains dict

    Returns:
        str: string of markdown format.
    """
    if not data_list:
        return ""

    if not isinstance(data_list[0], dict):
        data_list = convert_list_to_dict(data_list)

    headers = list(data_list[0].keys())
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"

    rows = []
    for item in data_list:
        row = "| " + " | ".join(str(item.get(h, "")) for h in headers) + " |"
        rows.append(row)

    return "\n".join([header_line, separator_line] + rows) + "\n"


def json_to_markdown(data: Union[dict, list], level: int = 1, prefix: str = "") -> str:
    """

    Convert json data into markdown-formatted string recursively.

    Args:
        data (dict | list): Json data
        level (int): level of markdown title
        prefix (str): prefix for the current field path

    Returns:
        str: Markdown-formatted string
    """
    markdown = ""
    indent = "#" * level

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            markdown += f"\n{indent} {key}\n"
            if isinstance(value, list) and value:
                markdown += list_to_markdown_table(value) + "\n"
            elif isinstance(value, (dict, list)):
                markdown += json_to_markdown(value, level + 1, new_prefix)
            else:
                markdown += f"{value}\n"
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            markdown += f"\n{indent} {prefix}[{idx}]\n"
            markdown += json_to_markdown(item, level + 1, prefix)
    else:
        markdown += f"\n{indent} {prefix}\n{data}\n"

    return markdown


def convert_json_file_to_md(json_file_path: str, md_file_path: str) -> None:
    """
    Convert Json file into markdown file.

    Args:
        json_file_path (str): the file path of input Json file.
        md_file_path (str): the file path of output markdown file
    """
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        markdown_content = json_to_markdown(data)

        with open(md_file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"Markdown file has been saved to: {md_file_path}")
    except Exception as e:
        print(f"Error occurred when converting json file into markdown file: {e}")


def save_json(data: Any, file_path: str, indent: int = 4) -> None:
    """
    Save data to a JSON file.

    Args:
        data (Any): The data to serialize and save in JSON format.
        file_path (str): The path where the JSON file will be saved.
        indent (int, optional): Number of spaces for indentation in the JSON file. Defaults to 4.

    Raises:
        TypeError: If the data is not serializable to JSON.
        OSError: If there is an error writing to the file system.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        print(f"JSON saved successfully to '{file_path}'.")

    except TypeError as e:
        raise TypeError(f"Data provided is not JSON serializable: {e}")
    except OSError as e:
        raise OSError(f"Error writing JSON to file: {e}")
