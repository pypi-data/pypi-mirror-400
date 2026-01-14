"""
Tests for Minimal Reference Skill
=================================

Validates skill against the standard:
- Schema compliance
- Capability execution
- Error handling
- Progressive disclosure behavior
"""

import json
from pathlib import Path

import pytest
import yaml

# Test Layer 0: Manifest and Schema (no skill.py import)


class TestLayer0Discovery:
    """Tests that run WITHOUT importing skill.py - pure discovery."""

    @pytest.fixture
    def skill_dir(self):
        return Path(__file__).parent.parent

    def test_manifest_exists(self, skill_dir):
        """manifest.yaml must exist."""
        assert (skill_dir / "manifest.yaml").exists()

    def test_schema_exists(self, skill_dir):
        """schema.json must exist."""
        assert (skill_dir / "schema.json").exists()

    def test_manifest_required_fields(self, skill_dir):
        """manifest.yaml must have required fields."""
        with open(skill_dir / "manifest.yaml") as f:
            manifest = yaml.safe_load(f)

        required = ["id", "version", "name", "description", "category", "entry_point"]
        for field in required:
            assert field in manifest, f"Missing required field: {field}"

    def test_manifest_size_limit(self, skill_dir):
        """manifest.yaml must be <1KB."""
        size = (skill_dir / "manifest.yaml").stat().st_size
        assert size < 1024, f"manifest.yaml too large: {size} bytes"

    def test_schema_valid_json(self, skill_dir):
        """schema.json must be valid JSON."""
        with open(skill_dir / "schema.json") as f:
            schema = json.load(f)
        assert "input" in schema
        assert "output" in schema

    def test_manifest_id_matches_path(self, skill_dir):
        """Skill ID must match folder structure."""
        with open(skill_dir / "manifest.yaml") as f:
            manifest = yaml.safe_load(f)

        expected_id = f"{skill_dir.parent.name}/{skill_dir.name}"
        assert manifest["id"] == expected_id


# Test Layer 1 & 2: Skill Execution (imports skill.py)


class TestLayer1Interface:
    """Tests that import skill.py class definition."""

    @pytest.fixture
    def skill_class(self):
        from skills._reference.minimal.skill import MinimalSkill
        return MinimalSkill

    def test_skill_class_exists(self, skill_class):
        """Skill class must be importable."""
        assert skill_class is not None

    def test_skill_has_required_methods(self, skill_class):
        """Skill must implement required interface."""
        required_methods = ["metadata", "execute"]
        skill = skill_class()
        for method in required_methods:
            assert hasattr(skill, method), f"Missing method: {method}"

    def test_metadata_returns_correct_type(self, skill_class):
        """metadata() must return SkillMetadata."""
        from skills.base import SkillMetadata
        skill = skill_class()
        meta = skill.metadata()
        assert isinstance(meta, SkillMetadata)


class TestLayer2Execution:
    """Tests that execute skill methods."""

    @pytest.fixture
    def skill(self):
        from skills._reference.minimal.skill import MinimalSkill
        return MinimalSkill()

    @pytest.fixture
    def context(self):
        from skills.base import SkillContext
        return SkillContext(user_id="test", session_id="test")

    def test_echo_capability(self, skill, context):
        """Echo capability returns transformed text."""
        result = skill.execute(
            {"text": "hello", "transform": "upper", "capability": "echo"},
            context
        )
        assert result.success
        assert result.output["result"] == "HELLO"
        assert result.output["transform_applied"] == "upper"

    def test_validate_capability(self, skill, context):
        """Validate capability checks text."""
        result = skill.execute(
            {"text": "valid text", "capability": "validate"},
            context
        )
        assert result.success
        assert result.output["result"] == "valid"

    def test_empty_text_validation(self, skill, context):
        """Empty text fails validation."""
        result = skill.execute(
            {"text": "", "capability": "validate"},
            context
        )
        assert not result.success
        assert "not_empty" in result.output["failed_checks"]

    def test_unknown_capability_error(self, skill, context):
        """Unknown capability returns error."""
        result = skill.execute(
            {"text": "test", "capability": "nonexistent"},
            context
        )
        assert not result.success
        assert result.error_code == "UNKNOWN_CAPABILITY"

    def test_default_transform(self, skill, context):
        """Default transform is 'none'."""
        result = skill.execute({"text": "Hello"}, context)
        assert result.output["result"] == "Hello"
        assert result.output["transform_applied"] == "none"


class TestSchemaCompliance:
    """Tests output matches schema.json."""

    @pytest.fixture
    def schema(self):
        skill_dir = Path(__file__).parent.parent
        with open(skill_dir / "schema.json") as f:
            return json.load(f)

    @pytest.fixture
    def skill(self):
        from skills._reference.minimal.skill import MinimalSkill
        return MinimalSkill()

    @pytest.fixture
    def context(self):
        from skills.base import SkillContext
        return SkillContext()

    def test_output_has_required_fields(self, skill, context, schema):
        """Output contains all required fields from schema."""
        result = skill.execute({"text": "test"}, context)
        required = schema["output"].get("required", [])
        for field in required:
            assert field in result.output, f"Missing required output field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
