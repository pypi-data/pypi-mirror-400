"""
Minimal Reference Skill Package
===============================

This __init__.py demonstrates progressive disclosure:
- Importing this package does NOT load skill.py
- Only manifest metadata is exposed at import time
- Full skill class is loaded lazily on first access
"""

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

# Layer 0: Load manifest at import (always happens)
_SKILL_DIR = Path(__file__).parent
_MANIFEST_PATH = _SKILL_DIR / "manifest.yaml"

with open(_MANIFEST_PATH) as f:
    MANIFEST = yaml.safe_load(f)

# Export manifest data without loading skill.py
SKILL_ID = MANIFEST["id"]
SKILL_VERSION = MANIFEST["version"]
SKILL_NAME = MANIFEST["name"]
SKILL_DESCRIPTION = MANIFEST["description"]
SKILL_CATEGORY = MANIFEST["category"]
SKILL_TAGS = MANIFEST.get("tags", [])

# Lazy loading mechanism
_skill_class = None


def get_skill_class():
    """
    Lazy loader for skill class (Layer 1).

    The actual skill.py is only imported when this function is called.
    This enables progressive disclosure - agents can discover skills
    via manifest without loading implementation code.
    """
    global _skill_class
    if _skill_class is None:
        from skills._reference.minimal.skill import MinimalSkill
        _skill_class = MinimalSkill
    return _skill_class


# Type hint support without runtime import
if TYPE_CHECKING:
    from skills._reference.minimal.skill import MinimalSkill

__all__ = [
    "MANIFEST",
    "SKILL_ID",
    "SKILL_VERSION",
    "SKILL_NAME",
    "SKILL_DESCRIPTION",
    "SKILL_CATEGORY",
    "SKILL_TAGS",
    "get_skill_class",
]
