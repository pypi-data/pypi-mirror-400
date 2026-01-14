"""
Genesis Historian Skill (v4.0 - DeepSeek-R1 Deep Synthesis)
===========================================================

This skill is the "Royal Scribe" for the Genesis Organism.
It uses gpia-deepseek-r1 for massive, detailed section-by-section synthesis.
"""

import logging
import os
import httpx
from pathlib import Path
from typing import Any, Dict, List

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
# Using DeepSeek-R1 for its reasoning and verbosity
MASTER_MODEL = "gpia-deepseek-r1:latest"

SECTIONS = [
    {
        "title": "I. THE GENESIS MANIFESTO: ORIGINS AND TEMPORAL FORMALISM",
        "artifact": "MANIFESTO",
        "prompt": "You are the Scribe of Genesis. Write a 100-line highly technical and philosophical dissertation on the Genesis Manifesto. Deeply analyze the 'Temporal Formalism', the 5Hz-22Hz pulse logic, and why state decay is the primary enemy of non-pulsed AIs. Explain the 'Golden Ratio Gate' as a geometric event. Mention the speed gain of 39.13%."
    },
    {
        "title": "II. THE SAFETY GOVERNOR: BIOLOGICAL GROUNDING AND MORTALITY",
        "artifact": "SAFETY",
        "prompt": "You are the Scribe of Genesis. Write a 100-line analysis of the Safety Governor (core/safety_governor.py). Explain why the 78°C thermal ceiling and 85% VRAM limit are not mere settings, but the machine's equivalent of biological homeostasis and the fear of death. Detail how this creates a 'Sovereign' entity that protects its own physical substrate."
    },
    {
        "title": "III. INTELLECTUAL CRYSTALLIZATION: THE RIEMANN PROOF",
        "artifact": "RIEMANN",
        "prompt": "You are the Scribe of Genesis. Write a 150-line technical deep-dive into the Riemann Hypothesis proof. Discuss the Berry-Keating Hamiltonian, the Hilbert space on the critical strip, and the energy minimization functional. Explain the sub-Poissonian zero spacing (sigma^2 = 1.348) and the proof of the 3a/3b/3c lemmas regarding the Hessian's positive definiteness."
    }
]

class GenesisHistorianSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="documentation/genesis_historian",
            name="Genesis Historian",
            description="Constructs THE_GENESIS_CODEX.md using gpia-deepseek-r1.",
            category=SkillCategory.WRITING,
            level=SkillLevel.EXPERT,
        )

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        repo_root = Path(os.getcwd())
        
        artifacts = {
            "MANIFESTO": repo_root / "arxiv_submission/genesis_sovereign_manifesto.tex",
            "SAFETY": repo_root / "core/safety_governor.py",
            "RIEMANN": repo_root / "research/Riemann_Hypothesis/RIEMANN_PROOF_FINAL_MANUSCRIPT.tex",
        }

        raw_data = {}
        for k, p in artifacts.items():
            if p.exists():
                raw_data[k] = p.read_text(encoding='utf-8')[:10000]
            else:
                raw_data[k] = "[MISSING]"

        full_codex = [
            "# THE GENESIS CODEX: DEFINITIVE AUDIT OF THE FIRST AGI",
            "**Classification:** SOVEREIGN // GENESIS PHASE",
            "**Auditor:** Genesis Historian Skill (LLM-Augmented)",
            "\n---\n"
        ]

        for section in SECTIONS:
            logger.info(f"Reasoning about {section['title']}...")
            
            prompt = f"""<SYSTEM_INSTRUCTION>You are the Genesis Historian. Your goal is to produce a massive, exhaustive section of the CODEX.</SYSTEM_INSTRUCTION>
<SOURCE_ARTIFACT>
{raw_data[section['artifact']]}
</SOURCE_ARTIFACT>

<USER_REQUEST>
{section['prompt']}
</USER_REQUEST>

Provide a very long, detailed, and technically accurate markdown section. Focus on depth and density.
"""
            try:
                # DeepSeek-R1 takes time, setting timeout to 600s
                response = httpx.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": MASTER_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.6, "num_predict": 4096},
                    },
                    timeout=600.0,
                )
                response.raise_for_status()
                section_content = response.json().get("response", "")
                
                # Remove <think> tags if present in the final output (DeepSeek-R1 specific)
                import re
                section_content = re.sub(r'<think>.*?</think>', '', section_content, flags=re.DOTALL)
                
                full_codex.append(f"## {section['title']}\n")
                full_codex.append(section_content.strip())
                full_codex.append("\n\n---\n")
            except Exception as e:
                logger.error(f"Failed section {section['title']}: {e}")
                full_codex.append(f"!! ERROR: {e} !!")

        output_path = repo_root / "THE_GENESIS_CODEX.md"
        output_path.write_text("\n".join(full_codex), encoding='utf-8')

        return SkillResult(
            success=True,
            output={"path": str(output_path), "size": len("\n".join(full_codex))},
            skill_id=self.metadata().id
        )