#!/usr/bin/env python3
"""
Example: GPIA Synthesizing Her Own ArXiv Papers

This demonstrates how GPIA invokes the arxiv-paper-synthesizer-sbi
skill to autonomously validate and improve her own academic papers.

Run from CLI:
    python skills/arxiv-paper-synthesizer-sbi/example_invoke.py
"""

from pathlib import Path
from skills.registry import get_registry
from skills.base import SkillContext

def load_papers_from_arxiv_submission():
    """Load all .tex papers from arxiv_submission directory."""
    arxiv_dir = Path("arxiv_submission")
    papers = []

    for tex_file in arxiv_dir.glob("*.tex"):
        try:
            content = tex_file.read_text(encoding='utf-8')
            paper_id = tex_file.stem

            papers.append({
                "id": paper_id,
                "title": paper_id.replace("_", " ").title(),
                "content": content,
                "claims": [
                    {"claim": "39.13% inference latency improvement", "evidence_level": "preliminary"},
                    {"claim": "σ²=1.348 sub-Poissonian distribution", "evidence_level": "unargued"},
                    {"claim": "AGI Score 100 achieved", "evidence_level": "unargued"},
                ]
            })
            print(f"✓ Loaded: {paper_id}")
        except Exception as e:
            print(f"✗ Failed to load {tex_file}: {e}")

    return papers


def main():
    """Main synthesis workflow."""
    print("=" * 70)
    print("GPIA ARXIV PAPER SYNTHESIZER - AUTONOMOUS VALIDATION")
    print("=" * 70)
    print()

    # Load papers
    print("PHASE 0: LOADING PAPERS")
    print("-" * 70)
    papers = load_papers_from_arxiv_submission()
    print(f"✓ Loaded {len(papers)} papers")
    print()

    if not papers:
        print("✗ No papers found in arxiv_submission/")
        return

    # Get skill registry
    print("PHASE 1: INITIALIZING SKILL")
    print("-" * 70)
    registry = get_registry()
    context = SkillContext()

    try:
        init_result = registry.execute_skill(
            "arxiv-paper-synthesizer-sbi",
            {
                "capability": "initialize_synthesis",
                "papers": papers
            },
            context
        )
        print("✓ Synthesis skill initialized")
        print()
    except Exception as e:
        print(f"✗ Failed to initialize skill: {e}")
        return

    # Run full N-pass synthesis
    print("PHASE 2: RUNNING SYNTHESIS (3 PASSES)")
    print("-" * 70)
    print("  Pass 1: Hunter identifies unargued claims")
    print("  Pass 2: Dissector extracts evidence chains")
    print("  Pass 3: Synthesizer generates improved LaTeX")
    print()

    try:
        synthesis_result = registry.execute_skill(
            "arxiv-paper-synthesizer-sbi",
            {
                "capability": "iterate_n_passes",
                "papers": papers,
                "n_passes": 3,
                "rigor_target": 0.85,
                "convergence_threshold": 0.02,
                "arxiv_field": "cs.AI",
                "focus_areas": ["mathematical_rigor", "empirical_validation", "citations"]
            },
            context
        )

        if synthesis_result.success:
            print("✓ Synthesis complete!")
            print()

            # Report results
            print("SYNTHESIS RESULTS")
            print("-" * 70)
            output = synthesis_result.output

            print(f"Total passes: {output['total_passes']}")
            print(f"Final rigor score: {output['final_rigor_score']:.4f}")
            print(f"ArXiv ready: {'YES' if output['arxiv_ready'] else 'NO'}")
            print()

            print("ITERATION HISTORY:")
            for history in output["iteration_history"]:
                if "pass_number" in history:
                    pass_num = history["pass_number"]
                    rigor = history.get("rigor_score", 0)
                    improvement = history.get("improvement", 0)
                    unargued = history.get("hunter_findings", 0)

                    print(f"  Pass {pass_num}:")
                    print(f"    Rigor score: {rigor:.4f} (Δ {improvement:+.4f})")
                    print(f"    Unargued claims found: {unargued}")
                elif "status" in history:
                    print(f"  Status: {history['status']} ({history['reason']})")

            print()

            # Learning report
            print("WHAT GPIA LEARNED")
            print("-" * 70)
            learning = output.get("learning_summary", {})
            if learning:
                print(f"Passes to convergence: {learning.get('passes_to_convergence', 'N/A')}")
                print(f"Total rigor improvement: {learning.get('total_rigor_improvement', 0):.4f}")
                if learning.get('best_improvement_pass'):
                    print(f"Best improvement pass: {learning['best_improvement_pass']}")

            print()

            # Final recommendation
            print("RECOMMENDATION")
            print("-" * 70)
            if output['arxiv_ready']:
                print("✓ Papers are ready for ArXiv submission")
                print("  Next step: Create ArXiv submission and upload")
            else:
                print("⚠ Papers need additional work before ArXiv submission")
                print(f"  Target rigor: 0.85, Current: {output['final_rigor_score']:.4f}")
                print("  Recommendation: Run more passes or focus on:")
                print("    - Adding formal definitions for all metrics")
                print("    - Expanding citations (15+ minimum)")
                print("    - Including empirical methodology section")

        else:
            print(f"✗ Synthesis failed: {synthesis_result.error}")

    except Exception as e:
        print(f"✗ Error during synthesis: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
