"""
Tests for the Skills Framework
==============================

Tests cover:
- Base skill classes
- Registry operations
- Skill loading
- Discovery
- Agent integration
"""

import pytest
from pathlib import Path

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
    FunctionSkill,
)
from skills.registry import SkillRegistry, SkillNotFoundError
from skills.loader import SkillLoader
from skills.discovery import SkillDiscovery, IntentAnalysis


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def registry():
    """Create a fresh registry for each test."""
    return SkillRegistry()


@pytest.fixture
def context():
    """Create a basic skill context."""
    return SkillContext(
        user_id="test_user",
        session_id="test_session",
        agent_role="CTO",
    )


class MockSkill(Skill):
    """A mock skill for testing."""

    def __init__(self, skill_id="test/mock"):
        self._skill_id = skill_id

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id=self._skill_id,
            name="Mock Skill",
            description="A mock skill for testing",
            category=SkillCategory.CODE,
            level=SkillLevel.BASIC,
            tags=["test", "mock"],
        )

    def execute(self, input_data, context) -> SkillResult:
        return SkillResult(
            success=True,
            output={"echo": input_data.get("message", "")},
            skill_id=self._skill_id,
        )


@pytest.fixture
def mock_skill():
    """Create a mock skill."""
    return MockSkill()


# =============================================================================
# Base Classes Tests
# =============================================================================

class TestSkillMetadata:
    """Tests for SkillMetadata."""

    def test_create_metadata(self):
        """Test creating skill metadata."""
        meta = SkillMetadata(
            id="test/skill",
            name="Test Skill",
            description="A test skill",
            category=SkillCategory.CODE,
        )
        assert meta.id == "test/skill"
        assert meta.name == "Test Skill"
        assert meta.category == SkillCategory.CODE
        assert meta.level == SkillLevel.INTERMEDIATE  # default

    def test_metadata_to_dict(self):
        """Test converting metadata to dict."""
        meta = SkillMetadata(
            id="test/skill",
            name="Test Skill",
            description="A test skill",
            tags=["tag1", "tag2"],
        )
        d = meta.to_dict()
        assert d["id"] == "test/skill"
        assert d["tags"] == ["tag1", "tag2"]

    def test_metadata_from_dict(self):
        """Test creating metadata from dict."""
        data = {
            "id": "test/skill",
            "name": "Test Skill",
            "description": "A test skill",
            "category": "data",
            "level": "advanced",
        }
        meta = SkillMetadata.from_dict(data)
        assert meta.id == "test/skill"
        assert meta.category == SkillCategory.DATA
        assert meta.level == SkillLevel.ADVANCED


class TestSkillContext:
    """Tests for SkillContext."""

    def test_create_context(self):
        """Test creating a context."""
        ctx = SkillContext(
            user_id="user1",
            agent_role="CTO",
        )
        assert ctx.user_id == "user1"
        assert ctx.agent_role == "CTO"
        assert ctx.depth == 0

    def test_context_with_extra(self):
        """Test adding extra data to context."""
        ctx = SkillContext()
        new_ctx = ctx.with_extra(custom_key="custom_value")
        assert new_ctx.extra["custom_key"] == "custom_value"
        assert "custom_key" not in ctx.extra  # Original unchanged


class TestSkillResult:
    """Tests for SkillResult."""

    def test_success_result(self):
        """Test creating a success result."""
        result = SkillResult(
            success=True,
            output={"data": "test"},
            skill_id="test/skill",
        )
        assert result.success
        assert result.output["data"] == "test"
        assert result.error is None

    def test_error_result(self):
        """Test creating an error result."""
        result = SkillResult(
            success=False,
            output=None,
            error="Something went wrong",
            error_code="TEST_ERROR",
        )
        assert not result.success
        assert result.error == "Something went wrong"

    def test_result_to_dict(self):
        """Test converting result to dict."""
        result = SkillResult(
            success=True,
            output="test output",
            skill_id="test/skill",
        )
        d = result.to_dict()
        assert d["success"] is True
        assert d["output"] == "test output"


class TestFunctionSkill:
    """Tests for FunctionSkill wrapper."""

    def test_function_skill(self, context):
        """Test wrapping a function as a skill."""
        def my_func(text: str, uppercase: bool = False) -> str:
            return text.upper() if uppercase else text

        skill = FunctionSkill(
            func=my_func,
            skill_id="test/function",
            name="Function Skill",
            description="A function-based skill",
        )

        result = skill.execute(
            {"text": "hello", "uppercase": True},
            context
        )
        assert result.success
        assert result.output == "HELLO"


# =============================================================================
# Registry Tests
# =============================================================================

class TestSkillRegistry:
    """Tests for SkillRegistry."""

    def test_register_skill(self, registry, mock_skill):
        """Test registering a skill."""
        skill_id = registry.register(mock_skill)
        assert skill_id == "test/mock"
        assert registry.has_skill("test/mock")

    def test_get_skill(self, registry, mock_skill):
        """Test getting a registered skill."""
        registry.register(mock_skill)
        skill = registry.get_skill("test/mock")
        assert skill.metadata().id == "test/mock"

    def test_get_nonexistent_skill(self, registry):
        """Test getting a skill that doesn't exist."""
        with pytest.raises(SkillNotFoundError):
            registry.get_skill("nonexistent/skill")

    def test_unregister_skill(self, registry, mock_skill):
        """Test unregistering a skill."""
        registry.register(mock_skill)
        assert registry.has_skill("test/mock")
        registry.unregister("test/mock")
        assert not registry.has_skill("test/mock")

    def test_list_skills_by_category(self, registry):
        """Test listing skills by category."""
        skill1 = MockSkill("code/skill1")
        skill2 = MockSkill("code/skill2")
        registry.register(skill1)
        registry.register(skill2)

        skills = registry.list_skills(category=SkillCategory.CODE)
        assert len(skills) == 2

    def test_search_skills(self, registry, mock_skill):
        """Test searching for skills."""
        registry.register(mock_skill)
        results = registry.search_skills("mock")
        assert len(results) > 0
        assert results[0].id == "test/mock"

    def test_execute_skill(self, registry, mock_skill, context):
        """Test executing a skill through the registry."""
        registry.register(mock_skill)
        result = registry.execute_skill(
            "test/mock",
            {"message": "hello"},
            context
        )
        assert result.success
        assert result.output["echo"] == "hello"

    def test_get_stats(self, registry, mock_skill):
        """Test getting registry stats."""
        registry.register(mock_skill)
        stats = registry.get_stats()
        assert stats["total_skills"] == 1
        assert stats["loaded_skills"] == 1


# =============================================================================
# Discovery Tests
# =============================================================================

class TestSkillDiscovery:
    """Tests for SkillDiscovery."""

    def test_analyze_intent_code(self):
        """Test intent analysis for code queries."""
        discovery = SkillDiscovery()
        intent = discovery._analyze_intent("help me debug this python code")

        assert intent.primary_category == SkillCategory.CODE
        assert "debug" in intent.keywords or "python" in intent.keywords

    def test_analyze_intent_data(self):
        """Test intent analysis for data queries."""
        discovery = SkillDiscovery()
        intent = discovery._analyze_intent("analyze my CSV data and show statistics")

        assert intent.primary_category == SkillCategory.DATA
        assert "analyze" in intent.keywords or "data" in intent.keywords

    def test_analyze_intent_writing(self):
        """Test intent analysis for writing queries."""
        discovery = SkillDiscovery()
        intent = discovery._analyze_intent("help me write a blog article")

        assert intent.primary_category == SkillCategory.WRITING

    def test_discover_skills(self, registry):
        """Test discovering skills from a query."""
        # Register some skills
        registry.register(MockSkill("code/python"))
        registry.register(MockSkill("code/review"))

        discovery = SkillDiscovery(registry)
        matches = discovery.discover("help with python code")

        assert len(matches) > 0

    def test_browse_by_category(self, registry):
        """Test browsing skills by category."""
        registry.register(MockSkill("code/skill1"))
        registry.register(MockSkill("code/skill2"))

        discovery = SkillDiscovery(registry)
        by_category = discovery.browse_by_category()

        assert SkillCategory.CODE in by_category
        assert len(by_category[SkillCategory.CODE]) == 2


# =============================================================================
# Loader Tests
# =============================================================================

class TestSkillLoader:
    """Tests for SkillLoader."""

    def test_validate_skill_directory_missing_manifest(self, tmp_path):
        """Test validation fails without manifest."""
        loader = SkillLoader()
        is_valid, errors = loader.validate_skill_directory(tmp_path)
        assert not is_valid
        assert any("manifest" in e.lower() for e in errors)

    def test_create_skill_template(self, tmp_path):
        """Test creating a skill template."""
        loader = SkillLoader()
        skill_dir = tmp_path / "my_skill"

        loader.create_skill_template(
            directory=skill_dir,
            skill_id="test/my-skill",
            name="My Test Skill",
            description="A test skill",
            category=SkillCategory.CODE,
        )

        assert (skill_dir / "manifest.yaml").exists()
        assert (skill_dir / "skill.py").exists()
        assert (skill_dir / "README.md").exists()


# =============================================================================
# Integration Tests
# =============================================================================

class TestSkillExecution:
    """Integration tests for skill execution."""

    def test_full_skill_workflow(self, registry, context):
        """Test complete skill workflow."""
        # Create and register skill
        skill = MockSkill("test/workflow")
        registry.register(skill)

        # Execute skill
        result = registry.execute_skill(
            "test/workflow",
            {"message": "test message"},
            context
        )

        assert result.success
        assert result.output["echo"] == "test message"
        assert result.skill_id == "test/workflow"

    def test_skill_with_dependencies(self, registry, context):
        """Test skills with dependencies."""
        # Register dependency
        dep_skill = MockSkill("test/dependency")
        registry.register(dep_skill)

        # Create skill with dependency
        class SkillWithDep(MockSkill):
            def metadata(self):
                from skills.base import SkillDependency
                meta = super().metadata()
                return SkillMetadata(
                    id="test/with-dep",
                    name="Skill With Dependency",
                    description="Has a dependency",
                    category=SkillCategory.CODE,
                    dependencies=[
                        SkillDependency(
                            skill_id="test/dependency",
                            reason="Test dependency"
                        )
                    ],
                )

        skill = SkillWithDep()
        registry.register(skill)

        # Resolve dependencies
        deps = registry.resolve_dependencies("test/with-dep")
        assert "test/dependency" in deps


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
