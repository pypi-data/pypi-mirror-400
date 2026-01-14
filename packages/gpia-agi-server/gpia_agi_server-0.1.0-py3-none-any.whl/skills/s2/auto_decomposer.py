"""
S2 Auto-Decomposer
==================

Automated skill decomposition engine for GPIA.

Uses LLMs (DeepSeek-R1 for analysis, Qwen3 for generation) to:
1. Analyze monolithic skills
2. Identify atomic operations (L0 micros)
3. Compose into meso/macro/meta layers
4. Generate S2 decomposed skill code
5. Create routing configurations

This enables GPIA to systematically decompose all 76+ skills
into the S2 multi-scale architecture.
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

import requests

from .context_stack import ScaleLevel

logger = logging.getLogger(__name__)

# Paths
SKILLS_DIR = Path(__file__).parent.parent
INDEX_PATH = SKILLS_DIR / "INDEX.json"
DECOMPOSED_DIR = SKILLS_DIR / "s2" / "decomposed"
DECOMPOSED_DIR.mkdir(exist_ok=True)

# Ollama endpoint
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


class DecompositionStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETE = "complete"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SkillAnalysis:
    """Analysis result for a skill."""
    skill_id: str
    name: str
    description: str
    capabilities: List[str] = field(default_factory=list)
    atomic_operations: List[Dict[str, str]] = field(default_factory=list)
    suggested_micros: List[str] = field(default_factory=list)
    suggested_mesos: List[str] = field(default_factory=list)
    suggested_macros: List[str] = field(default_factory=list)
    complexity: str = "medium"  # low, medium, high
    visual_potential: bool = False
    raw_analysis: str = ""


@dataclass
class DecomposedSkill:
    """Generated S2 decomposed skill."""
    skill_id: str
    original_name: str
    scale_structure: Dict[str, List[str]]
    generated_code: str
    skill_tree: Dict[str, List[str]]
    model_routing: Dict[str, str]
    status: DecompositionStatus = DecompositionStatus.PENDING


class LLMClient:
    """Simple LLM client for decomposition tasks."""

    def __init__(self, ollama_url: str = OLLAMA_URL):
        self.ollama_url = ollama_url

    def query(
        self,
        prompt: str,
        model: str = "deepseek-r1:latest",
        max_tokens: int = 1500,
        temperature: float = 0.7
    ) -> str:
        """Query an LLM via Ollama."""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                },
                timeout=180
            )

            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"LLM query failed: {response.status_code}")
                return ""

        except Exception as e:
            logger.error(f"LLM query error: {e}")
            return ""


class S2AutoDecomposer:
    """
    Automated S2 skill decomposition engine.

    GPIA uses this to systematically decompose monolithic skills
    into multi-scale S2 architecture.
    """

    # Skills already decomposed (prototypes)
    ALREADY_DECOMPOSED = {
        "reasoning/explainable-reasoning",
        "conscience/memory",
        "automation/hybrid-orchestrator",
    }

    # Skills to skip (system skills, duplicates)
    SKIP_PATTERNS = [
        ".system/",
        "codex",  # External codex skills
    ]

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        self.skills_index: List[Dict[str, Any]] = []
        self.analyses: Dict[str, SkillAnalysis] = {}
        self.decomposed: Dict[str, DecomposedSkill] = {}
        self._load_index()

    def _load_index(self):
        """Load skills index."""
        if INDEX_PATH.exists():
            with open(INDEX_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.skills_index = data.get("skills", [])
            logger.info(f"Loaded {len(self.skills_index)} skills from index")

    def get_decomposable_skills(self) -> List[Dict[str, Any]]:
        """Get list of skills that can be decomposed."""
        decomposable = []

        for skill in self.skills_index:
            skill_id = skill.get("id", "")

            # Skip already decomposed
            if skill_id in self.ALREADY_DECOMPOSED:
                continue

            # Skip patterns
            if any(pattern in skill_id for pattern in self.SKIP_PATTERNS):
                continue

            # Skip if source is not repo (external skills)
            if skill.get("source") != "repo":
                continue

            decomposable.append(skill)

        return decomposable

    def analyze_skill(self, skill: Dict[str, Any]) -> SkillAnalysis:
        """
        Analyze a skill to identify decomposition structure.

        Uses DeepSeek-R1 for deep reasoning about skill structure.
        """
        skill_id = skill.get("id", "")
        name = skill.get("name", "")
        description = skill.get("description", "")
        path = skill.get("path", "")

        # Try to read skill manifest for more context
        manifest_content = ""
        skill_path = Path(path)
        if skill_path.exists():
            manifest_file = skill_path / "SKILL.md"
            if manifest_file.exists():
                try:
                    manifest_content = manifest_file.read_text(encoding='utf-8')[:2000]
                except:
                    pass

        # Build analysis prompt
        prompt = f"""Analyze this skill for S2 multi-scale decomposition.

SKILL: {name}
ID: {skill_id}
DESCRIPTION: {description}

MANIFEST:
{manifest_content if manifest_content else "(No manifest available)"}

S2 SCALE LEVELS:
- L0 (Micro): Atomic operations, single action, <=10 tokens (e.g., parse_json, fetch_url)
- L1 (Meso): Composed operations, 2-3 micros combined, 30-50 tokens
- L2 (Macro): Bundled workflows, full capability, 80-120 tokens
- L3 (Meta): Orchestrator that coordinates macros

TASK: Identify how to decompose this skill into S2 scales.

Respond in this EXACT format:

COMPLEXITY: [low/medium/high]
VISUAL_POTENTIAL: [yes/no] (does this skill benefit from image/visual processing?)

ATOMIC_OPERATIONS (L0 micros - list 3-5):
1. [operation_name]: [brief description]
2. [operation_name]: [brief description]
3. [operation_name]: [brief description]

COMPOSED_OPERATIONS (L1 mesos - list 2-3):
1. [operation_name]: [which micros it composes]
2. [operation_name]: [which micros it composes]

BUNDLED_WORKFLOWS (L2 macros - list 1-2):
1. [operation_name]: [which mesos it bundles]

ORCHESTRATOR (L3 meta):
1. [orchestrator_name]: [how it coordinates the workflow]

Keep names in snake_case format."""

        # Query DeepSeek-R1 for analysis
        logger.info(f"Analyzing skill: {skill_id}")
        raw_response = self.llm.query(prompt, model="deepseek-r1:latest", max_tokens=1000)

        # Parse response
        analysis = SkillAnalysis(
            skill_id=skill_id,
            name=name,
            description=description,
            raw_analysis=raw_response
        )

        # Extract structured data from response
        analysis.complexity = self._extract_field(raw_response, "COMPLEXITY", "medium").lower()
        analysis.visual_potential = "yes" in self._extract_field(raw_response, "VISUAL_POTENTIAL", "no").lower()

        # Extract operations
        analysis.suggested_micros = self._extract_list(raw_response, "ATOMIC_OPERATIONS")
        analysis.suggested_mesos = self._extract_list(raw_response, "COMPOSED_OPERATIONS")
        analysis.suggested_macros = self._extract_list(raw_response, "BUNDLED_WORKFLOWS")

        self.analyses[skill_id] = analysis
        return analysis

    def _extract_field(self, text: str, field: str, default: str = "") -> str:
        """Extract a field value from response."""
        # Try multiple patterns
        patterns = [
            rf"{field}:\s*\[?([^\]\n]+)",
            rf"{field}\s*[:=]\s*([^\n]+)",
            rf"\*\*{field}\*\*:\s*([^\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip().strip("[]").strip("*")
        return default

    def _extract_list(self, text: str, section: str) -> List[str]:
        """Extract list items from a section with improved parsing."""
        items = []

        # Try multiple section header patterns
        section_patterns = [
            rf"{section}[^:]*:?\s*(.*?)(?=\n[A-Z_]{{3,}}[^a-z]|\n\n\n|$)",
            rf"\*\*{section}\*\*[^:]*:?\s*(.*?)(?=\n\*\*|\n\n\n|$)",
            rf"#{1,3}\s*{section}[^:]*:?\s*(.*?)(?=\n#|\n\n\n|$)",
        ]

        section_text = ""
        for pattern in section_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                section_text = match.group(1)
                break

        if not section_text:
            # Try to find any mention of the operations
            if "L0" in section or "micro" in section.lower():
                # Look for micro-like function names anywhere
                micro_pattern = r'(?:micro_|atomic_)?([a-z][a-z_]{2,30})(?:\s*[-:]\s*|\s*\()([^)\n]{10,100})'
                for m in re.finditer(micro_pattern, text, re.IGNORECASE):
                    name = m.group(1).strip().lower()
                    if name not in ['the', 'and', 'for', 'this', 'that', 'with']:
                        items.append(f"{name}: {m.group(2).strip()[:50]}")
                        if len(items) >= 5:
                            break
            return items[:5]

        # Try multiple item patterns
        item_patterns = [
            # Standard numbered: 1. name: description
            r"(\d+)[.)]\s*\[?([a-z][a-z_0-9]*)\]?\s*[-:]\s*(.+?)(?=\n\d+[.)]|\n\n|$)",
            # Bullet with name: - name: description
            r"[-*]\s*\[?([a-z][a-z_0-9]*)\]?\s*[-:]\s*(.+?)(?=\n[-*]|\n\n|$)",
            # Bold name: **name**: description
            r"\*\*([a-z][a-z_0-9]*)\*\*\s*[-:]\s*(.+?)(?=\n\*\*|\n\n|$)",
            # Backtick name: `name`: description
            r"`([a-z][a-z_0-9]*)`\s*[-:]\s*(.+?)(?=\n`|\n\n|$)",
            # Simple: name - description or name: description
            r"^\s*([a-z][a-z_0-9]{2,25})\s*[-:]\s*(.{10,80})$",
        ]

        for pattern in item_patterns:
            matches = list(re.finditer(pattern, section_text, re.IGNORECASE | re.MULTILINE))
            if matches:
                for m in matches:
                    groups = m.groups()
                    if len(groups) >= 2:
                        # Handle numbered vs non-numbered
                        if groups[0].isdigit():
                            name = groups[1].strip().lower()
                            desc = groups[2].strip() if len(groups) > 2 else ""
                        else:
                            name = groups[0].strip().lower()
                            desc = groups[1].strip()

                        # Clean up name
                        name = re.sub(r'[^a-z_0-9]', '_', name)
                        if len(name) >= 3 and name not in ['the', 'and', 'for']:
                            items.append(f"{name}: {desc[:60]}")

                if items:
                    break

        # Deduplicate while preserving order
        seen = set()
        unique_items = []
        for item in items:
            name = item.split(':')[0]
            if name not in seen:
                seen.add(name)
                unique_items.append(item)

        return unique_items[:8]  # Limit to 8 items

    def generate_decomposition(self, analysis: SkillAnalysis) -> DecomposedSkill:
        """
        Generate S2 decomposed skill code from analysis.

        Uses Qwen3 for code generation.
        """
        skill_id = analysis.skill_id
        safe_name = skill_id.replace("/", "_").replace("-", "_")

        # Build code generation prompt
        prompt = f"""Generate Python code for S2 decomposed skill.

SKILL: {analysis.name}
ID: {analysis.skill_id}
DESCRIPTION: {analysis.description}

STRUCTURE FROM ANALYSIS:
- Micros (L0): {', '.join(analysis.suggested_micros[:5])}
- Mesos (L1): {', '.join(analysis.suggested_mesos[:3])}
- Macros (L2): {', '.join(analysis.suggested_macros[:2])}
- Visual: {'Yes' if analysis.visual_potential else 'No'}

Generate a Python module with:
1. L0 micro functions (def micro_xxx)
2. L1 meso functions (def meso_xxx) that call micros
3. L2 macro functions (def macro_xxx) that call mesos
4. L3 meta orchestrator (def meta_xxx_orchestrator)
5. create_composer() function
6. get_skill_tree() function

Use this template structure:

```python
from typing import Any, Dict, List, Optional
from skills.s2.context_stack import ScaleLevel
from skills.s2.composer import S2Composer

# L0 MICRO SKILLS
def micro_example(input: str, **kwargs) -> Dict[str, Any]:
    return {{"result": "..."}}

# L1 MESO SKILLS
def meso_example(data: Any, **kwargs) -> Dict[str, Any]:
    micro_result = micro_example(str(data))
    return {{"composed": micro_result}}

# L2 MACRO SKILLS
def macro_example(task: str, **kwargs) -> Dict[str, Any]:
    meso_result = meso_example(task)
    return {{"workflow_result": meso_result}}

# L3 META ORCHESTRATOR
def meta_orchestrator(capability: str, params: dict = None, **kwargs) -> Dict[str, Any]:
    result = macro_example(params.get("task", ""))
    result["orchestrated"] = True
    return result

def create_composer() -> S2Composer:
    composer = S2Composer()
    composer.register_skill("skill/micro", micro_example, ScaleLevel.L0)
    # ... register all skills
    return composer

def get_skill_tree() -> Dict[str, List[str]]:
    return {{
        "skill/orchestrator": ["skill/macro"],
        "skill/macro": ["skill/meso"],
        "skill/meso": ["skill/micro"],
    }}
```

Generate complete working code for {analysis.name}. Use realistic implementations."""

        logger.info(f"Generating code for: {skill_id}")
        generated_code = self.llm.query(prompt, model="qwen3:latest", max_tokens=2000)

        # Clean up code (extract from markdown if needed)
        if "```python" in generated_code:
            match = re.search(r"```python\s*(.*?)```", generated_code, re.DOTALL)
            if match:
                generated_code = match.group(1).strip()
        elif "```" in generated_code:
            # Remove any remaining markdown code blocks
            generated_code = re.sub(r"```\w*\n?", "", generated_code)
            generated_code = generated_code.strip()

        # Build skill tree from analysis
        skill_tree = self._build_skill_tree(analysis)

        # Determine model routing - All 5 LLM Partners
        # - codegemma: Fast atomic operations, intent parsing
        # - qwen3: Creative synthesis, code generation
        # - deepseek_r1: Deep reasoning, analysis, debugging
        # - llava: Visual tasks, image analysis, screenshots
        # - gpt_oss_20b: Complex synthesis, dispute resolution, arbiter
        has_visual = analysis.visual_potential
        model_routing = {
            "L0": {
                "text": "codegemma",
                "visual": "llava" if has_visual else "codegemma",
                "reasoning": "codegemma",
                "synthesis": "qwen3"
            },
            "L1": {
                "text": "qwen3",
                "visual": "llava" if has_visual else "qwen3",
                "reasoning": "deepseek_r1",
                "synthesis": "qwen3"
            },
            "L2": {
                "text": "qwen3",
                "visual": "llava" if has_visual else "qwen3",
                "reasoning": "deepseek_r1",
                "synthesis": "gpt_oss_20b"
            },
            "L3": {
                "text": "deepseek_r1",
                "visual": "llava" if has_visual else "deepseek_r1",
                "reasoning": "deepseek_r1",
                "synthesis": "gpt_oss_20b"
            },
        }

        decomposed = DecomposedSkill(
            skill_id=skill_id,
            original_name=analysis.name,
            scale_structure={
                "L0": analysis.suggested_micros,
                "L1": analysis.suggested_mesos,
                "L2": analysis.suggested_macros,
                "L3": [f"{safe_name}_orchestrator"],
            },
            generated_code=generated_code,
            skill_tree=skill_tree,
            model_routing=model_routing,
            status=DecompositionStatus.COMPLETE
        )

        self.decomposed[skill_id] = decomposed
        return decomposed

    def _build_skill_tree(self, analysis: SkillAnalysis) -> Dict[str, List[str]]:
        """Build skill tree from analysis."""
        prefix = analysis.skill_id.replace("-", "_")
        tree = {}

        # Meta -> Macros
        if analysis.suggested_macros:
            macro_names = [f"{prefix}/{m.split(':')[0]}" for m in analysis.suggested_macros]
            tree[f"{prefix}/orchestrator"] = macro_names

        # Macros -> Mesos
        if analysis.suggested_mesos:
            meso_names = [f"{prefix}/{m.split(':')[0]}" for m in analysis.suggested_mesos]
            for macro in analysis.suggested_macros:
                macro_name = f"{prefix}/{macro.split(':')[0]}"
                tree[macro_name] = meso_names

        # Mesos -> Micros
        if analysis.suggested_micros:
            micro_names = [f"{prefix}/{m.split(':')[0]}" for m in analysis.suggested_micros]
            for meso in analysis.suggested_mesos:
                meso_name = f"{prefix}/{meso.split(':')[0]}"
                tree[meso_name] = micro_names[:3]  # Limit micros per meso

        return tree

    def save_decomposition(self, decomposed: DecomposedSkill) -> Path:
        """Save decomposed skill to file."""
        safe_name = decomposed.skill_id.replace("/", "_").replace("-", "_")
        output_file = DECOMPOSED_DIR / f"{safe_name}_s2.py"

        # Build full file content
        content = f'''"""
S2 Decomposed: {decomposed.original_name}
==========================================

Auto-generated by S2 Auto-Decomposer.

Original skill: {decomposed.skill_id}
Scale structure:
  L0 (Micro): {len(decomposed.scale_structure.get("L0", []))} operations
  L1 (Meso): {len(decomposed.scale_structure.get("L1", []))} operations
  L2 (Macro): {len(decomposed.scale_structure.get("L2", []))} operations
  L3 (Meta): 1 orchestrator

Model routing (5 LLM Partners: codegemma, qwen3, deepseek_r1, llava, gpt_oss_20b):
  L0 -> text:{decomposed.model_routing.get("L0", {}).get("text", "codegemma")} | reasoning:{decomposed.model_routing.get("L0", {}).get("reasoning", "codegemma")}
  L1 -> text:{decomposed.model_routing.get("L1", {}).get("text", "qwen3")} | reasoning:{decomposed.model_routing.get("L1", {}).get("reasoning", "deepseek_r1")}
  L2 -> text:{decomposed.model_routing.get("L2", {}).get("text", "qwen3")} | synthesis:{decomposed.model_routing.get("L2", {}).get("synthesis", "gpt_oss_20b")}
  L3 -> text:{decomposed.model_routing.get("L3", {}).get("text", "deepseek_r1")} | synthesis:{decomposed.model_routing.get("L3", {}).get("synthesis", "gpt_oss_20b")}
"""

{decomposed.generated_code}


# Skill metadata
SKILL_METADATA = {{
    "original_id": "{decomposed.skill_id}",
    "original_name": "{decomposed.original_name}",
    "scale_structure": {json.dumps(decomposed.scale_structure, indent=4)},
    "skill_tree": {json.dumps(decomposed.skill_tree, indent=4)},
    "model_routing": {json.dumps(decomposed.model_routing, indent=4)},
}}
'''

        output_file.write_text(content, encoding='utf-8')
        logger.info(f"Saved decomposition: {output_file}")
        return output_file

    def decompose_skill(self, skill: Dict[str, Any]) -> Optional[DecomposedSkill]:
        """Full decomposition pipeline for a single skill."""
        skill_id = skill.get("id", "")

        try:
            # Analyze
            analysis = self.analyze_skill(skill)

            # Check if analysis produced useful results
            if not analysis.suggested_micros:
                logger.warning(f"No micros identified for {skill_id}, skipping")
                return None

            # Generate code
            decomposed = self.generate_decomposition(analysis)

            # Save
            self.save_decomposition(decomposed)

            return decomposed

        except Exception as e:
            logger.error(f"Decomposition failed for {skill_id}: {e}")
            return None

    def decompose_batch(
        self,
        skills: Optional[List[Dict[str, Any]]] = None,
        limit: int = 10,
        delay_seconds: float = 2.0
    ) -> Dict[str, Any]:
        """
        Batch decompose multiple skills.

        Args:
            skills: Skills to decompose (or None for all decomposable)
            limit: Maximum number to process
            delay_seconds: Delay between skills (rate limiting)

        Returns:
            Summary of decomposition results
        """
        if skills is None:
            skills = self.get_decomposable_skills()

        skills_to_process = skills[:limit]

        results = {
            "total": len(skills_to_process),
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "decomposed": [],
            "errors": [],
        }

        print(f"\nS2 Auto-Decomposer: Processing {len(skills_to_process)} skills...")
        print("=" * 60)

        for i, skill in enumerate(skills_to_process):
            skill_id = skill.get("id", "")
            print(f"\n[{i+1}/{len(skills_to_process)}] {skill_id}")

            try:
                decomposed = self.decompose_skill(skill)

                if decomposed:
                    results["successful"] += 1
                    results["decomposed"].append(skill_id)
                    print(f"  -> SUCCESS: {len(decomposed.scale_structure.get('L0', []))} micros")
                else:
                    results["skipped"] += 1
                    print(f"  -> SKIPPED")

            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"skill_id": skill_id, "error": str(e)})
                print(f"  -> FAILED: {e}")

            # Rate limiting
            if i < len(skills_to_process) - 1:
                time.sleep(delay_seconds)

        print("\n" + "=" * 60)
        print(f"Complete: {results['successful']} successful, {results['failed']} failed, {results['skipped']} skipped")

        return results

    def get_decomposition_status(self) -> Dict[str, Any]:
        """Get status of decomposition progress."""
        decomposable = self.get_decomposable_skills()
        already_done = len(self.ALREADY_DECOMPOSED)
        auto_decomposed = len(list(DECOMPOSED_DIR.glob("*_s2.py")))

        return {
            "total_skills": len(self.skills_index),
            "decomposable": len(decomposable),
            "prototype_decomposed": already_done,
            "auto_decomposed": auto_decomposed,
            "remaining": len(decomposable) - auto_decomposed,
            "decomposed_dir": str(DECOMPOSED_DIR),
        }


# ==============================================================================
# CLI INTERFACE
# ==============================================================================

def run_decomposer(limit: int = 5):
    """Run the auto-decomposer on available skills."""
    print("=" * 60)
    print("GPIA S2 AUTO-DECOMPOSER")
    print("=" * 60)

    decomposer = S2AutoDecomposer()

    # Show status
    status = decomposer.get_decomposition_status()
    print(f"\nStatus:")
    print(f"  Total skills: {status['total_skills']}")
    print(f"  Decomposable: {status['decomposable']}")
    print(f"  Already decomposed (prototypes): {status['prototype_decomposed']}")
    print(f"  Auto-decomposed: {status['auto_decomposed']}")
    print(f"  Remaining: {status['remaining']}")

    # Get decomposable skills
    skills = decomposer.get_decomposable_skills()
    print(f"\nDecomposable skills ({len(skills)}):")
    for skill in skills[:10]:
        print(f"  - {skill.get('id')}: {skill.get('description', '')[:50]}...")

    if len(skills) > 10:
        print(f"  ... and {len(skills) - 10} more")

    # Run batch decomposition
    print(f"\nRunning decomposition (limit={limit})...")
    results = decomposer.decompose_batch(limit=limit)

    print(f"\nResults saved to: {DECOMPOSED_DIR}")

    return results


if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_decomposer(limit=limit)
