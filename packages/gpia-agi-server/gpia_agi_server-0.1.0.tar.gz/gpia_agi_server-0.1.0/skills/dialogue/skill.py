"""
Dialogue Skill Package Entry Point

Exports the ConversationHandlerSkill for the skills framework.
"""

from .conversation_handler import (
    ConversationHandlerSkill,
    IntentParser,
    EntityExtractor,
    ContextManager,
    ResponseGenerator,
    LearningModule,
    Intent,
    Entity,
    ConversationTurn,
    ConversationContext,
)

# Default export for skill loader
Skill = ConversationHandlerSkill

__all__ = [
    "ConversationHandlerSkill",
    "Skill",
    "IntentParser",
    "EntityExtractor",
    "ContextManager",
    "ResponseGenerator",
    "LearningModule",
    "Intent",
    "Entity",
    "ConversationTurn",
    "ConversationContext",
]
