# -*- coding: utf-8 -*-
"""Perovskite Report Generator.

Generate structured scientific research reports:
- Abstract
- Introduction
- Results & Discussion
- Conclusion Table
- Supporting Information

Features added:
- ThreadPool parallel execution
- Skip existing report JSON
- Force rerun option
- Progress control
- Range control
- Per-task isolation and error handling
"""

import json
import re
import time
import argparse
from pathlib import Path as PathLib
from pathlib import Path
from typing import Any, Dict, Tuple, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from openai import OpenAI
from seven_ai_layers_robotics.config import config


# =========================
# Config
# =========================

@dataclass
class ReportConfig:
    """Report generation configuration"""
    api_key: str = None
    base_url: str = None
    model: str = "qwen-plus"

    # generation options
    skip_if_no_result: bool = True

    def __post_init__(self):
        if self.api_key is None or self.base_url is None:
            cfg = {
                "api_key": config.generating_llm.dashscope_api_key,
                "base_url": config.generating_llm.base_url,
                "model": config.generating_llm.dashscope_model,
            }
            if self.api_key is None:
                object.__setattr__(self, "api_key", cfg.get("api_key", ""))
            if self.base_url is None:
                object.__setattr__(
                    self,
                    "base_url",
                    cfg.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
                )
            if self.model == "qwen-plus":
                object.__setattr__(self, "model", cfg.get("model", "qwen-plus"))

        generating_dir = PathLib(__file__).resolve().parents[2]

        object.__setattr__(self, "task_json_path", str(generating_dir / "data\\tasks_from_db.json"))
        object.__setattr__(self, "answer_folder", str(generating_dir / "data\\single"))
        object.__setattr__(self, "output_dir", str(generating_dir / "data\\ReportJSON"))

    @classmethod
    def from_dict(cls, cfg: Optional[Dict[str, Any]]) -> "ReportConfig":
        if not cfg:
            return cls()
        return cls(**{k: v for k, v in cfg.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, json_path: str) -> "ReportConfig":
        with open(json_path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


# =========================
# Utils
# =========================

def read_json(p: Path) -> Any:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def extract_digits(s: Any) -> str:
    if s is None:
        return ""
    s = str(s).strip()
    m = re.search(r"\d+", s)
    return m.group(0) if m else ""


def find_answer_part(obj: Any) -> List[str]:
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
    parts = find_answer_part(data)
    seen, uniq = set(), []
    for p in parts:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return "\n\n".join(uniq).strip()


def parse_answer_filename(stem: str) -> Tuple[str, str]:
    if "_" not in stem:
        return (extract_digits(stem), "")
    a, b = stem.split("_", 1)
    return (extract_digits(a), extract_digits(b))


def build_answer_index_by_pair(answer_dir: Path) -> Dict[Tuple[str, str], str]:
    idx: Dict[Tuple[str, str], str] = {}
    for fp in sorted(answer_dir.glob("*.json")):
        id1, id2 = parse_answer_filename(fp.stem)
        try:
            data = read_json(fp)
        except Exception as e:
            print(f"[WARN] Answer JSON read failed: {fp.name} err={e}")
            continue
        answer_part = extract_answer_part_from_json(data)
        idx[(id1, id2)] = answer_part
    return idx


def format_seconds(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# =========================
# LLM
# =========================

class DashScopeLLM:
    """DashScope OpenAI-compatible API client."""

    def __init__(self, cfg: ReportConfig):
        if not cfg.api_key or str(cfg.api_key).startswith("sk-xxx"):
            raise ValueError("Please configure a valid DASHSCOPE_API_KEY")

        self.client = OpenAI(
            api_key=cfg.api_key,
            base_url=cfg.base_url.rstrip("/")
        )
        self.model = cfg.model

    def _chat_stream(self, system_prompt: str, user_prompt: str) -> Tuple[str, str]:
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
            "(2) summarizing the key fabrication strategy or core process optimization(s), preferably in a 'from A to B' form; "
            "(3) reporting the main performance indicators (PCE, VOC, JSC, FF) and their improvement range. "
            "Only mention parameters that show a clear increase; if an index is flat or slightly decreased, do not mention it; "
            "(4) giving concise mechanism insights to explain why the improved recipe outperforms the control; "
            "(5) concluding with the overall significance and potential impact of this optimization. "
            "Be precise and factual; avoid citations, figure/table mentions, and avoid introducing unsupported information."
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
- F/P Optimization: describe the key formulation/process change using details from the input.
- Performance: write "from → to (+gain)" with units.
- Mechanism: detailed description of the mechanism and reasons for performance changes.

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


# =========================
# Builder
# =========================

class ReportBuilder:
    """Build a single structured report."""

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

        abstract, table_md = "", ""

        # 没有结果时是否跳过 LLM 调用
        if skip_if_empty and not rd_text:
            pass
        elif llm and method_text and rd_text:
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


# =========================
# Generator
# =========================

class ReportGenerator:
    """Report Generator - main entry point."""

    def __init__(self, cfg: Optional[Dict[str, Any]] = None):
        self.config = ReportConfig.from_dict(cfg)
        self._lock = Lock()

    def _make_llm(self) -> DashScopeLLM:
        """
        每个任务单独创建 client，避免多线程共享 client 带来的潜在线程安全问题。
        """
        return DashScopeLLM(self.config)

    def _process_one_task(
        self,
        i: int,
        item: Dict[str, Any],
        answer_index: Dict[Tuple[str, str], str],
        out_dir: Path,
        force: bool = False,
    ) -> Dict[str, Any]:
        try:
            if not isinstance(item, dict):
                return {
                    "status": "skipped",
                    "index": i,
                    "msg": f"[SKIP] index={i}: non-dict task item"
                }

            meta = item.get("meta_info") or {}
            id1 = extract_digits(meta.get("Sample_ID_1", ""))
            id2 = extract_digits(meta.get("Sample_ID_2", ""))

            if not id1 or not id2:
                return {
                    "status": "missing",
                    "index": i,
                    "msg": f"[MISS] index={i}: cannot extract id1/id2"
                }

            out_path = out_dir / f"{id1}_{id2}.json"

            # 已有 report 跳过
            if out_path.exists() and not force:
                return {
                    "status": "skipped_existing",
                    "index": i,
                    "msg": f"[SKIP] {out_path.name}: already exists"
                }

            rd = answer_index.get((id1, id2)) or answer_index.get((id2, id1)) or ""

            llm = self._make_llm()

            report = ReportBuilder.build(
                task_item=item,
                result_discussion=rd,
                llm=llm,
                skip_if_empty=self.config.skip_if_no_result,
            )

            write_json(out_path, report)

            if rd.strip():
                return {
                    "status": "matched",
                    "index": i,
                    "msg": f"[OK] {out_path.name}"
                }
            else:
                return {
                    "status": "missing",
                    "index": i,
                    "msg": f"[MISS] {out_path.name}: no answer_part"
                }

        except Exception as e:
            return {
                "status": "error",
                "index": i,
                "msg": f"[ERROR] index={i}: {e}"
            }

    def run(
        self,
        task_json_path: Optional[str] = None,
        answer_folder: Optional[str] = None,
        output_dir: Optional[str] = None,
        max_workers: int = 5,
        force: bool = False,
        start: int = 0,
        end: Optional[int] = None,
        print_every: int = 10,
    ) -> Dict[str, int]:
        """
        Execute report generation process.

        Parameters:
            task_json_path: override task path
            answer_folder: override answer folder
            output_dir: override output folder
            max_workers: thread pool size
            force: whether to rerun existing outputs
            start: start index (inclusive)
            end: end index (exclusive), None means all
            print_every: print progress every N finished tasks

        Returns:
            Statistics dict.
        """
        task_path = Path(task_json_path or self.config.task_json_path)
        ans_dir = Path(answer_folder or self.config.answer_folder)
        out_dir = Path(output_dir or self.config.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        task_data = read_json(task_path)
        if not isinstance(task_data, list):
            raise ValueError("task.json top level must be a list")

        total_all = len(task_data)
        start = max(0, int(start))
        end = total_all if end is None else min(int(end), total_all)
        selected_tasks = task_data[start:end]

        answer_index = build_answer_index_by_pair(ans_dir)

        stats = {
            "total_selected": len(selected_tasks),
            "matched": 0,
            "missing": 0,
            "skipped": 0,
            "skipped_existing": 0,
            "error": 0,
        }

        begin_time = time.time()

        print("=" * 80)
        print("[INFO] Report generation started")
        print(f"[INFO] task_json_path = {task_path}")
        print(f"[INFO] answer_folder   = {ans_dir}")
        print(f"[INFO] output_dir      = {out_dir}")
        print(f"[INFO] total_all       = {total_all}")
        print(f"[INFO] selected_range  = [{start}, {end})")
        print(f"[INFO] total_selected  = {len(selected_tasks)}")
        print(f"[INFO] max_workers     = {max_workers}")
        print(f"[INFO] force           = {force}")
        print(f"[INFO] print_every     = {print_every}")
        print("=" * 80)

        if not selected_tasks:
            print("[INFO] No tasks selected, exit.")
            return stats

        futures = []
        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for local_idx, item in enumerate(selected_tasks):
                global_idx = start + local_idx
                future = executor.submit(
                    self._process_one_task,
                    global_idx,
                    item,
                    answer_index,
                    out_dir,
                    force,
                )
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                status = result["status"]
                msg = result["msg"]

                with self._lock:
                    if status in stats:
                        stats[status] += 1
                    else:
                        stats["error"] += 1

                    completed += 1

                    # 打印单条结果
                    print(msg)

                    # 控制进度打印频率
                    if (completed % max(1, print_every) == 0) or (completed == stats["total_selected"]):
                        elapsed = time.time() - begin_time
                        speed = completed / elapsed if elapsed > 0 else 0.0
                        remaining = stats["total_selected"] - completed
                        eta = remaining / speed if speed > 0 else 0.0

                        print("-" * 80)
                        print(
                            f"[PROGRESS] {completed}/{stats['total_selected']} "
                            f"({completed / stats['total_selected'] * 100:.1f}%) | "
                            f"matched={stats['matched']} | "
                            f"missing={stats['missing']} | "
                            f"skipped={stats['skipped']} | "
                            f"skipped_existing={stats['skipped_existing']} | "
                            f"error={stats['error']} | "
                            f"elapsed={format_seconds(elapsed)} | "
                            f"eta={format_seconds(eta)} | "
                            f"speed={speed:.2f} task/s"
                        )
                        print("-" * 80)

        elapsed = time.time() - begin_time

        print("\n" + "=" * 80)
        print("[SUMMARY]")
        print(f"total_selected   : {stats['total_selected']}")
        print(f"matched          : {stats['matched']}")
        print(f"missing          : {stats['missing']}")
        print(f"skipped          : {stats['skipped']}")
        print(f"skipped_existing : {stats['skipped_existing']}")
        print(f"error            : {stats['error']}")
        print(f"elapsed          : {format_seconds(elapsed)}")
        print(f"output           : {out_dir.resolve()}")
        print("=" * 80)

        return stats

    def rebuild_from_answers(self, answer_folder: str, output_dir: str, force: bool = False) -> int:
        """
        Rebuild reports from answer files only (no LLM call).
        """
        ans_dir = Path(answer_folder)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        skipped_existing = 0

        for fp in ans_dir.glob("*.json"):
            id1, id2 = parse_answer_filename(fp.stem)
            if not id1 or not id2:
                continue

            out_path = out_dir / f"{id1}_{id2}.json"
            if out_path.exists() and not force:
                skipped_existing += 1
                continue

            try:
                data = read_json(fp)
                rd = extract_answer_part_from_json(data)
            except Exception:
                continue

            report = {
                "source_file": str(fp),
                "meta_info": {},
                "1_Abstract": "",
                "2_Introduction": {"2_1_Control_F_P": "", "2_2_Optimized_F_P": ""},
                "3_Result_Discussion": rd,
                "4_Conclusion": {"4_1_Table": ""},
                "5_Supporting_Information": "",
            }
            write_json(out_path, report)
            count += 1

        print(f"[INFO] Rebuilt {count} reports from answers → {out_dir}")
        print(f"[INFO] Skipped existing: {skipped_existing}")
        return count


# =========================
# CLI
# =========================

def _parse_args():
    parser = argparse.ArgumentParser(description="Perovskite Report Generator")
    parser.add_argument("--config", type=str, help="Config JSON path")
    parser.add_argument("--task", type=str, help="Task JSON path")
    parser.add_argument("--answers", type=str, help="Answer folder path")
    parser.add_argument("--output", type=str, help="Output directory")
    parser.add_argument("--rebuild-only", action="store_true", help="Only rebuild from answers (no LLM)")

    # parallel / control
    parser.add_argument("--workers", type=int, default=5, help="Max thread workers")
    parser.add_argument("--force", action="store_true", help="Force regenerate even if report already exists")
    parser.add_argument("--start", type=int, default=0, help="Start index (inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End index (exclusive)")
    parser.add_argument("--print-every", type=int, default=10, help="Print progress every N finished tasks")

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = ReportConfig.from_json(args.config) if args.config else ReportConfig()

    if args.task:
        cfg.task_json_path = args.task
    if args.answers:
        cfg.answer_folder = args.answers
    if args.output:
        cfg.output_dir = args.output

    generator = ReportGenerator(cfg)

    if args.rebuild_only:
        generator.rebuild_from_answers(
            answer_folder=cfg.answer_folder,
            output_dir=cfg.output_dir,
            force=args.force,
        )
    else:
        generator.run(
            task_json_path=cfg.task_json_path,
            answer_folder=cfg.answer_folder,
            output_dir=cfg.output_dir,
            max_workers=args.workers,
            force=args.force,
            start=args.start,
            end=args.end,
            print_every=args.print_every,
        )


if __name__ == "__main__":
    main()