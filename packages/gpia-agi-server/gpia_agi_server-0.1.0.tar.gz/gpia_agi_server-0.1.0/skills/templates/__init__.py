"""
Skill Templates
===============

Templates for creating new skills.

Available templates:
- skill_template.py: Python skill implementation template
- manifest_template.yaml: YAML manifest template
"""

from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent


def get_skill_template() -> str:
    """Get the Python skill template content."""
    return (TEMPLATE_DIR / "skill_template.py").read_text()


def get_manifest_template() -> str:
    """Get the YAML manifest template content."""
    return (TEMPLATE_DIR / "manifest_template.yaml").read_text()
