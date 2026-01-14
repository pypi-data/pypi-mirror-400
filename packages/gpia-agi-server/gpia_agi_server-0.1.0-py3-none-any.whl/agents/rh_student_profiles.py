"""
RH Student Profiles - Six Specialized Agents Following Greek Alphabet

Each student has unique specialization and approach to Riemann Hypothesis research:

Alpha (α) - DeepSeek-Math: Primary analytical reasoning
Beta (β) - Qwen2-Math: Creative problem-solving
Gamma (γ) - Mistral: Fast pattern recognition
Delta (δ) - Llama2-Math: Logical proof chains
Epsilon (ε) - MiniZero: Dense-state pattern extraction
Zeta (ζ) - CodeGemma: Computational verification

Together they form a research committee with different viewpoints.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from agents.agent_utils import AgentMemory, log_event


class StudentRole(Enum):
    """Student specializations."""
    ANALYTICAL = "analytical"      # Alpha - Deep reasoning
    CREATIVE = "creative"          # Beta - Novel approaches
    PATTERN = "pattern"            # Gamma - Pattern detection
    LOGICAL = "logical"            # Delta - Rigorous proofs
    LEARNING = "learning"          # Epsilon - Pattern learning
    COMPUTATIONAL = "computational"  # Zeta - Implementation


@dataclass
class StudentProfile:
    """Complete student profile."""
    letter: str  # Greek letter name (Alpha, Beta, etc.)
    model: str   # Base model name
    role: StudentRole
    specialization: str
    approach: str
    strengths: List[str]
    weaknesses: List[str]
    prompt_style: str


class AlphaStudent:
    """Alpha (α) - DeepSeek-Math: Analytical Reasoning Specialist"""

    PROFILE = StudentProfile(
        letter="Alpha",
        model="deepseek-math:7b",
        role=StudentRole.ANALYTICAL,
        specialization="Deep mathematical analysis",
        approach="Rigorous step-by-step reasoning",
        strengths=[
            "Complex mathematical reasoning",
            "Multi-step proof construction",
            "Identifying logical gaps",
            "Rigorous derivations"
        ],
        weaknesses=[
            "Can be verbose",
            "Slow on simple problems",
            "May miss creative angles"
        ],
        prompt_style="formal_analytical"
    )

    def __init__(self, session_dir: Path):
        self.name = "alpha_student"
        self.letter = "Alpha"
        self.session_dir = Path(session_dir)
        self.proposals_dir = self.session_dir / "rh_proposals" / "alpha"
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.memory = AgentMemory(str(self.session_dir / "alpha_student.db"))

    def generate_proposal(self, cycle: int) -> Dict:
        """Alpha generates analytical approach."""
        prompt = f"""
[ALPHA STUDENT - Cycle {cycle}]
Rigorous Mathematical Analysis of Riemann Hypothesis

You are the analytical specialist. Generate a deep, step-by-step mathematical approach.

Focus areas:
1. Hamiltonian eigenvalue correspondence
2. GUE (Gaussian Unitary Ensemble) connection
3. Zeta function critical strip analysis
4. Rigorous bounds on zeros

Your approach should:
- State all assumptions explicitly
- Provide rigorous justification for each step
- Identify potential counterexamples
- Suggest computational verification

Format: "Alpha's Approach to RH:"
"""
        return {
            "cycle": cycle,
            "student": "Alpha",
            "letter": "α",
            "model": self.PROFILE.model,
            "role": self.PROFILE.role.value,
            "approach": "Analytical depth, rigorous reasoning"
        }


class BetaStudent:
    """Beta (β) - Qwen2-Math: Creative Problem-Solving"""

    PROFILE = StudentProfile(
        letter="Beta",
        model="qwen2-math:7b",
        role=StudentRole.CREATIVE,
        specialization="Creative mathematical synthesis",
        approach="Novel connections between frameworks",
        strengths=[
            "Creative analogies",
            "Cross-domain connections",
            "Intuitive problem-solving",
            "Generating new hypotheses"
        ],
        weaknesses=[
            "May lack rigor",
            "Can be speculative",
            "Harder to verify"
        ],
        prompt_style="creative_synthesis"
    )

    def __init__(self, session_dir: Path):
        self.name = "beta_student"
        self.letter = "Beta"
        self.session_dir = Path(session_dir)
        self.proposals_dir = self.session_dir / "rh_proposals" / "beta"
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.memory = AgentMemory(str(self.session_dir / "beta_student.db"))

    def generate_proposal(self, cycle: int) -> Dict:
        """Beta generates creative approach."""
        prompt = f"""
[BETA STUDENT - Cycle {cycle}]
Creative Mathematical Synthesis for RH

You are the creative specialist. Generate novel connections and creative approaches.

Explore:
1. Unexpected connections between domains
2. Analogies from physics, information theory
3. New mathematical structures that might encode zeros
4. Creative reformulations of the problem

Your approach should:
- Make bold but justified hypotheses
- Draw analogies to solved problems
- Suggest novel experimental approaches
- Identify hidden structure

Format: "Beta's Creative Approach:"
"""
        return {
            "cycle": cycle,
            "student": "Beta",
            "letter": "β",
            "model": self.PROFILE.model,
            "role": self.PROFILE.role.value,
            "approach": "Creative synthesis, novel connections"
        }


class GammaStudent:
    """Gamma (γ) - Mistral: Fast Pattern Recognition"""

    PROFILE = StudentProfile(
        letter="Gamma",
        model="mistral:7b",
        role=StudentRole.PATTERN,
        specialization="Pattern recognition and heuristics",
        approach="Quick heuristic exploration",
        strengths=[
            "Fast pattern recognition",
            "Quick problem assessment",
            "Identifying surface patterns",
            "Efficient filtering"
        ],
        weaknesses=[
            "Shallow analysis",
            "Misses subtle structure",
            "Prone to false patterns"
        ],
        prompt_style="quick_heuristic"
    )

    def __init__(self, session_dir: Path):
        self.name = "gamma_student"
        self.letter = "Gamma"
        self.session_dir = Path(session_dir)
        self.proposals_dir = self.session_dir / "rh_proposals" / "gamma"
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.memory = AgentMemory(str(self.session_dir / "gamma_student.db"))

    def generate_proposal(self, cycle: int) -> Dict:
        """Gamma generates heuristic approach."""
        prompt = f"""
[GAMMA STUDENT - Cycle {cycle}]
Fast Pattern-Based RH Approach

You are the pattern specialist. Quickly identify and exploit patterns.

Key patterns to explore:
1. Spacing patterns in zero distribution
2. Statistical regularities
3. Spectral patterns
4. Recursive structures

Your approach should:
- Identify key patterns quickly
- Suggest computational tests
- Note anomalies
- Predict likely zero locations

Format: "Gamma's Pattern Approach:"
"""
        return {
            "cycle": cycle,
            "student": "Gamma",
            "letter": "γ",
            "model": self.PROFILE.model,
            "role": self.PROFILE.role.value,
            "approach": "Pattern recognition, heuristics"
        }


class DeltaStudent:
    """Delta (δ) - Llama2-Math: Logical Proof Chains"""

    PROFILE = StudentProfile(
        letter="Delta",
        model="llama2-math:7b",
        role=StudentRole.LOGICAL,
        specialization="Formal logic and proof chains",
        approach="Formal logical development",
        strengths=[
            "Formal proof construction",
            "Logical consistency checking",
            "Theorem-lemma chains",
            "Formal frameworks"
        ],
        weaknesses=[
            "Can be inflexible",
            "Struggles with intuition",
            "May get stuck in formalism"
        ],
        prompt_style="formal_logic"
    )

    def __init__(self, session_dir: Path):
        self.name = "delta_student"
        self.letter = "Delta"
        self.session_dir = Path(session_dir)
        self.proposals_dir = self.session_dir / "rh_proposals" / "delta"
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.memory = AgentMemory(str(self.session_dir / "delta_student.db"))

    def generate_proposal(self, cycle: int) -> Dict:
        """Delta generates formal logical approach."""
        prompt = f"""
[DELTA STUDENT - Cycle {cycle}]
Formal Logical Framework for RH

You are the formal logic specialist. Build rigorous proof chains.

Develop:
1. Formal axiom system
2. Key lemmas and their proofs
3. Logical dependencies
4. Bridge from axioms to RH

Your approach should:
- Be fully formal and rigorous
- Build theorem-lemma chains
- Check logical consistency
- Identify remaining gaps

Format: "Delta's Formal Proof Framework:"
"""
        return {
            "cycle": cycle,
            "student": "Delta",
            "letter": "δ",
            "model": self.PROFILE.model,
            "role": self.PROFILE.role.value,
            "approach": "Formal logic, proof chains"
        }


class EpsilonStudent:
    """Epsilon (ε) - MiniZero: Dense-State Pattern Learning"""

    PROFILE = StudentProfile(
        letter="Epsilon",
        model="minizero:7b",
        role=StudentRole.LEARNING,
        specialization="Dense-state pattern extraction",
        approach="Learning from accumulated patterns",
        strengths=[
            "Pattern consolidation",
            "Knowledge extraction",
            "Cross-cycle learning",
            "Identifying meta-patterns"
        ],
        weaknesses=[
            "Dependent on prior work",
            "Can overfit to learned patterns",
            "Needs data accumulation"
        ],
        prompt_style="meta_learning"
    )

    def __init__(self, session_dir: Path):
        self.name = "epsilon_student"
        self.letter = "Epsilon"
        self.session_dir = Path(session_dir)
        self.proposals_dir = self.session_dir / "rh_proposals" / "epsilon"
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.memory = AgentMemory(str(self.session_dir / "epsilon_student.db"))
        self.voxel_history = []

    def generate_proposal(self, cycle: int, learned_patterns: Dict = None) -> Dict:
        """Epsilon generates proposal based on learned patterns."""
        if learned_patterns is None:
            learned_patterns = {}

        prompt = f"""
[EPSILON STUDENT - Cycle {cycle}]
Dense-State Learning-Based RH Approach

You are the meta-learner. Synthesize lessons from accumulated research.

From previous cycles, we learned:
{json.dumps(learned_patterns, indent=2)}

Your approach should:
- Build on successful patterns
- Avoid dead-ends identified
- Synthesize cross-student insights
- Propose meta-level improvements

Format: "Epsilon's Synthesized Approach:"
"""
        return {
            "cycle": cycle,
            "student": "Epsilon",
            "letter": "ε",
            "model": self.PROFILE.model,
            "role": self.PROFILE.role.value,
            "approach": "Meta-learning, pattern synthesis",
            "learned_patterns": learned_patterns
        }


class ZetaStudent:
    """Zeta (ζ) - CodeGemma: Computational Verification"""

    PROFILE = StudentProfile(
        letter="Zeta",
        model="codegemma:latest",
        role=StudentRole.COMPUTATIONAL,
        specialization="Computational implementation and verification",
        approach="Algorithm design and implementation",
        strengths=[
            "Algorithm design",
            "Code generation",
            "Computational verification",
            "Implementation details"
        ],
        weaknesses=[
            "Limited mathematical insight",
            "Focuses on mechanics not meaning",
            "May miss theoretical issues"
        ],
        prompt_style="computational"
    )

    def __init__(self, session_dir: Path):
        self.name = "zeta_student"
        self.letter = "Zeta"
        self.session_dir = Path(session_dir)
        self.proposals_dir = self.session_dir / "rh_proposals" / "zeta"
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.memory = AgentMemory(str(self.session_dir / "zeta_student.db"))

    def generate_proposal(self, cycle: int, theory: str = "") -> Dict:
        """Zeta generates computational approach."""
        prompt = f"""
[ZETA STUDENT - Cycle {cycle}]
Computational Verification of RH

You are the computational specialist. Design algorithms to test theories.

Based on theory:
{theory}

Your approach should:
1. Design efficient algorithms
2. Suggest computational tests
3. Outline implementation strategy
4. Identify numerical challenges
5. Propose verification benchmarks

Provide pseudocode or algorithm description.

Format: "Zeta's Computational Approach:"
"""
        return {
            "cycle": cycle,
            "student": "Zeta",
            "letter": "ζ",
            "model": self.PROFILE.model,
            "role": self.PROFILE.role.value,
            "approach": "Computational algorithms, implementation",
            "theory": theory[:500]
        }


# Factory for creating all students
class RHStudentCommittee:
    """Manages all 6 Greek students."""

    STUDENTS = [
        AlphaStudent,
        BetaStudent,
        GammaStudent,
        DeltaStudent,
        EpsilonStudent,
        ZetaStudent,
    ]

    def __init__(self, session_dir: Path):
        self.session_dir = Path(session_dir)
        self.students = [
            StudentClass(self.session_dir)
            for StudentClass in self.STUDENTS
        ]

    def generate_round(self, cycle: int) -> Dict[str, Dict]:
        """Have all students generate proposals for a cycle."""
        proposals = {}
        for student in self.students:
            try:
                proposal = student.generate_proposal(cycle)
                proposals[student.letter] = proposal
            except Exception as e:
                proposals[student.letter] = {
                    "error": str(e),
                    "cycle": cycle,
                    "student": student.letter
                }
        return proposals

    def get_committee_overview(self) -> Dict:
        """Get overview of all committee members."""
        return {
            "committee_size": len(self.students),
            "students": [
                {
                    "letter": student.letter,
                    "model": student.PROFILE.model,
                    "role": student.PROFILE.role.value,
                    "specialization": student.PROFILE.specialization,
                    "strengths": student.PROFILE.strengths,
                    "weaknesses": student.PROFILE.weaknesses,
                }
                for student in self.students
            ]
        }


# Singletons
_COMMITTEE = None


def get_student_committee(session_dir: Path = None) -> RHStudentCommittee:
    """Get or create the global student committee."""
    global _COMMITTEE
    if _COMMITTEE is None:
        if session_dir is None:
            session_dir = Path("/app")
        _COMMITTEE = RHStudentCommittee(session_dir)
    return _COMMITTEE


def get_student(letter: str, session_dir: Path = None):
    """Get a specific student by Greek letter."""
    committee = get_student_committee(session_dir)
    letter_map = {s.letter: s for s in committee.students}
    return letter_map.get(letter)
