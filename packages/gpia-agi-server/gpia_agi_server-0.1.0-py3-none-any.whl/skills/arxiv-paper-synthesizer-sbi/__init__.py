"""
ArXiv Paper Synthesizer Skill - SBI Edition

Self-improving skill for autonomous synthesis of academic papers
through iterative cognitive ecosystem cycles.

Usage from GPIA:
    from skills.registry import get_registry
    result = get_registry().execute_skill(
        "arxiv-paper-synthesizer-sbi",
        {
            "capability": "iterate_n_passes",
            "papers": [...],
            "n_passes": 3,
            "rigor_target": 0.85
        },
        SkillContext()
    )
"""

from skills.arxiv_paper_synthesizer_sbi.skill import ArxivPaperSynthesizer

__all__ = ["ArxivPaperSynthesizer"]
