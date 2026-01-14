"""
Writing Skills
==============

Skills for content creation, editing, and documentation.

Available skills:
- writing/draft: Content drafting and generation
- writing/edit: Content editing and refinement
- writing/docs: Technical documentation generation
"""

from skills.writing.draft.skill import DraftSkill
from skills.writing.edit.skill import EditSkill

__all__ = [
    "DraftSkill",
    "EditSkill",
]
