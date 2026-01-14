"""
S2 Example Decompositions
=========================

Example skill decompositions demonstrating the S2 multi-scale architecture.

Examples:
- reasoning_s2: Explainable reasoning decomposed into L0-L3 scales
- memory_s2: Memory skill decomposed for hierarchical recall
- orchestrator_s2: Hybrid orchestrator with scale-aware delegation
"""

from .reasoning_s2 import (
    create_reasoning_composer,
    get_reasoning_skill_tree,
    run_example as run_reasoning_example,
)

from .memory_s2 import (
    create_memory_composer,
    get_memory_skill_tree,
    run_example as run_memory_example,
)

from .orchestrator_s2 import (
    create_orchestrator_composer,
    get_orchestrator_skill_tree,
    run_example as run_orchestrator_example,
)

__all__ = [
    # Reasoning
    "create_reasoning_composer",
    "get_reasoning_skill_tree",
    "run_reasoning_example",
    # Memory
    "create_memory_composer",
    "get_memory_skill_tree",
    "run_memory_example",
    # Orchestrator
    "create_orchestrator_composer",
    "get_orchestrator_skill_tree",
    "run_orchestrator_example",
]
