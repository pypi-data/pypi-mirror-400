"""
Progressive Disclosure Loader
=============================

Implements the skill loading protocol from SKILL_STANDARD.md.

Memory hierarchy:
  Layer 0: Manifest + Schema (~2KB)  - Always loaded
  Layer 1: Class definition (~5KB)   - Loaded on reference
  Layer 2: Method execution (~20KB)  - Loaded on invoke
  Layer 3: Extended resources        - Loaded on demand
"""

import importlib
import importlib.util
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

import yaml

from skills.base import Skill, SkillContext, SkillMetadata, SkillResult

logger = logging.getLogger(__name__)


@dataclass
class SkillManifest:
    """Layer 0: Parsed manifest data."""

    id: str
    version: str
    name: str
    description: str
    category: str
    tags: List[str]
    level: str
    load_weight: str
    entry_point: str
    requires: List[str]
    capabilities: List[Dict[str, str]]
    permissions: Dict[str, Any]

    # Path info
    skill_dir: Path = field(default=None)
    schema: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, manifest_path: Path) -> "SkillManifest":
        """Parse manifest.yaml into SkillManifest."""
        with open(manifest_path) as f:
            data = yaml.safe_load(f)

        skill_dir = manifest_path.parent

        # Load schema if exists
        schema_path = skill_dir / "schema.json"
        schema = {}
        if schema_path.exists():
            with open(schema_path) as f:
                schema = json.load(f)

        return cls(
            id=data["id"],
            version=data["version"],
            name=data["name"],
            description=data["description"],
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            level=data.get("level", "intermediate"),
            load_weight=data.get("load_weight", "light"),
            entry_point=data["entry_point"],
            requires=data.get("requires", []),
            capabilities=data.get("capabilities", []),
            permissions=data.get("permissions", {}),
            skill_dir=skill_dir,
            schema=schema,
        )

    def memory_size(self) -> int:
        """Estimate memory footprint of Layer 0 data."""
        # Rough estimate: YAML + JSON strings
        return len(str(self.__dict__))


@dataclass
class SkillHandle:
    """
    Lazy handle to a skill - supports progressive disclosure.

    Layer 0 (manifest) is always available.
    Layer 1+ is loaded on demand.
    """

    manifest: SkillManifest
    _skill_class: Optional[Type[Skill]] = field(default=None, repr=False)
    _skill_instance: Optional[Skill] = field(default=None, repr=False)
    _load_attempted: bool = field(default=False, repr=False)

    @property
    def id(self) -> str:
        return self.manifest.id

    @property
    def is_loaded(self) -> bool:
        """Check if Layer 1 (class) is loaded."""
        return self._skill_class is not None

    def get_class(self) -> Optional[Type[Skill]]:
        """
        Load Layer 1: Import skill class.

        This triggers Python module import of skill.py.
        """
        if self._skill_class is not None:
            return self._skill_class

        if self._load_attempted:
            return None  # Previous load failed

        self._load_attempted = True

        try:
            # Parse entry point: "skill.py:ClassName"
            module_file, class_name = self.manifest.entry_point.split(":")
            module_path = self.manifest.skill_dir / module_file

            if not module_path.exists():
                logger.error(f"Skill module not found: {module_path}")
                return None

            # Dynamic import
            spec = importlib.util.spec_from_file_location(
                f"skill_{self.manifest.id.replace('/', '_')}",
                module_path,
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self._skill_class = getattr(module, class_name)
            logger.debug(f"Loaded skill class: {self.manifest.id}")
            return self._skill_class

        except Exception as e:
            logger.error(f"Failed to load skill {self.manifest.id}: {e}")
            return None

    def get_instance(self) -> Optional[Skill]:
        """
        Get or create skill instance.

        Loads Layer 1 if not already loaded.
        """
        if self._skill_instance is not None:
            return self._skill_instance

        skill_class = self.get_class()
        if skill_class is None:
            return None

        try:
            self._skill_instance = skill_class()
            return self._skill_instance
        except Exception as e:
            logger.error(f"Failed to instantiate skill {self.manifest.id}: {e}")
            return None

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """
        Execute skill (Layer 2).

        Validates input, loads skill if needed, executes, validates output.
        """
        # Rule I1: Input validation BEFORE loading code
        if not self._validate_input(input_data):
            return SkillResult(
                success=False,
                output=None,
                error="Input validation failed",
                error_code="INVALID_INPUT",
                skill_id=self.manifest.id,
            )

        # Load skill (Layer 1)
        skill = self.get_instance()
        if skill is None:
            return SkillResult(
                success=False,
                output=None,
                error="Failed to load skill",
                error_code="LOAD_FAILED",
                skill_id=self.manifest.id,
            )

        # Execute (Layer 2)
        try:
            # Hook: before_execute
            if hasattr(skill, "before_execute"):
                input_data = skill.before_execute(input_data, context)

            result = skill.execute(input_data, context)

            # Hook: after_execute
            if hasattr(skill, "after_execute"):
                result = skill.after_execute(result, context)

            # Rule I3: Output validation
            if result.success and not self._validate_output(result.output):
                return SkillResult(
                    success=False,
                    output=result.output,
                    error="Output schema violation",
                    error_code="SCHEMA_VIOLATION",
                    skill_id=self.manifest.id,
                )

            return result

        except Exception as e:
            # Hook: on_error
            if hasattr(skill, "on_error"):
                return skill.on_error(e, context)
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="EXECUTION_ERROR",
                skill_id=self.manifest.id,
            )

    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input against schema.json."""
        schema = self.manifest.schema.get("input", {})
        required = schema.get("required", [])

        # Check required fields
        for field in required:
            if field not in input_data:
                logger.warning(f"Missing required field: {field}")
                return False

        # Type validation (basic)
        properties = schema.get("properties", {})
        for key, value in input_data.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type and not self._check_type(value, expected_type):
                    logger.warning(f"Type mismatch for {key}: expected {expected_type}")
                    return False

        return True

    def _validate_output(self, output: Any) -> bool:
        """Validate output against schema.json."""
        if output is None:
            return True  # None output is valid for error cases

        schema = self.manifest.schema.get("output", {})
        required = schema.get("required", [])

        if isinstance(output, dict):
            for field in required:
                if field not in output:
                    return False

        return True

    @staticmethod
    def _check_type(value: Any, expected: str) -> bool:
        """Check if value matches expected JSON schema type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected_type = type_map.get(expected)
        if expected_type is None:
            return True  # Unknown type, allow
        return isinstance(value, expected_type)


class ProgressiveLoader:
    """
    Skill loader implementing progressive disclosure.

    Usage:
        loader = ProgressiveLoader()
        loader.scan("skills/")  # Loads only manifests (Layer 0)

        # Discovery - no code loaded yet
        skills = loader.find_by_category("code")

        # Invocation - loads code (Layer 1+)
        result = loader.execute("code/python", {"action": "format"}, context)
    """

    def __init__(self):
        self._handles: Dict[str, SkillHandle] = {}
        self._dependency_graph: Dict[str, List[str]] = {}

    def scan(self, root: Path, recursive: bool = True) -> int:
        """
        Scan directory for skills (Layer 0 only).

        Returns number of skills discovered.
        """
        root = Path(root)
        pattern = "**/manifest.yaml" if recursive else "*/manifest.yaml"

        count = 0
        for manifest_path in root.glob(pattern):
            try:
                manifest = SkillManifest.from_yaml(manifest_path)

                # Enforce size limit
                if manifest.memory_size() > 1024:
                    logger.warning(f"Manifest too large: {manifest.id}")
                    continue

                self._handles[manifest.id] = SkillHandle(manifest=manifest)
                self._dependency_graph[manifest.id] = manifest.requires
                count += 1
                logger.debug(f"Discovered skill: {manifest.id}")

            except Exception as e:
                logger.warning(f"Failed to parse {manifest_path}: {e}")

        return count

    def get(self, skill_id: str) -> Optional[SkillHandle]:
        """Get skill handle by ID (does not load code)."""
        return self._handles.get(skill_id)

    def find_by_category(self, category: str) -> List[SkillHandle]:
        """Find skills by category (Layer 0 only - no code loaded)."""
        return [
            h for h in self._handles.values()
            if h.manifest.category == category
        ]

    def find_by_tag(self, tag: str) -> List[SkillHandle]:
        """Find skills by tag (Layer 0 only)."""
        return [
            h for h in self._handles.values()
            if tag in h.manifest.tags
        ]

    def find_by_capability(self, capability: str) -> List[SkillHandle]:
        """Find skills that have a specific capability."""
        results = []
        for handle in self._handles.values():
            for cap in handle.manifest.capabilities:
                if cap.get("capability_id") == capability:
                    results.append(handle)
                    break
        return results

    def resolve_dependencies(self, skill_id: str) -> List[str]:
        """
        Resolve skill dependencies (Rule D3).

        Returns ordered list of skill IDs to load.
        """
        resolved = []
        seen = set()

        def visit(sid: str):
            if sid in seen:
                return
            seen.add(sid)

            deps = self._dependency_graph.get(sid, [])
            for dep in deps:
                if dep not in self._handles:
                    raise ValueError(f"Missing dependency: {dep}")
                visit(dep)

            resolved.append(sid)

        visit(skill_id)
        return resolved

    def execute(
        self,
        skill_id: str,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        """
        Execute a skill with full protocol (discovery → load → execute).
        """
        handle = self.get(skill_id)
        if handle is None:
            return SkillResult(
                success=False,
                output=None,
                error=f"Skill not found: {skill_id}",
                error_code="NOT_FOUND",
            )

        # Resolve and load dependencies first
        try:
            dep_order = self.resolve_dependencies(skill_id)
            for dep_id in dep_order[:-1]:  # All except target
                dep_handle = self.get(dep_id)
                if dep_handle and not dep_handle.is_loaded:
                    dep_handle.get_instance()  # Preload dependency
        except ValueError as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="DEPENDENCY_ERROR",
            )

        # Execute target skill
        return handle.execute(input_data, context)

    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics."""
        return {
            "discovered": len(self._handles),
            "loaded": sum(1 for h in self._handles.values() if h.is_loaded),
            "by_category": self._count_by_category(),
            "total_layer0_memory": sum(
                h.manifest.memory_size() for h in self._handles.values()
            ),
        }

    def _count_by_category(self) -> Dict[str, int]:
        """Count skills by category."""
        counts: Dict[str, int] = {}
        for handle in self._handles.values():
            cat = handle.manifest.category
            counts[cat] = counts.get(cat, 0) + 1
        return counts


# Singleton loader
_loader: Optional[ProgressiveLoader] = None


def get_loader() -> ProgressiveLoader:
    """Get the global progressive loader."""
    global _loader
    if _loader is None:
        _loader = ProgressiveLoader()
    return _loader
