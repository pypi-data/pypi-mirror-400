"""
Skill Template
==============

Use this template as a starting point for creating new skills.
Copy this file to your skill directory and customize.

Steps:
1. Copy this file to skills/category/your-skill/skill.py
2. Create a manifest.yaml with your skill metadata
3. Implement the execute() method
4. Add tests in tests/skills/test_your_skill.py
"""

import time
from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillDependency,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class TemplateSkill(Skill):
    """
    Template skill implementation.

    Replace this docstring with a description of what your skill does.

    Capabilities:
    - List the main capabilities
    - Of your skill here
    - For documentation purposes
    """

    # Define task types your skill supports
    TASK_TYPES = ["task1", "task2", "task3"]

    def metadata(self) -> SkillMetadata:
        """
        Return skill metadata.

        This can also be loaded from a manifest.yaml file instead of
        being defined inline.
        """
        return SkillMetadata(
            # Unique identifier - format: category/subcategory/name
            id="category/template",

            # Human-readable name
            name="Template Skill",

            # Short description (shown in listings)
            description="A template skill for demonstration purposes.",

            # Version following semver
            version="0.1.0",

            # Primary category
            category=SkillCategory.CODE,

            # Complexity level (affects when skill is disclosed)
            level=SkillLevel.INTERMEDIATE,

            # Searchable tags
            tags=["template", "example"],

            # Full documentation (loaded on demand)
            long_description="""
This is the long description that provides detailed documentation
about the skill. It's only loaded when the skill is actually used,
supporting progressive disclosure.

Include:
- Detailed capability descriptions
- Usage examples
- Configuration options
- Known limitations
""",

            # Example inputs/outputs for documentation and testing
            examples=[
                {
                    "input": {"task": "task1", "data": "example"},
                    "output": {"result": "processed example"},
                },
            ],

            # Dependencies on other skills
            dependencies=[
                # SkillDependency(
                #     skill_id="other/skill",
                #     optional=True,
                #     reason="Why this dependency is needed",
                # ),
            ],

            # Required external tools/libraries
            requires_tools=[],

            # Approximate token cost when loaded
            estimated_tokens=500,

            # Authorship information
            author="Your Name",
            license="MIT",
            repository="https://github.com/your/repo",
        )

    def input_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for valid inputs.

        This schema is used for:
        - Input validation before execution
        - Documentation generation
        - IDE/editor autocompletion
        """
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "enum": self.TASK_TYPES,
                    "description": "The type of task to perform",
                },
                "data": {
                    "type": "string",
                    "description": "The data to process",
                },
                "options": {
                    "type": "object",
                    "description": "Optional configuration",
                    "properties": {
                        "verbose": {
                            "type": "boolean",
                            "default": False,
                        },
                    },
                },
            },
            "required": ["task", "data"],
        }

    def output_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for outputs.

        Documents the expected output structure.
        """
        return {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "The processed result",
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata about the result",
                },
            },
        }

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        One-time initialization of skill resources.

        Called lazily when skill is first loaded.
        Use for:
        - Loading models or data
        - Establishing connections
        - Pre-computing values
        """
        super().initialize(config)

        # Initialize your resources here
        # self._model = load_model()
        # self._cache = {}

    def cleanup(self) -> None:
        """
        Release any resources held by the skill.

        Called when skill is unloaded or system shuts down.
        """
        # Clean up your resources here
        # self._model = None
        # self._cache.clear()

        super().cleanup()

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        """
        Execute the skill's primary function.

        This is the main entry point for skill execution.

        Args:
            input_data: Validated input matching input_schema()
            context: Runtime context with system resources

        Returns:
            SkillResult with output and metadata
        """
        start_time = time.time()

        # Extract inputs
        task = input_data.get("task", "")
        data = input_data.get("data", "")
        options = input_data.get("options", {})
        verbose = options.get("verbose", False)

        try:
            # Route to appropriate handler based on task
            if task == "task1":
                result = self._handle_task1(data, context)
            elif task == "task2":
                result = self._handle_task2(data, context)
            elif task == "task3":
                result = self._handle_task3(data, context)
            else:
                return SkillResult(
                    success=False,
                    output=None,
                    error=f"Unknown task type: {task}",
                    error_code="INVALID_TASK",
                    skill_id=self.metadata().id,
                )

            # Calculate execution time
            execution_time = int((time.time() - start_time) * 1000)

            # Return successful result
            return SkillResult(
                success=True,
                output=result,
                execution_time_ms=execution_time,
                skill_id=self.metadata().id,

                # Suggest follow-up actions
                suggestions=self._get_suggestions(task, result),

                # Related skills the user might want
                related_skills=["category/related-skill"],
            )

        except Exception as e:
            # Handle errors gracefully
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="EXECUTION_ERROR",
                skill_id=self.metadata().id,
            )

    # -------------------------------------------------------------------------
    # Task Handlers
    # -------------------------------------------------------------------------

    def _handle_task1(self, data: str, context: SkillContext) -> Dict[str, Any]:
        """Handle task1."""
        # Implement task1 logic here
        return {
            "result": f"Processed task1: {data}",
            "metadata": {
                "task": "task1",
                "input_length": len(data),
            },
        }

    def _handle_task2(self, data: str, context: SkillContext) -> Dict[str, Any]:
        """Handle task2."""
        # Implement task2 logic here
        return {
            "result": f"Processed task2: {data}",
            "metadata": {
                "task": "task2",
            },
        }

    def _handle_task3(self, data: str, context: SkillContext) -> Dict[str, Any]:
        """Handle task3."""
        # Implement task3 logic here
        return {
            "result": f"Processed task3: {data}",
            "metadata": {
                "task": "task3",
            },
        }

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _get_suggestions(self, task: str, result: Dict) -> List[str]:
        """Generate follow-up suggestions based on task results."""
        suggestions = []

        if task == "task1":
            suggestions.append("Consider running task2 for further processing")

        return suggestions

    def get_prompt(self) -> str:
        """
        Return the skill's system prompt for LLM interactions.

        This prompt guides the LLM when the skill requires
        language model assistance.
        """
        return """You are executing the Template Skill.

Your role is to [describe what the LLM should do].

Guidelines:
- Guideline 1
- Guideline 2
- Guideline 3

When responding:
- Be specific and actionable
- Follow the output format specified
- Handle edge cases gracefully
"""

    def get_tools(self) -> List:
        """
        Return any callable tools this skill provides.

        These can be invoked by the agent during execution.
        """
        return [
            # Define callable tools here
            # self.tool_function,
        ]


# -----------------------------------------------------------------------------
# Optional: Convenience Functions
# -----------------------------------------------------------------------------

def create_template_skill() -> TemplateSkill:
    """Factory function for creating the skill."""
    return TemplateSkill()


# -----------------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Quick test when running directly
    skill = TemplateSkill()
    print(f"Skill: {skill.metadata().name}")
    print(f"ID: {skill.metadata().id}")
    print(f"Description: {skill.metadata().description}")

    # Test execution
    context = SkillContext(agent_role="test")
    result = skill.execute(
        {"task": "task1", "data": "test data"},
        context
    )
    print(f"Result: {result.output}")
    print(f"Success: {result.success}")
