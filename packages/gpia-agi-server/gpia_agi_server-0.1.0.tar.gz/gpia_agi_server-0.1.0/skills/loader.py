"""
Skill Loader
============

Handles discovery and loading of skills from the filesystem.
Supports progressive disclosure by scanning metadata without
full initialization.

Directory Structure:
    skills/
    ├── code/
    │   ├── python/
    │   │   ├── __init__.py
    │   │   ├── manifest.yaml      # Skill metadata
    │   │   ├── skill.py           # Skill implementation
    │   │   ├── prompts/           # Domain-specific prompts
    │   │   └── tools/             # Callable tools
    │   └── javascript/
    │       └── ...
    ├── data/
    │   └── ...
    └── ...
"""

import importlib
import importlib.util
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from skills.base import (
    Skill,
    SkillCategory,
    SkillLevel,
    SkillMetadata,
    SkillDependency,
)
from skills.registry import SkillRegistry, get_registry

logger = logging.getLogger(__name__)

# Standard files in a skill package
MANIFEST_FILES = ["manifest.yaml", "manifest.yml", "manifest.json", "skill.json"]
SKILL_FILES = ["skill.py", "__init__.py"]
PROMPT_DIR = "prompts"
TOOLS_DIR = "tools"


class SkillLoader:
    """
    Discovers and loads skills from the filesystem.

    Features:
    - Scans directories for skill packages
    - Parses manifests for metadata
    - Supports lazy loading (metadata only until needed)
    - Validates skill structure
    - Handles custom skill directories
    """

    def __init__(
        self,
        registry: Optional[SkillRegistry] = None,
        base_dirs: Optional[List[Path]] = None,
    ):
        self.registry = registry or get_registry()
        self.base_dirs = base_dirs or [
            Path(__file__).parent,  # Built-in skills
        ]
        if base_dirs is None:
            codex_home = os.getenv("CODEX_HOME")
            candidates = []
            if codex_home:
                candidates.append(Path(codex_home) / "skills")
            candidates.append(Path.home() / ".codex" / "skills")
            for path in candidates:
                if path.exists() and path not in self.base_dirs:
                    self.base_dirs.append(path)
        self._scanned: Set[Path] = set()

    def add_base_dir(self, path: Path) -> None:
        """Add a directory to scan for skills."""
        if path not in self.base_dirs:
            self.base_dirs.append(path)

    def scan_all(self, lazy: bool = True) -> int:
        """
        Scan all base directories for skills.

        Args:
            lazy: If True, only load metadata (not full skill)

        Returns:
            Number of skills discovered
        """
        total = 0
        for base_dir in self.base_dirs:
            if base_dir.exists():
                total += self.scan_directory(base_dir, lazy=lazy)
        return total

    def scan_directory(
        self,
        directory: Path,
        lazy: bool = True,
        category_prefix: str = "",
    ) -> int:
        """
        Scan a directory recursively for skill packages.

        A skill package is identified by having a manifest file.

        Args:
            directory: Directory to scan
            lazy: If True, only load metadata
            category_prefix: Prefix for skill IDs (e.g., "code/")

        Returns:
            Number of skills discovered
        """
        if directory in self._scanned:
            return 0

        self._scanned.add(directory)
        count = 0

        if not directory.exists():
            logger.warning(f"Skill directory does not exist: {directory}")
            return 0

        # Check if this directory is a skill package
        manifest_path = self._find_manifest(directory)
        if manifest_path:
            try:
                if lazy:
                    self._register_lazy(directory, manifest_path, category_prefix)
                else:
                    self._register_full(directory, manifest_path, category_prefix)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to register skill from {directory}: {e}")

        # Recursively scan subdirectories
        for subdir in directory.iterdir():
            if subdir.is_dir() and not subdir.name.startswith(("_", ".")):
                # Build category prefix from directory structure
                new_prefix = f"{category_prefix}{subdir.name}/"
                count += self.scan_directory(subdir, lazy=lazy, category_prefix=new_prefix)

        return count

    def _find_manifest(self, directory: Path) -> Optional[Path]:
        """Find the manifest file in a directory."""
        for filename in MANIFEST_FILES:
            path = directory / filename
            if path.exists():
                return path
        return None

    def _find_skill_file(self, directory: Path) -> Optional[Path]:
        """Find the skill implementation file."""
        for filename in SKILL_FILES:
            path = directory / filename
            if path.exists() and path != directory / "__init__.py":
                return path
        # Fall back to __init__.py if skill.py doesn't exist
        init_path = directory / "__init__.py"
        return init_path if init_path.exists() else None

    def _parse_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """Parse a manifest file (YAML or JSON)."""
        content = manifest_path.read_text(encoding="utf-8")

        if manifest_path.suffix in (".yaml", ".yml"):
            return yaml.safe_load(content)
        else:
            return json.loads(content)

    def _build_metadata(
        self,
        manifest: Dict[str, Any],
        directory: Path,
        category_prefix: str,
    ) -> SkillMetadata:
        """Build SkillMetadata from a manifest."""
        # Derive ID from directory structure if not specified
        skill_id = manifest.get("id") or manifest.get("skill_id") or f"{category_prefix}{directory.name}"
        skill_id = skill_id.rstrip("/")

        # Parse dependencies
        dependencies = []
        for dep in manifest.get("dependencies", []):
            if isinstance(dep, str):
                dependencies.append(SkillDependency(skill_id=dep))
            else:
                # Convert "required" to "optional" for backward compatibility
                dep_copy = dep.copy()
                if "required" in dep_copy:
                    dep_copy["optional"] = not dep_copy.pop("required")
                dependencies.append(SkillDependency(**dep_copy))

        # Parse category
        category_str = manifest.get("category", "code")
        try:
            category = SkillCategory(category_str.lower())
        except ValueError:
            category = SkillCategory.CODE

        # Parse level
        level_str = manifest.get("level", "intermediate")
        try:
            level = SkillLevel(level_str.lower())
        except ValueError:
            level = SkillLevel.INTERMEDIATE

        # Load long description from file if specified
        long_desc = manifest.get("long_description", "")
        if not long_desc:
            readme_path = directory / "README.md"
            if readme_path.exists():
                long_desc = readme_path.read_text(encoding="utf-8")
        if not long_desc:
            skill_doc = directory / "SKILL.md"
            if skill_doc.exists():
                long_desc = skill_doc.read_text(encoding="utf-8")

        return SkillMetadata(
            id=skill_id,
            name=manifest.get("name", directory.name.replace("_", " ").title()),
            description=manifest.get("description", ""),
            version=manifest.get("version", "0.1.0"),
            category=category,
            level=level,
            tags=manifest.get("tags", []),
            long_description=long_desc,
            examples=manifest.get("examples", []),
            dependencies=dependencies,
            requires_model=manifest.get("requires_model"),
            requires_tools=manifest.get("requires_tools", []),
            estimated_tokens=manifest.get("estimated_tokens", 500),
            author=manifest.get("author", "CLI AI Team"),
            license=manifest.get("license", "MIT"),
            repository=manifest.get("repository", ""),
        )

    def _register_lazy(
        self,
        directory: Path,
        manifest_path: Path,
        category_prefix: str,
    ) -> None:
        """Register skill metadata without loading the implementation."""
        manifest = self._parse_manifest(manifest_path)
        metadata = self._build_metadata(manifest, directory, category_prefix)

        # Determine module path for lazy loading
        skill_file = self._find_skill_file(directory)
        if skill_file:
            # Build module path relative to skills package
            rel_path = skill_file.relative_to(Path(__file__).parent.parent)
            module_path = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
        else:
            module_path = None

        self.registry.register_metadata(
            metadata=metadata,
            module_path=module_path,
            file_path=directory,
            is_builtin=directory.is_relative_to(Path(__file__).parent),
        )

        logger.debug(f"Registered lazy skill: {metadata.id}")

    def _register_full(
        self,
        directory: Path,
        manifest_path: Path,
        category_prefix: str,
    ) -> None:
        """Register and fully load a skill."""
        manifest = self._parse_manifest(manifest_path)
        metadata = self._build_metadata(manifest, directory, category_prefix)

        skill_file = self._find_skill_file(directory)
        if not skill_file:
            logger.info(f"No skill implementation found in {directory}; registering metadata only")
            self.registry.register_metadata(
                metadata=metadata,
                module_path=None,
                file_path=directory,
                is_builtin=directory.is_relative_to(Path(__file__).parent),
            )
            return

        # Load the module
        module = self._load_module(skill_file, metadata.id)

        # Find the skill class
        skill_class = self._find_skill_class(module, metadata.id)
        if not skill_class:
            raise ValueError(f"No Skill subclass found in {skill_file}")

        # Create instance and register
        instance = skill_class()
        self.registry.register(
            instance,
            file_path=directory,
            is_builtin=directory.is_relative_to(Path(__file__).parent),
        )

        logger.info(f"Registered full skill: {metadata.id}")

    def _load_module(self, skill_file: Path, skill_id: str):
        """Dynamically load a skill module."""
        module_name = f"skills.dynamic.{skill_id.replace('/', '_')}"
        skills_root = Path(__file__).parent
        try:
            rel_path = skill_file.relative_to(skills_root)
            module_name = "skills." + str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
        except ValueError:
            pass

        spec = importlib.util.spec_from_file_location(module_name, skill_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {skill_file}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module

    def _find_skill_class(self, module, skill_id: str) -> Optional[type]:
        """Find the Skill subclass in a module."""
        direct = getattr(module, "Skill", None)
        if isinstance(direct, type) and issubclass(direct, Skill) and direct is not Skill:
            return direct
        for name in dir(module):
            obj = getattr(module, name)
            if (
                isinstance(obj, type)
                and issubclass(obj, Skill)
                and obj is not Skill
                and obj.__module__ == module.__name__
            ):
                return obj
        return None

    def load_from_file(self, skill_file: Path) -> Skill:
        """
        Load a skill directly from a file.

        Useful for development and testing.
        """
        module = self._load_module(skill_file, skill_file.stem)
        skill_class = self._find_skill_class(module, skill_file.stem)

        if not skill_class:
            raise ValueError(f"No Skill subclass found in {skill_file}")

        instance = skill_class()
        self.registry.register(instance, file_path=skill_file.parent)

        return instance

    def validate_skill_directory(self, directory: Path) -> Tuple[bool, List[str]]:
        """
        Validate that a directory contains a valid skill package.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for manifest
        manifest_path = self._find_manifest(directory)
        if not manifest_path:
            errors.append(f"No manifest file found (expected one of {MANIFEST_FILES})")
            return False, errors

        # Validate manifest
        try:
            manifest = self._parse_manifest(manifest_path)
        except Exception as e:
            errors.append(f"Invalid manifest: {e}")
            return False, errors

        # Required manifest fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in manifest:
                errors.append(f"Manifest missing required field: {field}")

        # Check for implementation
        skill_file = self._find_skill_file(directory)
        if not skill_file:
            errors.append(f"No skill implementation found (expected one of {SKILL_FILES})")

        return len(errors) == 0, errors

    def create_skill_template(
        self,
        directory: Path,
        skill_id: str,
        name: str,
        description: str,
        category: SkillCategory = SkillCategory.CODE,
    ) -> None:
        """
        Create a new skill template in the given directory.

        Generates the standard skill structure with placeholder content.
        """
        directory.mkdir(parents=True, exist_ok=True)

        # Create manifest
        manifest = {
            "id": skill_id,
            "name": name,
            "description": description,
            "version": "0.1.0",
            "category": category.value,
            "level": "intermediate",
            "tags": [],
            "dependencies": [],
            "requires_tools": [],
            "estimated_tokens": 500,
            "author": "Your Name",
            "examples": [
                {
                    "input": {"task": "example"},
                    "output": {"result": "example output"},
                }
            ],
        }

        manifest_path = directory / "manifest.yaml"
        manifest_path.write_text(yaml.dump(manifest, default_flow_style=False))

        # Create skill implementation
        skill_code = f'''"""
{name}
{"=" * len(name)}

{description}
"""

from typing import Any, Dict
from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillMetadata,
    SkillResult,
)


class {name.replace(" ", "")}Skill(Skill):
    """Implementation of {name}."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="{skill_id}",
            name="{name}",
            description="{description}",
            category=SkillCategory.{category.name},
        )

    def input_schema(self) -> Dict[str, Any]:
        return {{
            "type": "object",
            "properties": {{
                "task": {{"type": "string", "description": "The task to perform"}},
            }},
            "required": ["task"],
        }}

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        task = input_data.get("task", "")

        # TODO: Implement your skill logic here
        result = f"Processed: {{task}}"

        return SkillResult(
            success=True,
            output=result,
            skill_id=self.metadata().id,
        )
'''

        skill_path = directory / "skill.py"
        skill_path.write_text(skill_code)

        # Create prompts directory
        prompts_dir = directory / PROMPT_DIR
        prompts_dir.mkdir(exist_ok=True)

        system_prompt = f"""You are executing the "{name}" skill.

{description}

Follow these guidelines:
- Focus on the specific task requested
- Return structured, actionable output
- Handle edge cases gracefully
"""

        (prompts_dir / "system.md").write_text(system_prompt)

        # Create README
        readme = f"""# {name}

{description}

## Usage

```python
from skills import load_skill

skill = load_skill("{skill_id}")
result = skill.execute({{"task": "your task here"}}, context)
```

## Examples

See `manifest.yaml` for example inputs and outputs.

## Configuration

No special configuration required.
"""

        (directory / "README.md").write_text(readme)

        logger.info(f"Created skill template at {directory}")


def scan_builtin_skills(lazy: bool = True) -> int:
    """Scan and register all built-in skills."""
    loader = SkillLoader()
    return loader.scan_all(lazy=lazy)
