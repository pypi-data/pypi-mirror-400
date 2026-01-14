"""
Minimal Reference Skill - Layer 1 & 2 Implementation
=====================================================

This file is NOT loaded until the skill is first invoked.
Progressive disclosure:
  - Layer 0: manifest.yaml + schema.json (always loaded)
  - Layer 1: This file's class definition (loaded on reference)
  - Layer 2: Method bodies (executed on invoke)
  - Layer 3: scripts/, prompts/, data/ (loaded on demand)
"""

from typing import Any, Dict

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class MinimalSkill(Skill):
    """
    Reference implementation demonstrating the skill standard.

    This class is Layer 1 - its definition is loaded when the skill
    is first referenced, but method bodies (Layer 2) execute only
    when invoked.
    """

    # Class-level cache for metadata (avoids re-parsing manifest)
    _cached_metadata: SkillMetadata = None

    def metadata(self) -> SkillMetadata:
        """Return skill metadata. Uses cached version after first call."""
        if MinimalSkill._cached_metadata is None:
            MinimalSkill._cached_metadata = SkillMetadata(
                id="_reference/minimal",
                name="Minimal Reference Skill",
                description="Demonstrates progressive disclosure pattern",
                category=SkillCategory.SYSTEM,
                level=SkillLevel.BASIC,
                tags=["reference", "example", "minimal"],
            )
        return MinimalSkill._cached_metadata

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Main entry point - Layer 2 execution.

        Routes to capability-specific methods based on input.
        """
        capability = input_data.get("capability", "echo")

        # Route to capability method
        handler = getattr(self, f"capability_{capability}", None)
        if handler is None:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                error_code="UNKNOWN_CAPABILITY",
                skill_id=self.metadata().id,
            )

        return handler(input_data, context)

    def capability_echo(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Echo capability - transforms and returns text."""
        text = input_data.get("text", "")
        transform = input_data.get("transform", "none")

        # Apply transformation
        transformations = {
            "upper": str.upper,
            "lower": str.lower,
            "reverse": lambda s: s[::-1],
            "none": lambda s: s,
        }

        transformer = transformations.get(transform, lambda s: s)
        result = transformer(text)

        return SkillResult(
            success=True,
            output={
                "result": result,
                "original_length": len(text),
                "transform_applied": transform,
            },
            skill_id=self.metadata().id,
        )

    def capability_validate(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Validate capability - checks text against rules."""
        text = input_data.get("text", "")

        validations = {
            "not_empty": len(text) > 0,
            "not_too_long": len(text) <= 1000,
            "no_null_bytes": "\x00" not in text,
        }

        all_valid = all(validations.values())
        failed = [k for k, v in validations.items() if not v]

        return SkillResult(
            success=all_valid,
            output={
                "result": "valid" if all_valid else "invalid",
                "validations": validations,
                "failed_checks": failed,
            },
            error=f"Validation failed: {failed}" if not all_valid else None,
            skill_id=self.metadata().id,
        )

    # Hook points for extension
    def before_execute(self, input_data: Dict[str, Any], context: SkillContext) -> Dict[str, Any]:
        """Hook: Modify input before execution. Override in subclass."""
        return input_data

    def after_execute(self, result: SkillResult, context: SkillContext) -> SkillResult:
        """Hook: Modify result after execution. Override in subclass."""
        return result

    def on_error(self, error: Exception, context: SkillContext) -> SkillResult:
        """Hook: Handle errors. Override in subclass for recovery."""
        return SkillResult(
            success=False,
            output=None,
            error=str(error),
            error_code="EXECUTION_ERROR",
            skill_id=self.metadata().id,
        )
