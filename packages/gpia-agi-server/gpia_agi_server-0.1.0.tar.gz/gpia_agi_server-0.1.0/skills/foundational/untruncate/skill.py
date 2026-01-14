"""
Untruncate Skill - Handle Truncated LLM Outputs

Created: 2025-12-30T12:00:59.866017
Taught by: Professor Agent
Learned by: Alpha Agent
Models used: DeepSeek-R1 (definition), Qwen3 (design), CodeGemma (code)

This skill enables agents to detect, handle, and prevent truncated outputs
from LLM calls.
"""

import requests
import re
from typing import List, Optional, Tuple
from skills.base import Skill, SkillMetadata, SkillContext, SkillResult, SkillCategory, SkillLevel

OLLAMA_URL = "http://localhost:11434/api/generate"


class UntruncateSkill(Skill):
    """Detect and handle truncated LLM outputs."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="foundational/untruncate",
            name="Untruncate",
            description="Detect, handle, and prevent truncated LLM outputs",
            category=SkillCategory.FOUNDATIONAL,
            level=SkillLevel.INTERMEDIATE,
            tags=["llm", "output", "truncation", "validation", "continuation"],
        )

    def input_schema(self):
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["detect", "continue", "merge", "validate"]},
                "text": {"type": "string"},
                "parts": {"type": "array"},
                "expected_type": {"type": "string", "enum": ["code", "text", "json", "yaml"]},
                "original_prompt": {"type": "string"},
            },
            "required": ["capability"]
        }

    def output_schema(self):
        return {
            "type": "object",
            "properties": {
                "is_truncated": {"type": "boolean"},
                "continued_text": {"type": "string"},
                "merged_text": {"type": "string"},
                "is_complete": {"type": "boolean"},
                "issues": {"type": "array"},
            }
        }

    def execute(self, input_data, context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        if capability == "detect":
            return self._detect_truncation(input_data.get("text", ""))
        elif capability == "continue":
            return self._request_continuation(
                input_data.get("original_prompt", ""),
                input_data.get("text", "")
            )
        elif capability == "merge":
            return self._merge_outputs(input_data.get("parts", []))
        elif capability == "validate":
            return self._validate_completeness(
                input_data.get("text", ""),
                input_data.get("expected_type", "text")
            )
        else:
            return SkillResult(success=False, output=None, error=f"Unknown capability: {capability}")

    def _detect_truncation(self, text: str) -> SkillResult:
        """Detect if text appears truncated."""
        issues = []

        # Check for unclosed brackets
        open_parens = text.count('(') - text.count(')')
        open_brackets = text.count('[') - text.count(']')
        open_braces = text.count('{') - text.count('}')

        if open_parens > 0:
            issues.append(f"Unclosed parentheses: {open_parens}")
        if open_brackets > 0:
            issues.append(f"Unclosed brackets: {open_brackets}")
        if open_braces > 0:
            issues.append(f"Unclosed braces: {open_braces}")

        # Check for incomplete sentences
        stripped = text.rstrip()
        if stripped and stripped[-1] not in '.!?:"\'}])':
            if not stripped.endswith('```'):
                issues.append("Text ends mid-sentence")

        # Check for incomplete code blocks
        code_blocks = text.count('```')
        if code_blocks % 2 != 0:
            issues.append("Unclosed code block")

        # Check for common truncation patterns
        truncation_patterns = [
            r'\.\.\.$',  # Ends with ...
            r'and$', r'or$', r'the$', r'a$',  # Ends with article/conjunction
            r'def\s+\w+\([^)]*$',  # Incomplete function definition
            r'class\s+\w+[^:]*$',  # Incomplete class definition
        ]

        for pattern in truncation_patterns:
            if re.search(pattern, stripped, re.IGNORECASE):
                issues.append(f"Pattern suggests truncation: {pattern}")

        is_truncated = len(issues) > 0

        return SkillResult(
            success=True,
            output={
                "is_truncated": is_truncated,
                "issues": issues,
                "text_length": len(text)
            },
            skill_id=self.metadata().id
        )

    def _request_continuation(self, original_prompt: str, partial_output: str) -> SkillResult:
        """Request LLM to continue from partial output."""
        continuation_prompt = f"""
The following output was truncated. Continue from where it stopped.

ORIGINAL PROMPT:
{original_prompt[:500]}

PARTIAL OUTPUT (continue from here):
{partial_output[-500:]}

Continue immediately without repeating what was already written:
"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": "qwen3:latest",
                    "prompt": continuation_prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 2000}
                },
                timeout=120
            )

            if response.status_code == 200:
                continuation = response.json().get("response", "")
                return SkillResult(
                    success=True,
                    output={
                        "continued_text": continuation,
                        "method": "llm_continuation"
                    },
                    skill_id=self.metadata().id
                )

        except Exception as e:
            return SkillResult(success=False, output=None, error=str(e))

    def _merge_outputs(self, parts: List[str]) -> SkillResult:
        """Merge multiple partial outputs."""
        if not parts:
            return SkillResult(success=False, output=None, error="No parts provided")

        merged = parts[0]
        for i, part in enumerate(parts[1:], 1):
            # Find overlap between end of merged and start of new part
            overlap_found = False
            for overlap_len in range(min(100, len(merged), len(part)), 0, -1):
                if merged[-overlap_len:] == part[:overlap_len]:
                    merged = merged + part[overlap_len:]
                    overlap_found = True
                    break

            if not overlap_found:
                merged = merged + part

        return SkillResult(
            success=True,
            output={
                "merged_text": merged,
                "parts_count": len(parts),
                "total_length": len(merged)
            },
            skill_id=self.metadata().id
        )

    def _validate_completeness(self, text: str, expected_type: str) -> SkillResult:
        """Validate that output is complete for expected type."""
        issues = []
        is_complete = True

        if expected_type == "code":
            # Check Python code completeness
            if "def " in text and "return" not in text:
                issues.append("Function without return statement")
            if "class " in text and "def " not in text:
                issues.append("Class without methods")

        elif expected_type == "json":
            try:
                import json
                json.loads(text)
            except:
                issues.append("Invalid JSON")
                is_complete = False

        elif expected_type == "yaml":
            try:
                import yaml
                yaml.safe_load(text)
            except:
                issues.append("Invalid YAML")
                is_complete = False

        # General completeness checks
        detection_result = self._detect_truncation(text)
        if detection_result.output.get("is_truncated"):
            is_complete = False
            issues.extend(detection_result.output.get("issues", []))

        return SkillResult(
            success=True,
            output={
                "is_complete": is_complete,
                "expected_type": expected_type,
                "issues": issues
            },
            skill_id=self.metadata().id
        )
