"""
S2 (Scaling on Scales) Module
=============================

Multi-scale skill architecture based on research showing that smaller models
at multiple scales outperform larger single-scale models via linear composition.

Components:
- transforms: Linear projections between skill scales (L0 <-> L1 <-> L2 <-> L3)
- context_stack: Hierarchical context management for scale-aware execution
- composer: Skill composition utilities for multi-scale workflows
- visual: LLaVa integration for visual context encoding and multi-modal routing

Scale Hierarchy:
- L0 (Micro): Atomic actions, <=10 tokens (e.g., fetch-url, parse-json)
- L1 (Meso): Composed operations, 30-50 tokens (e.g., extract-entities)
- L2 (Macro): Bundled workflows, 80-120 tokens (e.g., research-topic)
- L3 (Meta): Orchestrators, variable tokens (e.g., autonomous-devops)

Model Routing by Scale:
- L0: CodeGemma (text), LLaVa (visual) - Fast atomic operations
- L1: Qwen3 (text), LLaVa (visual) - Composed operations
- L2: Qwen3 (text), LLaVa (visual) - Workflow execution
- L3: DeepSeek-R1 (text), LLaVa (visual) - Meta orchestration
"""

from .transforms import ScaleTransform, S2Projector
from .context_stack import S2ContextStack, ScaleState, ScaleLevel
from .composer import S2Composer, CompositionPlan, S2MultiModalComposer

# Visual components (LLaVa integration)
from .visual import (
    LLaVaClient,
    S2VisualEncoder,
    S2MultiModalRouter,
    S2VisualTransform,
    VisualContext,
    VisualTaskType,
)

__all__ = [
    # Core transforms
    "ScaleTransform",
    "S2Projector",
    # Context management
    "S2ContextStack",
    "ScaleState",
    "ScaleLevel",
    # Composition
    "S2Composer",
    "CompositionPlan",
    "S2MultiModalComposer",
    # Visual/LLaVa
    "LLaVaClient",
    "S2VisualEncoder",
    "S2MultiModalRouter",
    "S2VisualTransform",
    "VisualContext",
    "VisualTaskType",
]
