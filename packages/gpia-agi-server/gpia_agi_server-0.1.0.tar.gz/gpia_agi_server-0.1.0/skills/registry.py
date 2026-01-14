"""
Skill Registry
==============

Central registry for skill discovery, loading, and lifecycle management.
Implements lazy loading for progressive disclosure - skills are only
fully loaded when needed.

Features:
- Hierarchical skill organization (category/domain/skill)
- Lazy loading with metadata pre-scanning
- Dependency resolution and validation
- Thread-safe operations
- Plugin-style extensibility
"""

import importlib
import importlib.util
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)

logger = logging.getLogger(__name__)


@dataclass
class SkillEntry:
    """Registry entry for a skill (may be unloaded)."""
    metadata: SkillMetadata
    skill_class: Optional[Type[Skill]] = None
    instance: Optional[Skill] = None
    module_path: Optional[str] = None       # For lazy loading
    file_path: Optional[Path] = None        # Source file location
    load_count: int = 0                     # Usage tracking
    is_loaded: bool = False
    is_builtin: bool = False                # Bundled with CLI AI


class SkillNotFoundError(Exception):
    """Raised when a requested skill doesn't exist."""
    pass


class SkillLoadError(Exception):
    """Raised when a skill fails to load."""
    pass


class DependencyError(Exception):
    """Raised when skill dependencies cannot be resolved."""
    pass


class SkillRegistry:
    """
    Central registry for all available skills.

    Supports:
    - Lazy loading: Skills are scanned for metadata but not fully loaded
    - Discovery: Find skills by category, tags, or search
    - Lifecycle: Initialize, execute, and cleanup skills
    - Dependencies: Resolve and load skill dependencies
    - Thread-safety: Safe for concurrent access

    Usage:
        registry = SkillRegistry()
        registry.scan_directory(Path("skills/code"))

        # List available skills
        skills = registry.list_skills(category=SkillCategory.CODE)

        # Load and execute a skill
        skill = registry.get_skill("code/python/refactor")
        result = skill.execute({"code": "..."}, context)
    """

    def __init__(self):
        self._entries: Dict[str, SkillEntry] = {}
        self._by_category: Dict[SkillCategory, Set[str]] = {
            cat: set() for cat in SkillCategory
        }
        self._by_tag: Dict[str, Set[str]] = {}
        self._lock = threading.RLock()
        self._initialized = False

    def register(
        self,
        skill_or_class: Union[Skill, Type[Skill]],
        module_path: Optional[str] = None,
        file_path: Optional[Path] = None,
        is_builtin: bool = False,
    ) -> str:
        """
        Register a skill or skill class with the registry.

        Args:
            skill_or_class: Skill instance or class
            module_path: Module path for lazy loading
            file_path: Source file location
            is_builtin: Whether this is a bundled skill

        Returns:
            The skill's ID
        """
        with self._lock:
            # Handle both instances and classes
            if isinstance(skill_or_class, type):
                instance = skill_or_class()
                skill_class = skill_or_class
            else:
                instance = skill_or_class
                skill_class = type(skill_or_class)

            metadata = instance.metadata()
            skill_id = metadata.id

            entry = SkillEntry(
                metadata=metadata,
                skill_class=skill_class,
                instance=instance,
                module_path=module_path,
                file_path=file_path,
                is_loaded=True,
                is_builtin=is_builtin,
            )

            self._entries[skill_id] = entry
            self._by_category[metadata.category].add(skill_id)

            for tag in metadata.tags:
                if tag not in self._by_tag:
                    self._by_tag[tag] = set()
                self._by_tag[tag].add(skill_id)

            logger.info(f"Registered skill: {skill_id}")
            return skill_id

    def register_metadata(
        self,
        metadata: SkillMetadata,
        module_path: Optional[str],
        file_path: Optional[Path] = None,
        is_builtin: bool = False,
    ) -> str:
        """
        Register skill metadata for lazy loading.
        The skill won't be instantiated until accessed.
        """
        with self._lock:
            skill_id = metadata.id

            entry = SkillEntry(
                metadata=metadata,
                module_path=module_path,
                file_path=file_path,
                is_loaded=False,
                is_builtin=is_builtin,
            )

            self._entries[skill_id] = entry
            self._by_category[metadata.category].add(skill_id)

            for tag in metadata.tags:
                if tag not in self._by_tag:
                    self._by_tag[tag] = set()
                self._by_tag[tag].add(skill_id)

            logger.debug(f"Registered metadata for lazy skill: {skill_id}")
            return skill_id

    def unregister(self, skill_id: str) -> bool:
        """Remove a skill from the registry."""
        with self._lock:
            if skill_id not in self._entries:
                return False

            entry = self._entries[skill_id]

            # Cleanup if loaded
            if entry.is_loaded and entry.instance:
                try:
                    entry.instance.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up skill {skill_id}: {e}")

            # Remove from indices
            self._by_category[entry.metadata.category].discard(skill_id)
            for tag in entry.metadata.tags:
                if tag in self._by_tag:
                    self._by_tag[tag].discard(skill_id)

            del self._entries[skill_id]
            logger.info(f"Unregistered skill: {skill_id}")
            return True

    def get_metadata(self, skill_id: str) -> SkillMetadata:
        """Get skill metadata without loading the skill."""
        with self._lock:
            if skill_id not in self._entries:
                raise SkillNotFoundError(f"Skill not found: {skill_id}")
            return self._entries[skill_id].metadata

    def get_skill(
        self,
        skill_id: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Skill:
        """
        Get a skill instance, loading it if necessary.

        Args:
            skill_id: The skill's unique identifier
            config: Optional configuration for initialization

        Returns:
            Initialized Skill instance
        """
        with self._lock:
            if skill_id not in self._entries:
                raise SkillNotFoundError(f"Skill not found: {skill_id}")

            entry = self._entries[skill_id]

            # Load if not already loaded
            if not entry.is_loaded:
                self._load_skill(entry, config)

            entry.load_count += 1
            return entry.instance

    def _load_skill(
        self,
        entry: SkillEntry,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Load a skill from its module path."""
        if entry.is_loaded:
            return

        if not entry.module_path:
            raise SkillLoadError(
                f"Cannot load skill {entry.metadata.id}: no module path"
            )

        try:
            # Import the module
            module = importlib.import_module(entry.module_path)

            # Find the skill class
            skill_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, Skill)
                    and obj is not Skill
                    and hasattr(obj, "metadata")
                ):
                    # Check if this class matches our metadata
                    try:
                        test_instance = obj()
                        if test_instance.metadata().id == entry.metadata.id:
                            skill_class = obj
                            break
                    except Exception:
                        continue

            if not skill_class:
                raise SkillLoadError(
                    f"Could not find skill class in {entry.module_path}"
                )

            # Instantiate and initialize
            instance = skill_class()
            instance.initialize(config)

            entry.skill_class = skill_class
            entry.instance = instance
            entry.is_loaded = True

            logger.info(f"Loaded skill: {entry.metadata.id}")

        except Exception as e:
            logger.exception(f"Failed to load skill {entry.metadata.id}")
            raise SkillLoadError(f"Failed to load {entry.metadata.id}: {e}")

    def has_skill(self, skill_id: str) -> bool:
        """Check if a skill is registered."""
        return skill_id in self._entries

    def is_loaded(self, skill_id: str) -> bool:
        """Check if a skill is currently loaded."""
        entry = self._entries.get(skill_id)
        return entry.is_loaded if entry else False

    def list_skills(
        self,
        category: Optional[SkillCategory] = None,
        level: Optional[SkillLevel] = None,
        tags: Optional[List[str]] = None,
        loaded_only: bool = False,
    ) -> List[SkillMetadata]:
        """
        List skills matching the given criteria.

        Args:
            category: Filter by category
            level: Filter by complexity level
            tags: Filter by tags (any match)
            loaded_only: Only return currently loaded skills

        Returns:
            List of matching SkillMetadata
        """
        with self._lock:
            results = []

            for skill_id, entry in self._entries.items():
                # Apply filters
                if category and entry.metadata.category != category:
                    continue
                if level and entry.metadata.level != level:
                    continue
                if loaded_only and not entry.is_loaded:
                    continue
                if tags:
                    if not any(tag in entry.metadata.tags for tag in tags):
                        continue

                results.append(entry.metadata)

            # Sort by category, then level, then name
            results.sort(key=lambda m: (
                m.category.value,
                m.level.value,
                m.name,
            ))

            return results

    def search_skills(
        self,
        query: str,
        limit: int = 10,
    ) -> List[SkillMetadata]:
        """
        Search skills by name, description, or tags.

        Args:
            query: Search query (case-insensitive)
            limit: Maximum results to return

        Returns:
            List of matching SkillMetadata, ranked by relevance
        """
        with self._lock:
            query_lower = query.lower()
            scored = []

            for entry in self._entries.values():
                meta = entry.metadata
                score = 0

                # Score by match location
                if query_lower in meta.id.lower():
                    score += 10
                if query_lower in meta.name.lower():
                    score += 8
                if query_lower in meta.description.lower():
                    score += 4
                if any(query_lower in tag.lower() for tag in meta.tags):
                    score += 6

                if score > 0:
                    scored.append((score, meta))

            # Sort by score descending
            scored.sort(key=lambda x: x[0], reverse=True)

            return [meta for _, meta in scored[:limit]]

    def get_categories(self) -> Dict[SkillCategory, int]:
        """Get all categories with skill counts."""
        with self._lock:
            return {
                cat: len(ids) for cat, ids in self._by_category.items()
                if ids
            }

    def get_tags(self) -> Dict[str, int]:
        """Get all tags with skill counts."""
        with self._lock:
            return {tag: len(ids) for tag, ids in self._by_tag.items()}

    def resolve_dependencies(
        self,
        skill_id: str,
        resolved: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Resolve all dependencies for a skill.

        Returns:
            List of skill IDs in load order (dependencies first)
        """
        if resolved is None:
            resolved = set()

        if skill_id in resolved:
            return []

        if skill_id not in self._entries:
            raise SkillNotFoundError(f"Skill not found: {skill_id}")

        entry = self._entries[skill_id]
        load_order = []

        for dep in entry.metadata.dependencies:
            if dep.skill_id not in self._entries:
                if not dep.optional:
                    raise DependencyError(
                        f"Missing required dependency: {dep.skill_id} "
                        f"(required by {skill_id})"
                    )
                continue

            # Recursively resolve
            sub_deps = self.resolve_dependencies(dep.skill_id, resolved)
            load_order.extend(sub_deps)

        resolved.add(skill_id)
        load_order.append(skill_id)

        return load_order

    def load_with_dependencies(
        self,
        skill_id: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Skill:
        """
        Load a skill and all its dependencies.

        Args:
            skill_id: The skill to load
            config: Configuration passed to all skills

        Returns:
            The loaded skill
        """
        load_order = self.resolve_dependencies(skill_id)

        for dep_id in load_order:
            if not self.is_loaded(dep_id):
                self.get_skill(dep_id, config)

        return self.get_skill(skill_id, config)

    def execute_skill(
        self,
        skill_id: str,
        input_data: Dict[str, Any],
        context: Optional[SkillContext] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> SkillResult:
        """
        Convenience method to load and execute a skill.

        Args:
            skill_id: The skill to execute
            input_data: Input for the skill
            context: Execution context
            config: Optional skill configuration

        Returns:
            SkillResult from execution
        """
        if context is None:
            context = SkillContext()

        try:
            skill = self.load_with_dependencies(skill_id, config)

            # Validate input
            errors = skill.validate_input(input_data)
            if errors:
                return SkillResult(
                    success=False,
                    output=None,
                    error="Input validation failed: " + "; ".join(errors),
                    error_code="VALIDATION_ERROR",
                    skill_id=skill_id,
                )

            return skill.execute(input_data, context)

        except SkillNotFoundError as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="SKILL_NOT_FOUND",
                skill_id=skill_id,
            )
        except Exception as e:
            logger.exception(f"Skill execution failed: {skill_id}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="EXECUTION_ERROR",
                skill_id=skill_id,
            )

    def unload_skill(self, skill_id: str) -> bool:
        """
        Unload a skill to free resources.
        The skill remains registered for future loading.
        """
        with self._lock:
            if skill_id not in self._entries:
                return False

            entry = self._entries[skill_id]

            if not entry.is_loaded:
                return True

            if entry.instance:
                try:
                    entry.instance.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up skill {skill_id}: {e}")

            entry.instance = None
            entry.is_loaded = False

            logger.info(f"Unloaded skill: {skill_id}")
            return True

    def cleanup_all(self) -> None:
        """Cleanup and unload all skills."""
        with self._lock:
            for skill_id in list(self._entries.keys()):
                self.unload_skill(skill_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            total = len(self._entries)
            loaded = sum(1 for e in self._entries.values() if e.is_loaded)
            builtin = sum(1 for e in self._entries.values() if e.is_builtin)

            return {
                "total_skills": total,
                "loaded_skills": loaded,
                "builtin_skills": builtin,
                "categories": self.get_categories(),
                "tag_count": len(self._by_tag),
            }


# Global registry instance
_registry: Optional[SkillRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> SkillRegistry:
    """Get the global skill registry."""
    global _registry
    with _registry_lock:
        if _registry is None:
            _registry = SkillRegistry()
        return _registry


def load_skill(
    skill_id: str,
    config: Optional[Dict[str, Any]] = None,
) -> Skill:
    """Convenience function to load a skill from the global registry."""
    return get_registry().load_with_dependencies(skill_id, config)
