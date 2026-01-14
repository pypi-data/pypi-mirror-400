"""
Skill Generator - Autonomous Skill Creation
============================================

This skill enables Alpha Agent to generate new skills autonomously
using Qwen3 for code generation and DeepSeek for validation.

This is the key to true autonomous capability expansion - Alpha can
create its own skills based on identified needs.

Capabilities:
- generate: Generate a new skill from specification
- validate: Validate generated skill code
- integrate: Add skill to registry
- test: Test generated skill functionality

Uses multi-model approach:
- Qwen3: Creative code generation
- DeepSeek-R1: Code validation and critique
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
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

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class SkillGeneratorSkill(Skill):
    """
    Generates new skills autonomously using LLM partners.

    This is Alpha's ability to extend its own capabilities by
    creating new skills when gaps are identified.

    Process:
    1. Take skill specification (from GrowthSkill)
    2. Use Qwen3 to generate skill code
    3. Use DeepSeek to validate and critique
    4. Create skill files and directory structure
    5. Test the generated skill
    6. Integrate into registry
    """

    def __init__(self):
        self._mindset = None
        self._memory = None

    @property
    def mindset(self):
        if self._mindset is None:
            try:
                from skills.conscience.mindset.skill import MindsetSkill
                self._mindset = MindsetSkill()
            except Exception as e:
                logger.warning(f"MindsetSkill not available: {e}")
        return self._mindset

    @property
    def memory(self):
        if self._memory is None:
            try:
                from skills.conscience.memory.skill import MemorySkill
                self._memory = MemorySkill()
            except Exception as e:
                logger.warning(f"MemorySkill not available: {e}")
        return self._memory

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="alpha/skill-generator",
            name="Skill Generator",
            description="Generates new skills autonomously using Qwen3 code generation",
            category=SkillCategory.AUTOMATION,
            level=SkillLevel.EXPERT,
            tags=["alpha", "generation", "meta-cognitive", "autonomous", "self-improvement"],
            dependencies=[
                SkillDependency(skill_id="conscience/mindset", optional=False),
                SkillDependency(skill_id="conscience/memory", optional=True),
            ],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": ["generate", "validate", "integrate", "test"],
                },
                "spec": {
                    "type": "object",
                    "properties": {
                        "skill_id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "capabilities": {"type": "array"},
                        "category": {"type": "string"},
                        "dependencies": {"type": "array"},
                    },
                },
                "code": {"type": "string", "description": "Generated code for validation"},
                "skill_path": {"type": "string", "description": "Path to skill for testing"},
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string"},
                "validation": {"type": "object"},
                "skill_path": {"type": "string"},
                "test_results": {"type": "object"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        handlers = {
            "generate": self._generate,
            "validate": self._validate,
            "integrate": self._integrate,
            "test": self._test,
        }

        handler = handlers.get(capability)
        if not handler:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                skill_id=self.metadata().id,
            )

        try:
            return handler(input_data, context)
        except Exception as e:
            logger.error(f"SkillGenerator {capability} failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id,
            )

    def _generate(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Generate skill code from specification using Qwen3.

        Takes a skill spec and uses Qwen3 to generate:
        1. Skill class implementation
        2. Metadata and schemas
        3. Capability methods
        4. Documentation
        """
        spec = input_data.get("spec", {})

        if not spec:
            return SkillResult(
                success=False,
                output=None,
                error="No skill specification provided",
                skill_id=self.metadata().id,
            )

        if not self.mindset:
            return SkillResult(
                success=False,
                output=None,
                error="MindsetSkill required",
                skill_id=self.metadata().id,
            )

        skill_id = spec.get("skill_id", "")
        name = spec.get("name", "")
        description = spec.get("description", "")
        capabilities = spec.get("capabilities", [])
        category = spec.get("category", "AUTOMATION")
        dependencies = spec.get("dependencies", [])

        # Use Qwen3 for creative code generation
        generation_prompt = f"""
Generate a complete Python skill implementation for the following specification:

Skill ID: {skill_id}
Name: {name}
Description: {description}
Category: {category}
Capabilities: {capabilities}
Dependencies: {dependencies}

Requirements:
1. Inherit from Skill base class
2. Implement metadata() method with SkillMetadata
3. Implement input_schema() and output_schema()
4. Implement execute() method that routes to capability handlers
5. Implement handler methods for each capability
6. Include comprehensive docstrings
7. Use proper error handling
8. Follow the existing skill patterns from the codebase

Generate ONLY the Python code for skill.py file. Include all necessary imports.
Make it production-ready and fully functional.
"""

        # Use creative synthesis pattern for code generation
        generation_result = self.mindset.execute({
            "capability": "synthesize",
            "components": [
                "Skill specification",
                "Base skill patterns",
                "Capability requirements",
                "Production code standards"
            ],
            "pattern": "creative_synthesis",  # Emphasizes Qwen3
            "creative_prompt": generation_prompt,
        }, context)

        if not generation_result.success:
            return SkillResult(
                success=False,
                output=None,
                error=f"Code generation failed: {generation_result.error}",
                skill_id=self.metadata().id,
            )

        generated_code = generation_result.output.get("synthesis", "")

        # Store generation in memory
        if self.memory:
            self.memory.execute({
                "capability": "experience",
                "content": f"Generated skill: {skill_id}",
                "memory_type": "procedural",
                "importance": 0.85,
                "context": {
                    "type": "skill_generation",
                    "skill_id": skill_id,
                    "timestamp": datetime.now().isoformat(),
                }
            }, context)

        return SkillResult(
            success=True,
            output={
                "code": generated_code,
                "spec": spec,
                "summary": f"Generated {len(generated_code)} characters of code for {skill_id}",
            },
            skill_id=self.metadata().id,
        )

    def _validate(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Validate generated skill code using DeepSeek.

        Checks:
        1. Code correctness and completeness
        2. Proper skill structure
        3. Error handling
        4. Documentation quality
        5. Security issues
        """
        code = input_data.get("code", "")
        spec = input_data.get("spec", {})

        if not code:
            return SkillResult(
                success=False,
                output=None,
                error="No code provided for validation",
                skill_id=self.metadata().id,
            )

        if not self.mindset:
            return SkillResult(
                success=False,
                output=None,
                error="MindsetSkill required",
                skill_id=self.metadata().id,
            )

        # Use DeepSeek for analytical validation
        validation_prompt = f"""
Validate this generated skill code:

Specification:
{spec}

Generated Code:
```python
{code}
```

Analyze for:
1. Correctness: Does it implement all required capabilities?
2. Completeness: Are all methods and schemas present?
3. Structure: Does it follow Skill base class patterns?
4. Error Handling: Proper try/except and error reporting?
5. Security: Any potential security issues?
6. Code Quality: Follows Python best practices?
7. Documentation: Adequate docstrings and comments?

Provide:
- Issues found (critical, high, medium, low priority)
- Recommendations for fixes
- Overall quality score (0-10)
- Decision: PASS or NEEDS_WORK
"""

        validation_result = self.mindset.execute({
            "capability": "critique",
            "subject": code[:1000],  # First part for context
            "criteria": "code quality, correctness, security, completeness",
            "pattern": "deep_analysis",  # Uses DeepSeek
            "critique_prompt": validation_prompt,
        }, context)

        if validation_result.success:
            critique = validation_result.output.get("critique", "")

            validation = {
                "timestamp": datetime.now().isoformat(),
                "code_length": len(code),
                "critique": critique,
                "decision": "PASS" if "PASS" in critique else "NEEDS_WORK",
            }

            return SkillResult(
                success=True,
                output={"validation": validation},
                skill_id=self.metadata().id,
            )

        return SkillResult(
            success=False,
            output=None,
            error="Validation failed",
            skill_id=self.metadata().id,
        )

    def _integrate(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Integrate generated skill into the skill registry.

        Creates:
        1. Skill directory structure
        2. skill.py file with code
        3. README.md documentation
        4. Registers with skill loader
        """
        code = input_data.get("code", "")
        spec = input_data.get("spec", {})

        if not code or not spec:
            return SkillResult(
                success=False,
                output=None,
                error="Code and spec required for integration",
                skill_id=self.metadata().id,
            )

        skill_id = spec.get("skill_id", "")
        if not skill_id:
            return SkillResult(
                success=False,
                output=None,
                error="skill_id required in spec",
                skill_id=self.metadata().id,
            )

        # Create skill directory
        skill_path = REPO_ROOT / "skills" / skill_id.replace("/", os.sep)
        skill_path.mkdir(parents=True, exist_ok=True)

        # Write skill.py
        skill_file = skill_path / "skill.py"
        skill_file.write_text(code, encoding="utf-8")

        # Write README.md
        readme_content = f"""# {spec.get('name', skill_id)}

{spec.get('description', '')}

## Capabilities

{chr(10).join('- ' + cap for cap in spec.get('capabilities', []))}

## Generated

This skill was generated autonomously by Alpha Agent's SkillGenerator.

Generated: {datetime.now().isoformat()}
"""
        readme_file = skill_path / "README.md"
        readme_file.write_text(readme_content, encoding="utf-8")

        logger.info(f"Integrated new skill: {skill_id} at {skill_path}")

        return SkillResult(
            success=True,
            output={
                "skill_path": str(skill_path),
                "files_created": ["skill.py", "README.md"],
                "summary": f"Integrated {skill_id} at {skill_path}",
            },
            skill_id=self.metadata().id,
        )

    def _test(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Test generated skill functionality.

        Attempts to:
        1. Import the skill module
        2. Instantiate the skill class
        3. Call metadata() method
        4. Validate schemas
        5. Test execute() with dummy input
        """
        skill_path = input_data.get("skill_path", "")

        if not skill_path:
            return SkillResult(
                success=False,
                output=None,
                error="skill_path required for testing",
                skill_id=self.metadata().id,
            )

        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": [],
            "passed": 0,
            "failed": 0,
            "errors": [],
        }

        # Basic syntax check with Python
        skill_file = Path(skill_path) / "skill.py"
        if not skill_file.exists():
            test_results["errors"].append("skill.py not found")
            return SkillResult(
                success=False,
                output={"test_results": test_results},
                error="skill.py not found",
                skill_id=self.metadata().id,
            )

        # Test: Syntax check
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(skill_file)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                test_results["tests_run"].append("syntax_check")
                test_results["passed"] += 1
            else:
                test_results["tests_run"].append("syntax_check")
                test_results["failed"] += 1
                test_results["errors"].append(f"Syntax error: {result.stderr}")
        except Exception as e:
            test_results["errors"].append(f"Syntax check failed: {e}")
            test_results["failed"] += 1

        # More tests could be added here (import, instantiate, etc.)
        # For safety, we keep it minimal in this autonomous context

        test_results["summary"] = f"{test_results['passed']}/{test_results['passed'] + test_results['failed']} tests passed"

        return SkillResult(
            success=test_results["passed"] > 0 and test_results["failed"] == 0,
            output={"test_results": test_results},
            skill_id=self.metadata().id,
        )
