"""
S² Context Stack
================

Hierarchical context management for multi-scale skill execution.

Each scale level maintains its own context state. Child scales inherit
parent context but can only modify their own level. This prevents
lower-level skills from corrupting higher-level orchestration state.

Stack Structure:
    L3 (Meta)   <- Global goals, orchestration state
    L2 (Macro)  <- Task-level plans, workflow state
    L1 (Meso)   <- Subtask state, intermediate results
    L0 (Micro)  <- Immediate action state, atomic operations
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import copy
import logging
import time

logger = logging.getLogger(__name__)


class ScaleLevel(str, Enum):
    L0 = "L0"  # Micro
    L1 = "L1"  # Meso
    L2 = "L2"  # Macro
    L3 = "L3"  # Meta


@dataclass
class ScaleState:
    """State for a single scale level."""
    level: ScaleLevel
    data: Dict[str, Any] = field(default_factory=dict)
    results: List[Any] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    tokens_used: int = 0
    skills_executed: List[str] = field(default_factory=list)

    def set(self, key: str, value: Any) -> None:
        """Set a value in this scale's context."""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from this scale's context."""
        return self.data.get(key, default)

    def add_result(self, result: Any) -> None:
        """Add an execution result."""
        self.results.append(result)

    def add_error(self, error: str) -> None:
        """Record an error at this scale."""
        self.errors.append(error)

    def record_skill(self, skill_id: str, tokens: int = 0) -> None:
        """Record skill execution."""
        self.skills_executed.append(skill_id)
        self.tokens_used += tokens

    def elapsed_ms(self) -> int:
        """Time elapsed since scale started."""
        return int((time.time() - self.start_time) * 1000)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "data": self.data,
            "results_count": len(self.results),
            "errors": self.errors,
            "tokens_used": self.tokens_used,
            "skills_executed": self.skills_executed,
            "elapsed_ms": self.elapsed_ms(),
        }


class S2ContextStack:
    """
    Hierarchical context stack for S² multi-scale execution.

    Key principles:
    1. Each scale has isolated state
    2. Child scales inherit parent context (read-only)
    3. Results flow upward via composition
    4. Errors propagate upward immediately
    """

    def __init__(self):
        self.stack: Dict[ScaleLevel, ScaleState] = {
            ScaleLevel.L0: ScaleState(ScaleLevel.L0),
            ScaleLevel.L1: ScaleState(ScaleLevel.L1),
            ScaleLevel.L2: ScaleState(ScaleLevel.L2),
            ScaleLevel.L3: ScaleState(ScaleLevel.L3),
        }
        self.current_level: ScaleLevel = ScaleLevel.L2  # Default to macro
        self._execution_trace: List[Dict[str, Any]] = []

    def push(self, level: ScaleLevel) -> ScaleState:
        """
        Enter a scale level for execution.
        Returns the state for that level.
        """
        self.current_level = level
        state = self.stack[level]
        state.start_time = time.time()

        self._execution_trace.append({
            "action": "push",
            "level": level.value,
            "time": time.time(),
        })

        logger.debug(f"S2 push to {level.value}")
        return state

    def pop(self) -> Optional[ScaleState]:
        """
        Exit current scale level, returning its final state.
        Results are composed into the parent level.
        """
        state = self.stack[self.current_level]

        self._execution_trace.append({
            "action": "pop",
            "level": self.current_level.value,
            "results_count": len(state.results),
            "errors": state.errors,
            "time": time.time(),
        })

        # Move up to parent scale
        levels = [ScaleLevel.L0, ScaleLevel.L1, ScaleLevel.L2, ScaleLevel.L3]
        idx = levels.index(self.current_level)
        if idx < 3:
            self.current_level = levels[idx + 1]

        logger.debug(f"S2 pop from {state.level.value}, now at {self.current_level.value}")
        return state

    def get_context(self, level: Optional[ScaleLevel] = None) -> Dict[str, Any]:
        """
        Get merged context for a scale level.
        Includes inherited context from parent scales.
        """
        if level is None:
            level = self.current_level

        # Merge from top (L3) down to target level
        merged = {}
        levels = [ScaleLevel.L3, ScaleLevel.L2, ScaleLevel.L1, ScaleLevel.L0]
        level_idx = levels.index(level)

        for i in range(level_idx + 1):
            parent = levels[i]
            merged.update(self.stack[parent].data)

        return merged

    def set(self, key: str, value: Any, level: Optional[ScaleLevel] = None) -> None:
        """Set a value in the current or specified scale's context."""
        if level is None:
            level = self.current_level
        self.stack[level].set(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value, searching from current level up to L3."""
        levels = [ScaleLevel.L0, ScaleLevel.L1, ScaleLevel.L2, ScaleLevel.L3]
        start_idx = levels.index(self.current_level)

        for i in range(start_idx, 4):
            value = self.stack[levels[i]].get(key)
            if value is not None:
                return value
        return default

    def add_result(self, result: Any) -> None:
        """Add result to current scale."""
        self.stack[self.current_level].add_result(result)

    def add_error(self, error: str) -> None:
        """Add error to current scale (propagates to parent on pop)."""
        self.stack[self.current_level].add_error(error)

    def record_skill(self, skill_id: str, tokens: int = 0) -> None:
        """Record skill execution at current level."""
        self.stack[self.current_level].record_skill(skill_id, tokens)

    def get_all_results(self) -> Dict[str, List[Any]]:
        """Get results from all scale levels."""
        return {
            level.value: self.stack[level].results
            for level in ScaleLevel
        }

    def get_all_errors(self) -> Dict[str, List[str]]:
        """Get errors from all scale levels."""
        return {
            level.value: self.stack[level].errors
            for level in ScaleLevel
            if self.stack[level].errors
        }

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of the entire multi-scale execution."""
        total_tokens = sum(s.tokens_used for s in self.stack.values())
        all_skills = []
        for s in self.stack.values():
            all_skills.extend(s.skills_executed)

        return {
            "scales": {
                level.value: self.stack[level].to_dict()
                for level in ScaleLevel
            },
            "total_tokens": total_tokens,
            "total_skills": len(all_skills),
            "skills_executed": all_skills,
            "has_errors": any(s.errors for s in self.stack.values()),
            "trace_length": len(self._execution_trace),
        }

    def reset(self, level: Optional[ScaleLevel] = None) -> None:
        """Reset state for a specific level or all levels."""
        if level:
            self.stack[level] = ScaleState(level)
        else:
            for lvl in ScaleLevel:
                self.stack[lvl] = ScaleState(lvl)
            self._execution_trace = []

    def clone(self) -> "S2ContextStack":
        """Create a deep copy of the context stack."""
        new_stack = S2ContextStack()
        new_stack.stack = copy.deepcopy(self.stack)
        new_stack.current_level = self.current_level
        new_stack._execution_trace = copy.deepcopy(self._execution_trace)
        return new_stack


def create_s2_context(
    goal: str,
    agent_role: Optional[str] = None,
    initial_data: Optional[Dict[str, Any]] = None,
) -> S2ContextStack:
    """
    Create a new S² context stack with initial meta-level state.

    Args:
        goal: High-level goal for the execution
        agent_role: Which agent is executing
        initial_data: Additional context data
    """
    stack = S2ContextStack()

    # Set meta-level (L3) context
    meta = stack.push(ScaleLevel.L3)
    meta.set("goal", goal)
    meta.set("agent_role", agent_role)
    if initial_data:
        for k, v in initial_data.items():
            meta.set(k, v)

    return stack
