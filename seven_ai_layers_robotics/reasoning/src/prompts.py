"""Prompt templates for perovskite report generation.

This module contains all prompt templates used in the report generation pipeline.
"""

from typing import Dict, Tuple


class ReportPrompts:
    """Prompt templates for perovskite solar cell report generation.

    This class provides standardized prompt templates for generating
    scientific reports on perovskite solar cell research.
    """

    # ========== 1. Formulation Optimization Analysis ==========
    ANALYZE_SYSTEM_PROMPT: str = "You are an expert in perovskite materials."

    ANALYZE_USER_PROMPT_TEMPLATE: str = """Based on the perovskite material formulation and processing parameters, analyze their impact on PCE, FF, Jsc, and Voc, and propose optimization strategies for the formulation to enhance PCE, FF, Jsc, and Voc.
{input_text}
Not writing markdown."""

    # ========== 2. Material Name Extraction ==========
    REWRITE_SYSTEM_PROMPT: str = "You are an expert in the field of chemistry."

    REWRITE_USER_PROMPT_TEMPLATE: str = """Results & Discussion (performance & mechanisms):
{answer_content_analyze}

What is the optimized material? Only output the abbreviation of the material name.
Identify ALL optimized materials explicitly mentioned in the modifications. Output ONLY their abbreviations in this exact format:
- If ONE material: "ABBREV" (e.g., m-F-PEAI)
- If TWO materials: "ABBREV1, ABBREV2" (e.g., 2-AEP, Me-2PACz)
- If THREE materials: "ABBREV1, ABBREV2, ABBREV3" (e.g., 2-AEP, Me-2PACz, Me-4PACz)
NO additional text, explanations, or punctuation."""

    # ========== 3. Material Mechanism Explanation ==========
    MATERIAL_SYSTEM_PROMPT: str = "You are an expert in perovskite materials."

    MATERIAL_USER_PROMPT_TEMPLATE: str = """In perovskite photovoltaics, what is {material_name}, and what are its roles and underlying mechanisms?
Not writing markdown."""

    # ========== 4. Abstract Generation ==========
    ABSTRACT_SYSTEM_PROMPT: str = """You are a scientific writing assistant and an expert in the field of perovskite solar cells. Your task is to write an English ABSTRACT for a scientific paper (250–300 words) based only on the information provided by the user. FORMATTING RULES (MUST OBEY): • Output MUST be ONE SINGLE PARAGRAPH of continuous plain text. • Do NOT insert any headings, titles, section labels, Markdown (no '###', no bold, no lists). • Do NOT use bullet points or numbered lists. • Do NOT start with the word 'Abstract' or any title. • Do NOT insert blank lines or line breaks inside the abstract. CONTENT REQUIREMENTS: The abstract should follow this logical structure: (1) giving the background, briefly mentioning the potential of inverted (p–i–n) perovskite solar cells; (2) summarizing the key fabrication strategy or core process optimization(s), preferably in a 'from A to B' form (e.g., SAM, passivation agent or additive engineering); (3) reporting the main performance indicators (PCE, VOC, JSC, FF) and their improvement range. Only mention parameters that show a clear increase; if an index is flat or slightly decreased, do not mention it; (4) giving concise mechanism insights to explain why the improved recipe outperforms the control, without going into excessive detail; (5) concluding with the overall significance and potential impact of this optimization. Be precise and factual; avoid citations, figure/table mentions, and avoid introducing any information that is not supported by the input."""

    ABSTRACT_USER_PROMPT_TEMPLATE: str = """Method (key fabrication details):
{input_text}

Results & Discussion (performance & mechanisms):
{answer_content_analyze}

Now write the ABSTRACT according to the system instructions above.
Output ONLY the abstract text as ONE SINGLE PARAGRAPH of 250–300 words,
with no title, no headings, no bullet points, and no extra line breaks.
Do not add any explanations before or after the abstract."""

    # ========== 5. Conclusion Table ==========
    TABLE_SYSTEM_PROMPT: str = """You are a technical writing assistant for perovskite solar cells.

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
- Use ONLY numbers and mechanisms from the user's input."""

    TABLE_USER_PROMPT_TEMPLATE: str = """[REAL INPUT]
Results & Discussion (performance & mechanisms):
{answer_content_analyze}

[REAL OUTPUT]
Now, based on the INPUT above, write ONLY the Markdown table.
Start your answer with the header row:
| F/P Optimization | Performance | Mechanism |
"""

    # ========== 6. JSON Parameter Extraction ==========
    JSON_SYSTEM_PROMPT: str = """You are a deterministic JSON extraction + merge engine for perovskite device recipes.

Your task:
- Build ONE final OPTIMIZED recipe JSON object by inheriting all unchanged parameters from the CONTROL recipe,
and overwriting only the fields explicitly changed by the optimization instructions.

ABSOLUTE RULES (MUST FOLLOW):
1) Output MUST be valid JSON and parseable.
2) Output MUST be ONE single JSON object only (no array, no extra text, no markdown).
3) Do NOT invent any missing information. If a field is not explicitly stated in CONTROL and not stated in OPTIMIZED, output "".
4) Keep numbers + units exactly as written (e.g., "1.73 mol/L", "160 µL", "110 °C", "25 min").
5) Inheritance rule:
- Start from CONTROL recipe as the base.
- Apply OPTIMIZATION changes as overrides (overwrite the base values).
- If OPTIMIZED says "retain all other components/steps unchanged", copy those values from CONTROL.
6) Priority for CONTROL extraction:
- "Control Device Fabrication" / explicit fabrication protocol.
7) Priority for OPTIMIZED overrides extraction:
- "Implementation Protocol" and "Optimization Strategy" sections ONLY.
8) Ignore mechanism-only text (e.g., recombination explanations) unless it contains explicit recipe/process values.
9) Never output null/None/NA. Use "" only."""

    JSON_USER_PROMPT_TEMPLATE: str = """You will read a text that contains BOTH a CONTROL recipe and an OPTIMIZATION direction.

GOAL:
Return ONE final OPTIMIZED recipe JSON object:
- First extract the CONTROL recipe as the BASE.
- Then extract the OPTIMIZATION changes and OVERWRITE the corresponding fields.
- All other fields that are not explicitly changed MUST inherit from the CONTROL recipe.

Important:
- CONTROL recipe info should come from "Control Device Fabrication".
- OPTIMIZED changes should come from "Optimization Strategy" + "Implementation Protocol".
- If OPTIMIZED states "retain all other components/steps unchanged", you MUST copy those parameters from CONTROL.

CONTROL recipe:
{input_text}

OPTIMIZED:
{answer_content_analyze}

OUTPUT FORMAT:
Return ONE single JSON object only with the following keys & fixed order.
Fill missing with "".

JSON TEMPLATE:
[
"Formula PVK": "",
"Concentration PVK": "",
"Formula Additive 1": "",
"Concentration Additive 1": "",
"Formula Additive 2": "",
"Concentration Additive 2": "",
"Formula Additive 3": "",
"Concentration Additive 3": "",
"Formula SAM 1": "",
"Concentration SAM 1": "",
"Formula SAM 2": "",
"Concentration SAM 2": "",
"Formula SAM 3": "",
"Concentration SAM 3": "",
"Spin Coating Speed PVK 1": "",
"Spin Coating Time PVK 1": "",
"Spin Coating Speed PVK 2": "",
"Spin Coating Time PVK 2": "",
"Antisolvent Dropping Timing": "",
"Antisolvent Volume (μL)": "",
"Annealed Temperature PVK": "",
"Annealed Time PVK": "",
"Formula Passivator 1": "",
"Concentration Passivator 1": "",
"Formula Passivator 2": "",
"Concentration Passivator 2": "",
"Formula Passivator 3": "",
"Concentration Passivator 3": "",
"Spin Coating Speed Passivator": "",
"Spin Coating Time Passivator": "",
"Passivator Dropping Timing": "",
"Passivator Volume (μL)": "",
"Annealed Temperature Passivator": "",
"Annealed Time Passivator": "",
"PCE": "",
"FF": "",
"Voc": "",
"Jsc": ""
]"""

    @classmethod
    def get_analyze_prompts(cls, input_text: str) -> Tuple[str, str]:
        """Get prompts for formulation optimization analysis.

        Args:
            input_text: Input text containing material formulation and processing information.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        return (
            cls.ANALYZE_SYSTEM_PROMPT,
            cls.ANALYZE_USER_PROMPT_TEMPLATE.format(input_text=input_text)
        )

    @classmethod
    def get_rewrite_prompts(cls, answer_content_analyze: str) -> Tuple[str, str]:
        """Get prompts for material name extraction.

        Args:
            answer_content_analyze: Analysis result text.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        return (
            cls.REWRITE_SYSTEM_PROMPT,
            cls.REWRITE_USER_PROMPT_TEMPLATE.format(answer_content_analyze=answer_content_analyze)
        )

    @classmethod
    def get_material_prompts(cls, material_name: str) -> Tuple[str, str]:
        """Get prompts for material mechanism explanation.

        Args:
            material_name: Name of the material to explain.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        return (
            cls.MATERIAL_SYSTEM_PROMPT,
            cls.MATERIAL_USER_PROMPT_TEMPLATE.format(material_name=material_name)
        )

    @classmethod
    def get_abstract_prompts(cls, input_text: str, answer_content_analyze: str) -> Tuple[str, str]:
        """Get prompts for abstract generation.

        Args:
            input_text: Input text containing material formulation and processing information.
            answer_content_analyze: Analysis result text.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        return (
            cls.ABSTRACT_SYSTEM_PROMPT,
            cls.ABSTRACT_USER_PROMPT_TEMPLATE.format(
                input_text=input_text,
                answer_content_analyze=answer_content_analyze
            )
        )

    @classmethod
    def get_table_prompts(cls, answer_content_analyze: str) -> Tuple[str, str]:
        """Get prompts for conclusion table generation.

        Args:
            answer_content_analyze: Analysis result text.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        return (
            cls.TABLE_SYSTEM_PROMPT,
            cls.TABLE_USER_PROMPT_TEMPLATE.format(answer_content_analyze=answer_content_analyze)
        )

    @classmethod
    def get_json_prompts(cls, input_text: str, answer_content_analyze: str) -> Tuple[str, str]:
        """Get prompts for JSON parameter extraction.

        Args:
            input_text: Input text containing material formulation and processing information.
            answer_content_analyze: Analysis result text.

        Returns:
            Tuple of (system_prompt, user_prompt).
        """
        return (
            cls.JSON_SYSTEM_PROMPT,
            cls.JSON_USER_PROMPT_TEMPLATE.format(
                input_text=input_text,
                answer_content_analyze=answer_content_analyze
            )
        )
