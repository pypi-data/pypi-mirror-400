"""
Base Skill Interface
====================

Defines the core abstractions for the skills system. Skills are modular units
of domain expertise that agents can invoke on-demand.

Design Principles:
1. Progressive Disclosure: Skills expose only necessary information
2. Schema-Driven: Input/output validation via JSON schemas
3. Composable: Skills can depend on and invoke other skills
4. Observable: Built-in logging and metrics support
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class SkillLevel(str, Enum):
    """Complexity level of a skill - affects when it's disclosed to agents."""
    BASIC = "basic"          # Always available, low token cost
    INTERMEDIATE = "intermediate"  # Loaded on relevant tasks
    ADVANCED = "advanced"    # Loaded only when explicitly needed
    EXPERT = "expert"        # Requires confirmation before loading


class SkillScale(str, Enum):
    """
    S² (Scaling on Scales) hierarchy level.

    Based on research showing smaller models at multiple scales
    outperform larger single-scale models via linear composition.
    """
    L0_MICRO = "L0"    # Atomic actions (≤10 tokens) - e.g., fetch-url, parse-json
    L1_MESO = "L1"     # Composed operations (30-50 tokens) - e.g., extract-entities
    L2_MACRO = "L2"    # Bundled workflows (80-120 tokens) - e.g., research-topic
    L3_META = "L3"     # Orchestrators (variable) - e.g., autonomous-devops


class SkillCategory(str, Enum):
    """Primary domain categories for skill organization."""
    CODE = "code"            # Programming and development
    DATA = "data"            # Data processing and analysis
    WRITING = "writing"      # Content creation and editing
    RESEARCH = "research"    # Information gathering
    AUTOMATION = "automation"  # Workflow and task automation
    INTEGRATION = "integration"  # External service connections
    REASONING = "reasoning"  # Logic and problem-solving
    CREATIVE = "creative"    # Creative and generative tasks
    SYSTEM = "system"        # Core system behaviors and kernels
    FOUNDATIONAL = "foundational"  # Base capabilities used across domains


@dataclass
class SkillDependency:
    """Declares a dependency on another skill."""
    skill_id: str                    # e.g., "code/python"
    version: str = "*"               # Semantic version constraint
    optional: bool = False           # If true, skill works without it
    reason: str = ""                 # Why this dependency is needed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "optional": self.optional,
            "reason": self.reason,
        }


@dataclass
class SkillMetadata:
    """
    Metadata describing a skill's capabilities and requirements.
    This is the "manifest" that enables discovery and progressive disclosure.
    """
    id: str                          # Unique identifier (e.g., "code/python/refactor")
    name: str                        # Human-readable name
    description: str                 # Short description (shown in listings)
    version: str = "0.1.0"

    # Classification
    category: SkillCategory = SkillCategory.CODE
    level: SkillLevel = SkillLevel.INTERMEDIATE
    tags: List[str] = field(default_factory=list)

    # S² Multi-Scale Architecture
    scale: SkillScale = SkillScale.L2_MACRO  # Default to macro for backward compat
    sub_skills: List[str] = field(default_factory=list)  # Child skill IDs for composition
    token_budget: int = 100          # Max tokens for this scale level

    # Documentation
    long_description: str = ""       # Full documentation (loaded on demand)
    examples: List[Dict[str, Any]] = field(default_factory=list)

    # Dependencies
    dependencies: List[SkillDependency] = field(default_factory=list)

    # Resource requirements
    requires_model: Optional[str] = None  # Specific model requirement
    requires_tools: List[str] = field(default_factory=list)  # External tools
    estimated_tokens: int = 500      # Approximate token cost when loaded

    # Authorship
    author: str = "CLI AI Team"
    license: str = "MIT"
    repository: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category.value,
            "level": self.level.value,
            "tags": self.tags,
            # S² fields
            "scale": self.scale.value,
            "sub_skills": self.sub_skills,
            "token_budget": self.token_budget,
            # Documentation
            "long_description": self.long_description,
            "examples": self.examples,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "requires_model": self.requires_model,
            "requires_tools": self.requires_tools,
            "estimated_tokens": self.estimated_tokens,
            "author": self.author,
            "license": self.license,
            "repository": self.repository,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillMetadata":
        dependencies = [
            SkillDependency(**d) for d in data.get("dependencies", [])
        ]
        # Parse S² scale with backward compatibility
        scale_str = data.get("scale", "L2")
        try:
            scale = SkillScale(scale_str)
        except ValueError:
            scale = SkillScale.L2_MACRO

        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            version=data.get("version", "0.1.0"),
            category=SkillCategory(data.get("category", "code")),
            level=SkillLevel(data.get("level", "intermediate")),
            tags=data.get("tags", []),
            # S² fields
            scale=scale,
            sub_skills=data.get("sub_skills", []),
            token_budget=data.get("token_budget", 100),
            # Documentation
            long_description=data.get("long_description", ""),
            examples=data.get("examples", []),
            dependencies=dependencies,
            requires_model=data.get("requires_model"),
            requires_tools=data.get("requires_tools", []),
            estimated_tokens=data.get("estimated_tokens", 500),
            author=data.get("author", "CLI AI Team"),
            license=data.get("license", "MIT"),
            repository=data.get("repository", ""),
        )


@dataclass
class SkillContext:
    """
    Runtime context passed to skill execution.
    Provides access to system resources and state.
    """
    # User/session info
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # System resources
    kb_context: Optional[str] = None       # Knowledge base context
    memory_context: Optional[str] = None   # H-Net memory context

    # Agent info
    agent_role: Optional[str] = None       # Which agent is invoking
    agent_model: Optional[str] = None      # Model being used

    # Execution settings
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout_seconds: int = 60

    # Skill chaining
    parent_skill: Optional[str] = None     # If called from another skill
    depth: int = 0                         # Nesting depth

    # S² Multi-Scale Context
    current_scale: Optional[str] = None    # Current execution scale (L0-L3)
    scale_context: Dict[str, Any] = field(default_factory=dict)  # Per-scale state
    scale_embeddings: Dict[str, List[float]] = field(default_factory=dict)  # Per-scale 384-dim

    # Custom data
    extra: Dict[str, Any] = field(default_factory=dict)

    def with_extra(self, **kwargs) -> "SkillContext":
        """Return a new context with additional extra data."""
        new_extra = {**self.extra, **kwargs}
        return SkillContext(
            user_id=self.user_id,
            session_id=self.session_id,
            kb_context=self.kb_context,
            memory_context=self.memory_context,
            agent_role=self.agent_role,
            agent_model=self.agent_model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout_seconds=self.timeout_seconds,
            parent_skill=self.parent_skill,
            depth=self.depth,
            extra=new_extra,
        )


@dataclass
class SkillResult:
    """
    Result of a skill execution.
    Includes the output, any artifacts, and execution metadata.
    """
    success: bool
    output: Any                           # Primary result

    # Artifacts (files, data structures produced)
    artifacts: Dict[str, Any] = field(default_factory=dict)

    # Execution info
    tokens_used: int = 0
    execution_time_ms: int = 0
    skill_id: str = ""

    # Error handling
    error: Optional[str] = None
    error_code: Optional[str] = None

    # Suggestions for follow-up
    suggestions: List[str] = field(default_factory=list)
    related_skills: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "artifacts": self.artifacts,
            "tokens_used": self.tokens_used,
            "execution_time_ms": self.execution_time_ms,
            "skill_id": self.skill_id,
            "error": self.error,
            "error_code": self.error_code,
            "suggestions": self.suggestions,
            "related_skills": self.related_skills,
        }


class Skill(ABC):
    """
    Abstract base class for all skills.

    Skills provide domain expertise through a standard interface:
    1. metadata() - Returns skill description and requirements
    2. input_schema() - JSON schema for valid inputs
    3. output_schema() - JSON schema for outputs
    4. execute() - Performs the skill's function

    Example:
        class PythonRefactorSkill(Skill):
            def metadata(self):
                return SkillMetadata(
                    id="code/python/refactor",
                    name="Python Refactoring",
                    description="Refactors Python code for clarity and efficiency",
                    category=SkillCategory.CODE,
                )

            def execute(self, input_data, context):
                code = input_data["code"]
                # ... perform refactoring ...
                return SkillResult(success=True, output=refactored_code)
    """

    # Class-level cache for expensive resources
    _resources: Dict[str, Any] = {}
    _initialized: bool = False

    @abstractmethod
    def metadata(self) -> SkillMetadata:
        """Return the skill's metadata for discovery and disclosure."""
        pass

    def input_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for valid inputs.
        Override to provide specific validation.
        """
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }

    def output_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for outputs.
        Override to document expected output structure.
        """
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
            },
        }

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        One-time initialization of skill resources.
        Called lazily when skill is first loaded.
        """
        self._initialized = True
        logger.debug(f"Initialized skill: {self.metadata().id}")

    def cleanup(self) -> None:
        """Release any resources held by the skill."""
        self._resources.clear()
        self._initialized = False
        logger.debug(f"Cleaned up skill: {self.metadata().id}")

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Validate input against schema. Returns list of error messages.
        Empty list means valid input.
        """
        # Basic validation - subclasses can add jsonschema validation
        errors = []
        schema = self.input_schema()
        required = schema.get("required", [])
        for field in required:
            if field not in input_data:
                errors.append(f"Missing required field: {field}")
        return errors

    @abstractmethod
    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        """
        Execute the skill's primary function.

        Args:
            input_data: Validated input matching input_schema()
            context: Runtime context with system resources

        Returns:
            SkillResult with output and metadata
        """
        pass

    def get_prompt(self) -> str:
        """
        Return the skill's system prompt for LLM interactions.
        Override to provide custom prompts.
        """
        meta = self.metadata()
        return f"""You are executing the "{meta.name}" skill.

{meta.long_description or meta.description}

Follow these guidelines:
- Focus on the specific task requested
- Use the provided context when relevant
- Return structured output matching the expected format
"""

    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example inputs and expected outputs."""
        return self.metadata().examples

    def get_tools(self) -> List[Callable]:
        """
        Return any callable tools this skill provides.
        These can be invoked by the agent during execution.
        """
        return []

    def __repr__(self) -> str:
        meta = self.metadata()
        return f"<Skill {meta.id} v{meta.version}>"


class BaseSkill(Skill):
    """
    Backward-compatible base for skills that predate the Skill metadata API.

    Subclasses can define class attributes to describe themselves:
      SKILL_ID, SKILL_NAME, SKILL_DESCRIPTION, SKILL_CATEGORY, SKILL_LEVEL, SKILL_TAGS
    """

    SKILL_ID: Optional[str] = None
    SKILL_NAME: Optional[str] = None
    SKILL_DESCRIPTION: Optional[str] = None
    SKILL_CATEGORY: SkillCategory = SkillCategory.CODE
    SKILL_LEVEL: SkillLevel = SkillLevel.INTERMEDIATE
    SKILL_TAGS: List[str] = []

    def metadata(self) -> SkillMetadata:
        skill_id = self.SKILL_ID or self._derive_skill_id()
        name = self.SKILL_NAME or self.__class__.__name__.replace("Skill", "").replace("_", " ").strip()
        description = self.SKILL_DESCRIPTION or self._derive_description()
        category = self._coerce_category(self.SKILL_CATEGORY)
        level = self._coerce_level(self.SKILL_LEVEL)
        tags = list(self.SKILL_TAGS) if self.SKILL_TAGS else []

        return SkillMetadata(
            id=skill_id,
            name=name,
            description=description,
            category=category,
            level=level,
            tags=tags,
        )

    def _derive_description(self) -> str:
        doc = (self.__doc__ or "").strip()
        if not doc:
            return ""
        return doc.splitlines()[0].strip()

    def _derive_skill_id(self) -> str:
        module = self.__class__.__module__.replace(".", "/")
        class_name = self.__class__.__name__.replace("Skill", "")
        return f"{module}/{class_name}".lower()

    @staticmethod
    def _coerce_category(value: object) -> SkillCategory:
        if isinstance(value, SkillCategory):
            return value
        if isinstance(value, str):
            try:
                return SkillCategory(value.lower())
            except ValueError:
                return SkillCategory.CODE
        return SkillCategory.CODE

    @staticmethod
    def _coerce_level(value: object) -> SkillLevel:
        if isinstance(value, SkillLevel):
            return value
        if isinstance(value, str):
            try:
                return SkillLevel(value.lower())
            except ValueError:
                return SkillLevel.INTERMEDIATE
        return SkillLevel.INTERMEDIATE


class CompositeSkill(Skill):
    """
    A skill that combines multiple sub-skills into a workflow.
    Enables complex operations through skill composition.
    """

    def __init__(self, sub_skills: List[Skill]):
        self.sub_skills = sub_skills
        self._skill_map = {s.metadata().id: s for s in sub_skills}

    def get_sub_skill(self, skill_id: str) -> Optional[Skill]:
        return self._skill_map.get(skill_id)

    def execute_sub_skill(
        self,
        skill_id: str,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        """Execute a sub-skill with proper context chaining."""
        skill = self.get_sub_skill(skill_id)
        if not skill:
            return SkillResult(
                success=False,
                output=None,
                error=f"Sub-skill not found: {skill_id}",
                error_code="SUB_SKILL_NOT_FOUND",
            )

        # Update context for sub-skill
        sub_context = SkillContext(
            user_id=context.user_id,
            session_id=context.session_id,
            kb_context=context.kb_context,
            memory_context=context.memory_context,
            agent_role=context.agent_role,
            agent_model=context.agent_model,
            max_tokens=context.max_tokens,
            temperature=context.temperature,
            timeout_seconds=context.timeout_seconds,
            parent_skill=self.metadata().id,
            depth=context.depth + 1,
            extra=context.extra,
        )

        return skill.execute(input_data, sub_context)


class FunctionSkill(Skill):
    """
    Wraps a simple function as a skill.
    Useful for creating skills from existing utilities.

    Example:
        def my_function(text: str, uppercase: bool = False) -> str:
            return text.upper() if uppercase else text

        skill = FunctionSkill(
            func=my_function,
            skill_id="text/transform",
            name="Text Transformer",
            description="Transforms text based on options",
        )
    """

    def __init__(
        self,
        func: Callable,
        skill_id: str,
        name: str,
        description: str,
        category: SkillCategory = SkillCategory.CODE,
        level: SkillLevel = SkillLevel.BASIC,
        **metadata_kwargs,
    ):
        self._func = func
        self._metadata = SkillMetadata(
            id=skill_id,
            name=name,
            description=description,
            category=category,
            level=level,
            **metadata_kwargs,
        )

    def metadata(self) -> SkillMetadata:
        return self._metadata

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        import time
        start = time.time()

        try:
            result = self._func(**input_data)
            execution_time = int((time.time() - start) * 1000)

            return SkillResult(
                success=True,
                output=result,
                execution_time_ms=execution_time,
                skill_id=self._metadata.id,
            )
        except Exception as e:
            logger.exception(f"FunctionSkill execution failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="EXECUTION_ERROR",
                skill_id=self._metadata.id,
            )
