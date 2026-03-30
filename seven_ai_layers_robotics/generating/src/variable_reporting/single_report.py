# -*- coding: utf-8 -*-
"""
Perovskite Report Generator
Generate structured scientific research reports (Abstract + Introduction + Results & Discussion + Conclusion Table + Supporting Information)

Use DashScope OpenAI-compatible API to generate Abstract and Conclusion Table.

✅ Single-file encapsulation | ✅ Externally callable | ✅ Sync/async compatible
"""

import json
import re
import os
from pathlib import Path
from typing import Any, Dict, Tuple, List, Optional
from dataclasses import dataclass, field
from openai import OpenAI

# Import configuration loader
import sys
from pathlib import Path as PathLib
script_dir = PathLib(__file__).parent
# Add generating/src to sys.path to use config_loader under Generating
generating_src = script_dir.parent  # Variable_Reporting -> generating/src
if str(generating_src) not in sys.path:
    sys.path.insert(0, str(generating_src))

# Import configuration from app.config
from seven_ai_layers_robotics.config import config


# ============================================================================
# 📋 Configuration Class (supports dict/code override)
# ============================================================================

@dataclass
class ReportConfig:
    """Report generation configuration"""
    # DashScope API configuration (loaded from config file)
    api_key: str = None  # 🔐 Modify as needed
    base_url: str = None
    model: str = "qwen-plus"

    def __post_init__(self):
        """Load default values from app.config after initialization"""
        if self.api_key is None or self.base_url is None:
            cfg = {
                'api_key': config.generating_llm.dashscope_api_key,
                'base_url': config.generating_llm.base_url,
                'model': config.generating_llm.dashscope_model,
            }
            if self.api_key is None:
                object.__setattr__(self, 'api_key', cfg.get('api_key', ''))
            if self.base_url is None:
                object.__setattr__(self, 'base_url', cfg.get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1  '))
            if self.model == "qwen-plus":  # If not explicitly set, use model from config file
                object.__setattr__(self, 'model', cfg.get('model', 'qwen-plus'))

        # Convert relative paths to absolute paths relative to Generating directory after initialization
        generating_dir = PathLib(__file__).resolve().parents[2]

        # Path configuration
        object.__setattr__(self, 'task_json_path', str(generating_dir / "data\\tasks_from_db.json"))
        object.__setattr__(self, 'answer_folder', str(generating_dir / "data\\single"))  # single directory
        object.__setattr__(self, 'output_dir', str(generating_dir / "data\\ReportJSON"))

    # Generation options
    skip_if_no_result: bool = True  # If Result_Discussion is empty, skip Abstract/Table generation

    @classmethod
    def from_dict(cls, cfg: Optional[Dict[str, Any]]) -> "ReportConfig":
        if not cfg:
            return cls()
        return cls(**{k: v for k, v in cfg.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, json_path: str) -> "ReportConfig":
        with open(json_path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


# ============================================================================
# 🔧 Utility Functions
# ============================================================================

def read_json(p: Path) -> Any:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def write_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def extract_digits(s: Any) -> str:
    """Extract digits from '38847,control device' / '38847' / 38847 → '38847'"""
    if s is None:
        return ""
    s = str(s).strip()
    m = re.search(r"\d+", s)
    return m.group(0) if m else ""

def find_answer_part(obj: Any) -> List[str]:
    """Recursively extract all answer_part fields"""
    found: List[str] = []
    if isinstance(obj, dict):
        if "answer_part" in obj:
            ap = obj.get("answer_part")
            if isinstance(ap, str) and ap.strip():
                found.append(ap.strip())
        for v in obj.values():
            found.extend(find_answer_part(v))
    elif isinstance(obj, list):
        for it in obj:
            found.extend(find_answer_part(it))
    return found

def extract_answer_part_from_json(data: Any) -> str:
    """Extract and deduplicate answer_part from potentially nested dict/list"""
    parts = find_answer_part(data)
    seen, uniq = set(), []
    for p in parts:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return "\n\n".join(uniq).strip()

def parse_answer_filename(stem: str) -> Tuple[str, str]:
    """Parse answer filename → (id1, id2)"""
    if "_" not in stem:
        return (extract_digits(stem), "")
    a, b = stem.split("_", 1)
    return (extract_digits(a), extract_digits(b))

def build_answer_index_by_pair(answer_dir: Path) -> Dict[Tuple[str, str], str]:
    """Build (id1, id2) → answer_part index"""
    idx: Dict[Tuple[str, str], str] = {}
    for fp in sorted(answer_dir.glob("*.json")):
        id1, id2 = parse_answer_filename(fp.stem)
        try:
            data = read_json(fp)
        except Exception as e:
            print(f"⚠️ Answer JSON read failed: {fp.name} err={e}")
            continue
        answer_part = extract_answer_part_from_json(data)
        idx[(id1, id2)] = answer_part
    return idx


# ============================================================================
# 🤖 DashScope LLM Wrapper
# ============================================================================

class DashScopeLLM:
    """DashScope OpenAI-compatible API client"""

    def __init__(self, config: ReportConfig):
        if not config.api_key or config.api_key.startswith("sk-xxx"):
            raise ValueError("Please configure a valid DASHSCOPE_API_KEY")

        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url.rstrip("/")
        )
        self.model = config.model

    def _chat_stream(self, system_prompt: str, user_prompt: str) -> Tuple[str, str]:
        """Stream call, return (answer_content, reasoning_content)"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            extra_body={"enable_thinking": True},
            stream=True,
        )

        reasoning_content, answer_content = "", ""
        for chunk in completion:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                reasoning_content += delta.reasoning_content
            if hasattr(delta, "content") and delta.content:
                answer_content += delta.content

        return answer_content.strip(), reasoning_content.strip()

    def generate_abstract(self, method_text: str, result_discussion_text: str) -> str:
        """Generate Abstract (single paragraph, 250-300 words)"""
        system = (
            "You are a scientific writing assistant and an expert in the field of perovskite solar cells. "
            "Your task is to write an English ABSTRACT for a scientific paper (250–300 words) based only on the information provided by the user. "
            "FORMATTING RULES (MUST OBEY): "
            "• Output MUST be ONE SINGLE PARAGRAPH of continuous plain text. "
            "• Do NOT insert any headings, titles, section labels, Markdown (no '###', no bold, no lists). "
            "• Do NOT use bullet points or numbered lists. "
            "• Do NOT start with the word 'Abstract' or any title. "
            "• Do NOT insert blank lines or line breaks inside the abstract. "
            "CONTENT REQUIREMENTS: "
            "The abstract should follow this logical structure: "
            "(1) giving the background, briefly mentioning the potential of inverted (p–i–n) perovskite solar cells; "
            "(2) summarizing the key fabrication strategy or core process optimization(s), preferably in a 'from A to B' form (e.g., SAM, passivation agent or additive engineering); "
            "(3) reporting the main performance indicators (PCE, VOC, JSC, FF) and their improvement range. Only mention parameters that show a clear increase; if an index is flat or slightly decreased, do not mention it; "
            "(4) giving concise mechanism insights to explain why the improved recipe outperforms the control, without going into excessive detail; "
            "(5) concluding with the overall significance and potential impact of this optimization. "
            "Be precise and factual; avoid citations, figure/table mentions, and avoid introducing any information that is not supported by the input."
        )

        user = f"""
Method (key fabrication details):
{method_text}

Results & Discussion (performance & mechanisms):
{result_discussion_text}

Now write the ABSTRACT according to the system instructions above.
Output ONLY the abstract text as ONE SINGLE PARAGRAPH of 250–300 words,
with no title, no headings, no bullet points, and no extra line breaks.
Do not add any explanations before or after the abstract.
""".strip()

        answer, _ = self._chat_stream(system, user)
        return answer

    def generate_conclusion_table(self, result_discussion_text: str) -> str:
        """Generate Conclusion Markdown Table"""
        system = r"""
You are a technical writing assistant for perovskite solar cells.

Your ONLY task in this conversation:
- Read the user's input (Result and Discussion).
- Then output ONE Markdown table.

VERY IMPORTANT FORMAT RULES:
- Output ONLY one Markdown table.
- Do NOT output any text before or after the table.
- Do NOT use code fences (no ```).
- Do NOT write headings or paragraphs.

The table MUST have EXACTLY these three columns in this order:
| F/P Optimization | Performance | Mechanism |

ROW RULES:
- Make ONE row for each metric that improved (VOC, JSC, FF, PCE).
- If a metric did not improve, do NOT make a row for it.

COLUMN CONTENT:
- F/P Optimization: describe the key formulation/process change using details from the input
(e.g., replacing PEABr with MACl at 0.7 mg/mL and reducing PSP to 2.0 mg/mL).
- Performance: write "from → to (+gain)" with units, for example:
VOC: 0.99 V → 1.03 V (+0.04 V)
JSC: 22.94 → 23.74 mA cm⁻² (+0.80 mA cm⁻²)
FF: 69.16% → 74.46% (+5.30 pct)
PCE: 15.76% → 18.35% (+2.59 pct)
- Mechanism: Detailed description of the mechanism and reasons for performance changes (e.g., dipole-induced work-function shift, defect passivation, band alignment, recombination suppression.).

DATA:
- Use ONLY numbers and mechanisms from the user's input.
""".strip()

        user = f"""
[REAL INPUT]
Results & Discussion (performance & mechanisms):
{result_discussion_text}

[REAL OUTPUT]
Now, based on the INPUT above, write ONLY the Markdown table.
Start your answer with the header row:
| F/P Optimization | Performance | Mechanism |
""".strip()

        answer, _ = self._chat_stream(system, user)
        return answer


# ============================================================================
# 📄 Report Builder
# ============================================================================

class ReportBuilder:
    """Build a single structured report"""

    @staticmethod
    def build(
        task_item: Dict[str, Any],
        result_discussion: str,
        llm: Optional[DashScopeLLM] = None,
        skip_if_empty: bool = True,
    ) -> Dict[str, Any]:
        meta_info = task_item.get("meta_info") or {}
        control_fp = task_item.get("control_device_fabrication", "") or ""
        optimized_fp = task_item.get("target_device_fabrication", "") or ""
        supporting = (task_item.get("expert_data") or {}).get("summary_text", "") or ""

        method_text = f"{control_fp}\n\n{optimized_fp}".strip()
        rd_text = (result_discussion or "").strip()

        # Conditional generation of Abstract and Table
        abstract, table_md = "", ""
        # if llm and method_text and rd_text and not skip_if_empty:
        print(llm)
        print(rd_text)
        if llm and method_text and rd_text:
            abstract = llm.generate_abstract(method_text, rd_text)
            table_md = llm.generate_conclusion_table(rd_text)

        return {
            "source_file": "",
            "meta_info": meta_info,
            "1_Abstract": abstract,
            "2_Introduction": {
                "2_1_Control_F_P": control_fp,
                "2_2_Optimized_F_P": optimized_fp,
            },
            "3_Result_Discussion": rd_text,
            "4_Conclusion": {
                "4_1_Table": table_md,
            },
            "5_Supporting_Information": supporting,
        }


# ============================================================================
# 🚀 Main Entry Class (core for external calls)
# ============================================================================

class ReportGenerator:
    """Report Generator - main entry point"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = ReportConfig.from_dict(config)
        self.llm = DashScopeLLM(self.config)

    def run(self,
            task_json_path: Optional[str] = None,
            answer_folder: Optional[str] = None,
            output_dir: Optional[str] = None) -> Dict[str, int]:
        """
        Execute report generation process

        Parameters:
            task_json_path: Task JSON path (override config)
            answer_folder: Answer file directory (override config)
            output_dir: Output directory (override config)

        Returns:
            Statistics dict: {"total": N, "matched": N, "missing": N, "skipped": N}
        """
        # Apply parameter overrides
        task_path = Path(task_json_path or self.config.task_json_path)
        ans_dir = Path(answer_folder or self.config.answer_folder)
        out_dir = Path(output_dir or self.config.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Load tasks
        task_data = read_json(task_path)
        if not isinstance(task_data, list):
            raise ValueError("task.json top level must be a list")

        # Build answer index
        answer_index = build_answer_index_by_pair(ans_dir)

        # Statistics
        stats = {"total": len(task_data), "matched": 0, "missing": 0, "skipped": 0}

        for i, item in enumerate(task_data):
            if not isinstance(item, dict):
                print(f"⚠️ Skip non-dict task item: index={i}")
                stats["skipped"] += 1
                continue

            meta = item.get("meta_info") or {}
            id1 = extract_digits(meta.get("Sample_ID_1", ""))
            id2 = extract_digits(meta.get("Sample_ID_2", ""))

            if not id1 or not id2:
                print(f"⚠️ task index={i} cannot extract id1/id2")
                stats["missing"] += 1
                continue

            # Exact match + fallback reverse match
            rd = answer_index.get((id1, id2)) or answer_index.get((id2, id1)) or ""

            # Build report
            report = ReportBuilder.build(
                task_item=item,
                result_discussion=rd,
                llm=self.llm,
                skip_if_empty=self.config.skip_if_no_result,
            )

            # Save
            out_path = out_dir / f"{id1}_{id2}.json"
            write_json(out_path, report)

            if rd.strip():
                stats["matched"] += 1
                print(f"✅ {out_path.name}")
            else:
                stats["missing"] += 1
                print(f"⚠️ {out_path.name} (no answer_part)")

        # Summary
        print(f"\n📊 SUMMARY: total={stats['total']}, matched={stats['matched']}, missing={stats['missing']}, skipped={stats['skipped']}")
        print(f"📁 Output: {out_dir.resolve()}")
        return stats

    def rebuild_from_answers(self, answer_folder: str, output_dir: str) -> int:
        """
        Rebuild reports from answer files only (no LLM call, for debugging/re-run)
        Returns the number of generated reports
        """
        ans_dir = Path(answer_folder)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for fp in ans_dir.glob("*.json"):
            id1, id2 = parse_answer_filename(fp.stem)
            if not id1 or not id2:
                continue
            try:
                data = read_json(fp)
                rd = extract_answer_part_from_json(data)
            except:
                continue

            # Build minimal report
            report = {
                "source_file": str(fp),
                "meta_info": {},
                "1_Abstract": "",
                "2_Introduction": {"2_1_Control_F_P": "", "2_2_Optimized_F_P": ""},
                "3_Result_Discussion": rd,
                "4_Conclusion": {"4_1_Table": ""},
                "5_Supporting_Information": "",
            }
            write_json(out_dir / f"{id1}_{id2}.json", report)
            count += 1

        print(f"📄 Rebuilt {count} reports from answers → {out_dir}")
        return count


# ============================================================================
# 🖥️ Command-line Entry (optional)
# ============================================================================

def _parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Perovskite Report Generator")
    parser.add_argument("--config", type=str, help="Config JSON path")
    parser.add_argument("--task", type=str, help="Task JSON path")
    parser.add_argument("--answers", type=str, help="Answer folder path")
    parser.add_argument("--output", type=str, help="Output directory")
    parser.add_argument("--rebuild-only", action="store_true", help="Only rebuild from answers (no LLM)")
    return parser.parse_args()

def main():
    args = _parse_args()
    config = ReportConfig.from_json(args.config) if args.config else ReportConfig()

    if args.task:
        config.task_json_path = args.task
    if args.answers:
        config.answer_folder = args.answers
    if args.output:
        config.output_dir = args.output

    generator = ReportGenerator(config)

    if args.rebuild_only:
        generator.rebuild_from_answers(config.answer_folder, config.output_dir)
    else:
        generator.run()

if __name__ == "__main__":
    main()