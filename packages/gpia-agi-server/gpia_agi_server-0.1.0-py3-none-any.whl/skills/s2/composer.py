"""
S² Skill Composer
=================

Utilities for composing skills across scale levels.

The composer handles:
1. Planning: Decompose high-level goals into multi-scale execution plans
2. Execution: Run skills at appropriate scales with proper context
3. Aggregation: Compose results from lower scales into higher-scale outputs
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum
import logging
import time

from .context_stack import S2ContextStack, ScaleLevel, create_s2_context
from .transforms import S2Projector

logger = logging.getLogger(__name__)


@dataclass
class SkillNode:
    """A skill node in the execution plan."""
    skill_id: str
    scale: ScaleLevel
    inputs: Dict[str, Any] = field(default_factory=dict)
    children: List["SkillNode"] = field(default_factory=list)
    parallel: bool = False  # Can children run in parallel?


@dataclass
class CompositionPlan:
    """
    Multi-scale execution plan.

    Represents a tree of skills to execute, where each node
    can have children at lower scale levels.
    """
    root: SkillNode
    goal: str
    estimated_tokens: int = 0
    estimated_time_ms: int = 0

    def flatten(self) -> List[Tuple[ScaleLevel, str]]:
        """Flatten plan to ordered list of (scale, skill_id)."""
        result = []

        def traverse(node: SkillNode):
            for child in node.children:
                traverse(child)
            result.append((node.scale, node.skill_id))

        traverse(self.root)
        return result

    def get_skills_at_scale(self, scale: ScaleLevel) -> List[str]:
        """Get all skills at a specific scale level."""
        flat = self.flatten()
        return [skill_id for s, skill_id in flat if s == scale]

    def to_dict(self) -> Dict[str, Any]:
        def node_to_dict(node: SkillNode) -> Dict[str, Any]:
            return {
                "skill_id": node.skill_id,
                "scale": node.scale.value,
                "inputs": node.inputs,
                "children": [node_to_dict(c) for c in node.children],
                "parallel": node.parallel,
            }

        return {
            "goal": self.goal,
            "root": node_to_dict(self.root),
            "estimated_tokens": self.estimated_tokens,
            "estimated_time_ms": self.estimated_time_ms,
        }


class S2Composer:
    """
    Composes and executes multi-scale skill workflows.

    This is the main orchestrator for S² execution:
    1. Takes a high-level goal
    2. Creates an execution plan across scales
    3. Executes skills bottom-up (L0 -> L1 -> L2 -> L3)
    4. Composes results via linear transforms
    """

    def __init__(
        self,
        skill_registry: Optional[Dict[str, Any]] = None,
        projector: Optional[S2Projector] = None,
    ):
        self.skill_registry = skill_registry or {}
        self.projector = projector or S2Projector()
        self._execution_history: List[Dict[str, Any]] = []

    def register_skill(self, skill_id: str, skill: Any, scale: ScaleLevel) -> None:
        """Register a skill with its scale level."""
        self.skill_registry[skill_id] = {
            "skill": skill,
            "scale": scale,
        }
        logger.debug(f"Registered skill {skill_id} at scale {scale.value}")

    def create_plan(
        self,
        goal: str,
        meta_skill_id: str,
        skill_tree: Dict[str, List[str]],  # parent -> children mapping
    ) -> CompositionPlan:
        """
        Create an execution plan from a skill tree definition.

        Args:
            goal: High-level goal description
            meta_skill_id: Root L3 meta-skill
            skill_tree: Mapping of skill_id -> list of child skill_ids
        """

        def build_node(skill_id: str) -> SkillNode:
            info = self.skill_registry.get(skill_id, {})
            scale = info.get("scale", ScaleLevel.L2)

            children = skill_tree.get(skill_id, [])
            child_nodes = [build_node(c) for c in children]

            # Check if children can run in parallel (all same scale, no dependencies)
            parallel = len(child_nodes) > 1 and len(set(c.scale for c in child_nodes)) == 1

            return SkillNode(
                skill_id=skill_id,
                scale=scale,
                children=child_nodes,
                parallel=parallel,
            )

        root = build_node(meta_skill_id)

        # Estimate resources
        flat = []

        def count_nodes(node: SkillNode):
            flat.append(node)
            for c in node.children:
                count_nodes(c)

        count_nodes(root)

        # Rough estimates
        token_budgets = {ScaleLevel.L0: 10, ScaleLevel.L1: 40, ScaleLevel.L2: 100, ScaleLevel.L3: 150}
        estimated_tokens = sum(token_budgets.get(n.scale, 50) for n in flat)
        estimated_time_ms = len(flat) * 100  # ~100ms per skill

        return CompositionPlan(
            root=root,
            goal=goal,
            estimated_tokens=estimated_tokens,
            estimated_time_ms=estimated_time_ms,
        )

    def execute(
        self,
        plan: CompositionPlan,
        context: Optional[S2ContextStack] = None,
        executor: Optional[Callable[[str, Dict[str, Any], S2ContextStack], Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a composition plan.

        Args:
            plan: The execution plan
            context: Optional pre-initialized context
            executor: Function to execute individual skills (skill_id, inputs, context) -> result

        Returns:
            Execution results with composed outputs at each scale
        """
        if context is None:
            context = create_s2_context(plan.goal)

        if executor is None:
            executor = self._default_executor

        start_time = time.time()
        results = {}

        def execute_node(node: SkillNode) -> Any:
            # First execute children (bottom-up)
            child_results = []
            for child in node.children:
                child_result = execute_node(child)
                child_results.append(child_result)

            # Push to this node's scale level
            context.push(node.scale)

            # Provide child results as input
            if child_results:
                node.inputs["child_results"] = child_results

            # Execute this skill
            try:
                result = executor(node.skill_id, node.inputs, context)
                context.add_result(result)
                context.record_skill(node.skill_id)
                results[node.skill_id] = result
            except Exception as e:
                context.add_error(f"{node.skill_id}: {str(e)}")
                result = {"error": str(e)}

            # Pop back to parent scale
            context.pop()

            return result

        # Execute from root
        final_result = execute_node(plan.root)

        execution_time = int((time.time() - start_time) * 1000)

        execution_record = {
            "goal": plan.goal,
            "skills_executed": list(results.keys()),
            "execution_time_ms": execution_time,
            "summary": context.get_execution_summary(),
        }
        self._execution_history.append(execution_record)

        return {
            "result": final_result,
            "all_results": results,
            "context_summary": context.get_execution_summary(),
            "execution_time_ms": execution_time,
        }

    def _default_executor(
        self,
        skill_id: str,
        inputs: Dict[str, Any],
        context: S2ContextStack,
    ) -> Any:
        """Default skill executor - looks up in registry and calls execute()."""
        info = self.skill_registry.get(skill_id)
        if not info:
            return {"error": f"Skill not found: {skill_id}"}

        skill = info["skill"]
        if hasattr(skill, "execute"):
            # Create a basic SkillContext from S2ContextStack
            from ..base import SkillContext
            skill_context = SkillContext(
                extra=context.get_context(),
                current_scale=context.current_level.value,
            )
            return skill.execute(inputs, skill_context)
        elif callable(skill):
            return skill(**inputs)
        else:
            return {"error": f"Skill {skill_id} is not executable"}

    def decompose_skill(
        self,
        skill_id: str,
        target_scale: ScaleLevel = ScaleLevel.L0,
    ) -> Dict[str, Any]:
        """
        Analyze a skill and suggest decomposition into lower scales.

        This is a planning utility - actual decomposition requires
        implementing the sub-skills.
        """
        info = self.skill_registry.get(skill_id)
        if not info:
            return {"error": f"Skill not found: {skill_id}"}

        current_scale = info.get("scale", ScaleLevel.L2)

        # Suggest decomposition based on scale gap
        scale_order = [ScaleLevel.L0, ScaleLevel.L1, ScaleLevel.L2, ScaleLevel.L3]
        current_idx = scale_order.index(current_scale)
        target_idx = scale_order.index(target_scale)

        if target_idx >= current_idx:
            return {"message": f"Skill {skill_id} is already at or below {target_scale.value}"}

        layers_needed = current_idx - target_idx
        suggested_structure = {
            "original_skill": skill_id,
            "original_scale": current_scale.value,
            "target_scale": target_scale.value,
            "layers": [],
        }

        for i in range(layers_needed):
            layer_scale = scale_order[current_idx - i - 1]
            count = 3 if layer_scale == ScaleLevel.L0 else 2  # More micros, fewer mesos
            suggested_structure["layers"].append({
                "scale": layer_scale.value,
                "suggested_count": count,
                "naming_pattern": f"{skill_id}/{layer_scale.value}_*",
            })

        return suggested_structure


def quick_compose(
    skills: List[Tuple[str, ScaleLevel, Callable]],
    goal: str,
    skill_tree: Dict[str, List[str]],
) -> Dict[str, Any]:
    """
    Quick utility to compose and execute skills.

    Args:
        skills: List of (skill_id, scale, callable) tuples
        goal: Goal description
        skill_tree: Parent -> children mapping

    Returns:
        Execution results
    """
    composer = S2Composer()

    for skill_id, scale, func in skills:
        composer.register_skill(skill_id, func, scale)

    # Find root (skill with no parent)
    all_children = set()
    for children in skill_tree.values():
        all_children.update(children)

    root_id = None
    for skill_id, _, _ in skills:
        if skill_id not in all_children:
            root_id = skill_id
            break

    if not root_id:
        root_id = skills[-1][0]  # Last skill as root

    plan = composer.create_plan(goal, root_id, skill_tree)
    return composer.execute(plan)


class S2MultiModalComposer(S2Composer):
    """
    Extended S2Composer with multi-modal (text + visual) support.

    Integrates LLaVa for visual tasks and routes to appropriate
    models based on scale level and content type.
    """

    # Scale to model routing - All 5 LLM Partners
    # - codegemma: Fast atomic operations, intent parsing
    # - qwen3: Creative synthesis, code generation
    # - deepseek_r1: Deep reasoning, analysis, debugging
    # - llava: Visual tasks, image analysis, screenshots
    # - gpt_oss_20b: Complex synthesis, dispute resolution, arbiter
    SCALE_MODELS = {
        ScaleLevel.L0: {
            "text": "codegemma",
            "visual": "llava",
            "reasoning": "codegemma",
            "synthesis": "qwen3"
        },
        ScaleLevel.L1: {
            "text": "qwen3",
            "visual": "llava",
            "reasoning": "deepseek_r1",
            "synthesis": "qwen3"
        },
        ScaleLevel.L2: {
            "text": "qwen3",
            "visual": "llava",
            "reasoning": "deepseek_r1",
            "synthesis": "gpt_oss_20b"
        },
        ScaleLevel.L3: {
            "text": "deepseek_r1",
            "visual": "llava",
            "reasoning": "deepseek_r1",
            "synthesis": "gpt_oss_20b"
        },
    }

    def __init__(
        self,
        skill_registry: Optional[Dict[str, Any]] = None,
        projector: Optional["S2Projector"] = None,
        enable_visual: bool = True,
    ):
        super().__init__(skill_registry, projector)
        self.enable_visual = enable_visual
        self._visual_encoder = None
        self._multi_modal_router = None

    @property
    def visual_encoder(self):
        """Lazy load visual encoder."""
        if self._visual_encoder is None and self.enable_visual:
            try:
                from .visual import S2VisualEncoder
                self._visual_encoder = S2VisualEncoder()
            except ImportError:
                logger.warning("Visual encoder not available")
        return self._visual_encoder

    @property
    def multi_modal_router(self):
        """Lazy load multi-modal router."""
        if self._multi_modal_router is None and self.enable_visual:
            try:
                from .visual import S2MultiModalRouter
                self._multi_modal_router = S2MultiModalRouter()
            except ImportError:
                logger.warning("Multi-modal router not available")
        return self._multi_modal_router

    def get_model_for_scale(
        self,
        scale: ScaleLevel,
        has_visual: bool = False,
        task_type: str = "text"
    ) -> str:
        """
        Get appropriate model for scale and task type.

        Task types:
        - text: General text processing
        - visual: Image analysis (llava)
        - reasoning: Deep analysis, debugging (deepseek_r1)
        - synthesis: Multi-perspective, arbiter (gpt_oss_20b)
        """
        models = self.SCALE_MODELS.get(scale, self.SCALE_MODELS[ScaleLevel.L2])
        if has_visual:
            return models["visual"]
        return models.get(task_type, models["text"])

    def execute_with_routing(
        self,
        plan: CompositionPlan,
        context: Optional[S2ContextStack] = None,
        visual_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute plan with scale-aware model routing.

        Args:
            plan: The execution plan
            context: Optional context stack
            visual_context: Optional visual context (images, etc.)

        Returns:
            Execution results with model routing info
        """
        if context is None:
            context = create_s2_context(plan.goal)

        has_visual = visual_context is not None and self.enable_visual

        # Track which models were used
        model_usage = {}

        def routed_executor(skill_id: str, inputs: Dict[str, Any], ctx: S2ContextStack) -> Any:
            """Execute with model routing based on scale."""
            info = self.skill_registry.get(skill_id)
            if not info:
                return {"error": f"Skill not found: {skill_id}"}

            scale = info.get("scale", ScaleLevel.L2)
            model = self.get_model_for_scale(scale, has_visual)

            # Track model usage
            if model not in model_usage:
                model_usage[model] = []
            model_usage[model].append(skill_id)

            # Add visual context if available
            if has_visual and visual_context:
                inputs["visual_context"] = visual_context

            # Execute skill
            skill = info["skill"]
            if callable(skill):
                result = skill(**inputs, **ctx.get_context())
                result["_routed_model"] = model
                result["_scale"] = scale.value
                return result
            return {"error": f"Skill {skill_id} not callable"}

        # Execute with routed executor
        result = self.execute(plan, context, executor=routed_executor)

        # Add routing metadata
        result["model_routing"] = {
            "models_used": list(model_usage.keys()),
            "usage": model_usage,
            "visual_enabled": has_visual,
        }

        return result

    def compress_context(
        self,
        text: str,
        target_tokens: int = 100,
        scale: ScaleLevel = ScaleLevel.L2
    ) -> Dict[str, Any]:
        """
        Compress context using visual encoder.

        Uses LLaVa to intelligently compress large context.
        """
        if self.visual_encoder:
            return self.visual_encoder.compress_context(text, target_tokens, scale)
        else:
            # Fallback to simple truncation
            words = text.split()
            return {
                "compressed": " ".join(words[:target_tokens]),
                "original_tokens": len(words),
                "method": "truncation"
            }
