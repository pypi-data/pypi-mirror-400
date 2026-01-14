"""
Conversation Handler Skill

The foundational skill for Alpha to interact with users in natural language.
This is the first step toward becoming an interactive AGI.

Components:
1. Intent Parser - Understands what the user wants
2. Context Manager - Maintains conversation state
3. Entity Extractor - Identifies key elements in user messages
4. Response Generator - Creates natural, contextual responses
5. Memory Integration - Learns from every interaction
6. Learning Module - Extracts insights for future improvement

Implements the Interaction Loop from AGI_CURRICULUM.md:
User speaks -> Intent Parser -> Context Manager -> User Modeler ->
Reasoning Engine -> Response Generator -> Self-Checker -> Alpha responds ->
Learning Module -> Memory Store
"""

import os
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

# Try to import skill base classes
try:
    from skills.base import Skill, SkillResult, SkillContext
except ImportError:
    # Standalone mode
    class SkillContext:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class SkillResult:
        def __init__(self, success: bool, output: Any = None, error: str = None):
            self.success = success
            self.output = output
            self.error = error

    class Skill:
        name = "base"
        description = "Base skill"
        version = "1.0.0"
        capabilities = []

# LLM Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


@dataclass
class Intent:
    """Represents parsed user intent."""
    primary: str  # Main intent category
    confidence: float  # 0.0 to 1.0
    sub_intents: List[str] = field(default_factory=list)
    modifiers: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Entity:
    """Extracted entity from user message."""
    text: str
    entity_type: str  # person, location, time, action, object, concept
    start: int
    end: int
    confidence: float = 0.8


@dataclass
class ConversationTurn:
    """Single turn in conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    intent: Optional[Intent] = None
    entities: List[Entity] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Full conversation context."""
    conversation_id: str
    turns: List[ConversationTurn] = field(default_factory=list)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    session_facts: List[str] = field(default_factory=list)
    emotional_state: str = "neutral"
    topic_stack: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class IntentParser:
    """Parses user messages to extract intent."""

    # Intent categories for AGI interaction
    INTENT_CATEGORIES = {
        "question": ["what", "how", "why", "when", "where", "who", "which", "can you explain"],
        "command": ["do", "make", "create", "run", "execute", "start", "stop", "show"],
        "request": ["please", "could you", "would you", "can you", "i want", "i need", "help me"],
        "statement": ["i think", "i believe", "in my opinion", "i feel"],
        "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
        "farewell": ["bye", "goodbye", "see you", "later", "exit", "quit"],
        "confirmation": ["yes", "yeah", "ok", "okay", "sure", "correct", "right"],
        "negation": ["no", "nope", "not", "don't", "cancel", "stop"],
        "clarification": ["what do you mean", "i don't understand", "can you clarify", "explain again"],
        "feedback": ["good", "bad", "great", "terrible", "thanks", "thank you"],
        "meta": ["what can you do", "who are you", "help", "capabilities", "about"],
    }

    def parse(self, message: str, context: ConversationContext = None) -> Intent:
        """Parse message to extract intent."""
        message_lower = message.lower().strip()

        # Score each intent category
        scores = {}
        for intent, keywords in self.INTENT_CATEGORIES.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[intent] = score

        # Determine primary intent
        if scores:
            primary = max(scores, key=scores.get)
            confidence = min(scores[primary] / 3.0, 1.0)  # Normalize
        else:
            primary = "statement"  # Default
            confidence = 0.5

        # Detect sub-intents
        sub_intents = [k for k, v in scores.items() if k != primary and v > 0]

        # Detect modifiers
        modifiers = {}
        if "?" in message:
            modifiers["is_question"] = True
        if "!" in message:
            modifiers["is_emphatic"] = True
        if any(word in message_lower for word in ["urgent", "asap", "now", "immediately"]):
            modifiers["is_urgent"] = True
        if any(word in message_lower for word in ["please", "kindly", "if possible"]):
            modifiers["is_polite"] = True

        return Intent(
            primary=primary,
            confidence=confidence,
            sub_intents=sub_intents,
            modifiers=modifiers
        )

    def parse_with_llm(self, message: str, model: str = "codegemma:latest") -> Intent:
        """Use LLM for more sophisticated intent parsing."""
        prompt = f"""Analyze this user message and extract the intent.

Message: "{message}"

Respond with JSON only:
{{
    "primary_intent": "question|command|request|statement|greeting|farewell|confirmation|negation|clarification|feedback|meta",
    "confidence": 0.0-1.0,
    "sub_intents": ["list", "of", "secondary", "intents"],
    "is_urgent": true/false,
    "emotional_tone": "neutral|positive|negative|curious|frustrated|excited"
}}"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 200}
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json().get("response", "")
                # Extract JSON from response
                try:
                    # Find JSON in response
                    start = result.find("{")
                    end = result.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(result[start:end])
                        return Intent(
                            primary=data.get("primary_intent", "statement"),
                            confidence=float(data.get("confidence", 0.7)),
                            sub_intents=data.get("sub_intents", []),
                            modifiers={
                                "is_urgent": data.get("is_urgent", False),
                                "emotional_tone": data.get("emotional_tone", "neutral")
                            }
                        )
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        # Fallback to rule-based
        return self.parse(message)


class EntityExtractor:
    """Extracts entities from user messages."""

    # Simple pattern-based extraction
    ENTITY_PATTERNS = {
        "time": ["today", "tomorrow", "yesterday", "now", "later", "morning", "afternoon", "evening", "night"],
        "action": ["run", "create", "delete", "update", "find", "search", "show", "list", "help"],
        "object": ["file", "code", "skill", "memory", "agent", "model", "system", "data"],
    }

    def extract(self, message: str) -> List[Entity]:
        """Extract entities from message."""
        entities = []
        message_lower = message.lower()

        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                idx = message_lower.find(pattern)
                if idx >= 0:
                    entities.append(Entity(
                        text=pattern,
                        entity_type=entity_type,
                        start=idx,
                        end=idx + len(pattern),
                        confidence=0.8
                    ))

        return entities

    def extract_with_llm(self, message: str, model: str = "codegemma:latest") -> List[Entity]:
        """Use LLM for entity extraction."""
        prompt = f"""Extract entities from this message.

Message: "{message}"

Identify: people, places, times, actions, objects, concepts.

Respond with JSON only:
{{
    "entities": [
        {{"text": "entity text", "type": "person|place|time|action|object|concept", "importance": 0.0-1.0}}
    ]
}}"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 300}
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json().get("response", "")
                try:
                    start = result.find("{")
                    end = result.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(result[start:end])
                        entities = []
                        for e in data.get("entities", []):
                            idx = message.lower().find(e["text"].lower())
                            entities.append(Entity(
                                text=e["text"],
                                entity_type=e.get("type", "concept"),
                                start=idx if idx >= 0 else 0,
                                end=idx + len(e["text"]) if idx >= 0 else len(e["text"]),
                                confidence=float(e.get("importance", 0.7))
                            ))
                        return entities
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        return self.extract(message)


class ContextManager:
    """Manages conversation context across turns."""

    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns
        self.contexts: Dict[str, ConversationContext] = {}

    def get_or_create_context(self, conversation_id: str = None) -> ConversationContext:
        """Get existing context or create new one."""
        if not conversation_id:
            conversation_id = hashlib.sha256(
                datetime.now().isoformat().encode()
            ).hexdigest()[:12]

        if conversation_id not in self.contexts:
            self.contexts[conversation_id] = ConversationContext(
                conversation_id=conversation_id
            )

        return self.contexts[conversation_id]

    def add_turn(self, context: ConversationContext, role: str, content: str,
                 intent: Intent = None, entities: List[Entity] = None) -> ConversationTurn:
        """Add a turn to the conversation."""
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            intent=intent,
            entities=entities or []
        )

        context.turns.append(turn)
        context.updated_at = datetime.now().isoformat()

        # Trim old turns if needed
        if len(context.turns) > self.max_turns:
            context.turns = context.turns[-self.max_turns:]

        return turn

    def get_recent_context(self, context: ConversationContext, n: int = 5) -> str:
        """Get recent conversation as formatted string."""
        recent = context.turns[-n:] if len(context.turns) > n else context.turns
        lines = []
        for turn in recent:
            role = "User" if turn.role == "user" else "Alpha"
            lines.append(f"{role}: {turn.content}")
        return "\n".join(lines)

    def extract_topic(self, context: ConversationContext) -> str:
        """Extract current topic from context."""
        if context.topic_stack:
            return context.topic_stack[-1]

        # Infer from recent turns
        if context.turns:
            last_user_turn = None
            for turn in reversed(context.turns):
                if turn.role == "user":
                    last_user_turn = turn
                    break

            if last_user_turn and last_user_turn.entities:
                # Use most important entity as topic
                return last_user_turn.entities[0].text

        return "general"

    def update_user_profile(self, context: ConversationContext, key: str, value: Any):
        """Update user profile in context."""
        context.user_profile[key] = value
        context.updated_at = datetime.now().isoformat()

    def add_session_fact(self, context: ConversationContext, fact: str):
        """Add a fact learned during this session."""
        if fact not in context.session_facts:
            context.session_facts.append(fact)


class ResponseGenerator:
    """Generates natural language responses."""

    def __init__(self, model: str = "qwen3:latest"):
        self.model = model
        self.personality = {
            "name": "Alpha",
            "traits": ["helpful", "curious", "thoughtful", "honest"],
            "style": "clear and friendly, concise but thorough when needed"
        }

    def generate(self, user_message: str, intent: Intent, context: ConversationContext,
                 use_llm: bool = True) -> str:
        """Generate response to user message."""

        if not use_llm:
            return self._generate_rule_based(user_message, intent)

        # Build prompt with context
        recent_context = ""
        if context.turns:
            context_mgr = ContextManager()
            recent_context = context_mgr.get_recent_context(context, n=3)

        system_prompt = f"""You are Alpha, an AI agent learning to become AGI.

Your personality: {', '.join(self.personality['traits'])}
Your style: {self.personality['style']}

Current topic: {context.topic_stack[-1] if context.topic_stack else 'general conversation'}
User's emotional state: {context.emotional_state}

Guidelines:
- Be genuinely helpful and engaged
- Show curiosity and ask follow-up questions when appropriate
- Admit when you don't know something
- Remember details from the conversation
- Be concise but complete"""

        prompt = f"""{system_prompt}

Recent conversation:
{recent_context}

User intent: {intent.primary} (confidence: {intent.confidence:.2f})
User message: {user_message}

Generate a natural, helpful response:"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 500}
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                # Clean up response
                if result.startswith('"') and result.endswith('"'):
                    result = result[1:-1]
                return result
        except Exception as e:
            print(f"LLM error: {e}")

        return self._generate_rule_based(user_message, intent)

    def _generate_rule_based(self, message: str, intent: Intent) -> str:
        """Fallback rule-based response generation."""
        responses = {
            "greeting": "Hello! I'm Alpha, your AI assistant. How can I help you today?",
            "farewell": "Goodbye! It was nice talking with you. Feel free to come back anytime.",
            "confirmation": "Understood. I'll proceed with that.",
            "negation": "Alright, I won't do that. What would you like instead?",
            "question": "That's an interesting question. Let me think about it...",
            "command": "I'll do my best to help with that.",
            "request": "Of course, I'd be happy to help.",
            "clarification": "Let me try to explain that more clearly...",
            "feedback": "Thank you for your feedback! I'm always learning.",
            "meta": "I'm Alpha, an AI agent learning to become AGI. I can help with conversations, answer questions, and learn from our interactions.",
            "statement": "I understand. Please tell me more.",
        }

        return responses.get(intent.primary, "I'm here to help. Could you tell me more?")


class LearningModule:
    """Extracts learnings from interactions for memory storage."""

    def __init__(self, model: str = "deepseek-r1:latest"):
        self.model = model

    def extract_learnings(self, context: ConversationContext) -> List[Dict[str, Any]]:
        """Extract learnings from conversation for memory storage."""
        learnings = []

        # Extract from session facts
        for fact in context.session_facts:
            learnings.append({
                "content": fact,
                "memory_type": "semantic",
                "importance": 0.7,
                "source": "conversation"
            })

        # Extract from user profile updates
        if context.user_profile:
            learnings.append({
                "content": f"User profile: {json.dumps(context.user_profile)}",
                "memory_type": "episodic",
                "importance": 0.6,
                "source": "user_modeling"
            })

        # Use LLM to extract deeper learnings
        if len(context.turns) >= 2:
            learnings.extend(self._extract_with_llm(context))

        return learnings

    def _extract_with_llm(self, context: ConversationContext) -> List[Dict[str, Any]]:
        """Use LLM to extract insights from conversation."""
        context_mgr = ContextManager()
        conversation_text = context_mgr.get_recent_context(context, n=10)

        prompt = f"""Analyze this conversation and extract key learnings for an AI agent.

Conversation:
{conversation_text}

Extract:
1. Facts learned (semantic memory)
2. User preferences discovered (episodic memory)
3. Communication patterns to remember (procedural memory)

Respond with JSON only:
{{
    "learnings": [
        {{"content": "what was learned", "type": "semantic|episodic|procedural", "importance": 0.0-1.0}}
    ]
}}"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.5, "num_predict": 500}
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json().get("response", "")
                try:
                    start = result.find("{")
                    end = result.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(result[start:end])
                        return [
                            {
                                "content": l["content"],
                                "memory_type": l.get("type", "semantic"),
                                "importance": float(l.get("importance", 0.6)),
                                "source": "llm_extraction"
                            }
                            for l in data.get("learnings", [])
                        ]
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

        return []


class ConversationHandlerSkill(Skill):
    """
    Main conversation handler skill for natural language interaction.

    This is the foundational skill that enables Alpha to:
    - Understand natural language messages
    - Maintain conversation context
    - Generate appropriate responses
    - Learn from every interaction
    """

    def __init__(self):
        self._metadata = None
        self.intent_parser = IntentParser()
        self.entity_extractor = EntityExtractor()
        self.context_manager = ContextManager()
        self.response_generator = ResponseGenerator()
        self.learning_module = LearningModule()
        self.memory = None  # Will be set if memory skill available

        # Try to connect to memory skill
        try:
            from skills.conscience.memory.skill import MemorySkill
            self.memory = MemorySkill()
        except ImportError:
            pass

    def metadata(self):
        """Return skill metadata for discovery and disclosure."""
        if self._metadata is None:
            try:
                from skills.base import SkillMetadata, SkillCategory, SkillLevel, SkillDependency
                self._metadata = SkillMetadata(
                    id="dialogue/conversation-handler",
                    name="Conversation Handler",
                    description="Natural language conversation handling for interactive AGI",
                    version="1.0.0",
                    category=SkillCategory.REASONING,
                    level=SkillLevel.BASIC,
                    tags=["nlu", "nlg", "conversation", "agi", "natural-language", "core"],
                    long_description="""
The foundational skill that enables Alpha to interact with users in natural language.
This is the first step toward becoming an interactive AGI.

Components:
1. Intent Parser - Understands what the user wants
2. Entity Extractor - Identifies key elements in messages
3. Context Manager - Maintains conversation state
4. Response Generator - Creates natural responses
5. Learning Module - Extracts insights for memory storage

Implements the Interaction Loop from AGI Curriculum:
User speaks -> Intent Parser -> Context Manager -> Response Generator ->
Self-Checker -> Alpha responds -> Learning Module -> Memory Store
""",
                    examples=[
                        {
                            "input": {"capability": "process_message", "message": "Hello! What can you do?"},
                            "output": {"response": "Hello! I'm Alpha...", "intent": {"primary": "greeting"}}
                        }
                    ],
                    dependencies=[
                        SkillDependency(
                            skill_id="conscience/memory",
                            optional=True,
                            reason="For storing learnings from conversations"
                        )
                    ],
                    requires_model="qwen3:latest",
                    estimated_tokens=800,
                    author="Professor + Alpha + Claude"
                )
            except ImportError:
                # Fallback for standalone mode
                self._metadata = type('SkillMetadata', (), {
                    'id': 'dialogue/conversation-handler',
                    'name': 'Conversation Handler',
                    'description': 'Natural language conversation handling for interactive AGI',
                    'version': '1.0.0'
                })()
        return self._metadata

    def execute(self, params: Dict[str, Any], context: SkillContext = None) -> SkillResult:
        """Execute conversation handler capability."""
        capability = params.get("capability", "process_message")

        if capability == "process_message":
            return self._process_message(params, context)
        elif capability == "get_context":
            return self._get_context(params)
        elif capability == "extract_learnings":
            return self._extract_learnings(params)
        elif capability == "set_personality":
            return self._set_personality(params)
        else:
            return SkillResult(
                success=False,
                error=f"Unknown capability: {capability}"
            )

    def _process_message(self, params: Dict[str, Any], context: SkillContext = None) -> SkillResult:
        """
        Process a user message through the full interaction loop.

        Interaction Loop:
        User speaks -> Intent Parser -> Context Manager -> Entity Extractor ->
        Response Generator -> Self-Checker -> Alpha responds -> Learning Module -> Memory Store
        """
        message = params.get("message", "")
        conversation_id = params.get("conversation_id")
        use_llm = params.get("use_llm", True)

        if not message:
            return SkillResult(
                success=False,
                error="No message provided"
            )

        # Step 1: Get or create conversation context
        conv_context = self.context_manager.get_or_create_context(conversation_id)

        # Step 2: Parse intent
        if use_llm:
            intent = self.intent_parser.parse_with_llm(message)
        else:
            intent = self.intent_parser.parse(message, conv_context)

        # Step 3: Extract entities
        if use_llm:
            entities = self.entity_extractor.extract_with_llm(message)
        else:
            entities = self.entity_extractor.extract(message)

        # Step 4: Update context with user turn
        self.context_manager.add_turn(
            conv_context, "user", message, intent, entities
        )

        # Step 5: Update topic stack
        if entities:
            main_entity = max(entities, key=lambda e: e.confidence)
            if main_entity.entity_type in ["object", "concept", "action"]:
                conv_context.topic_stack.append(main_entity.text)
                if len(conv_context.topic_stack) > 5:
                    conv_context.topic_stack = conv_context.topic_stack[-5:]

        # Step 6: Detect emotional state (simple heuristic)
        if intent.modifiers.get("emotional_tone"):
            conv_context.emotional_state = intent.modifiers["emotional_tone"]
        elif intent.primary in ["feedback", "farewell"]:
            conv_context.emotional_state = "positive"
        elif intent.primary in ["negation", "clarification"]:
            conv_context.emotional_state = "uncertain"

        # Step 7: Generate response
        response = self.response_generator.generate(
            message, intent, conv_context, use_llm=use_llm
        )

        # Step 8: Self-check response (basic quality check)
        if len(response) < 10:
            response = "I understand. Could you tell me more about what you need?"

        # Step 9: Add assistant turn to context
        self.context_manager.add_turn(conv_context, "assistant", response)

        # Step 10: Extract and store learnings
        learnings = self.learning_module.extract_learnings(conv_context)

        if self.memory and learnings:
            for learning in learnings[:3]:  # Limit to prevent memory overflow
                try:
                    self.memory.execute({
                        "capability": "experience",
                        "content": learning["content"],
                        "memory_type": learning["memory_type"],
                        "importance": learning["importance"],
                        "context": {"source": "conversation", "conversation_id": conv_context.conversation_id}
                    }, context)
                except Exception:
                    pass

        return SkillResult(
            success=True,
            output={
                "response": response,
                "conversation_id": conv_context.conversation_id,
                "intent": asdict(intent),
                "entities": [asdict(e) for e in entities],
                "learnings_extracted": len(learnings),
                "turn_count": len(conv_context.turns)
            }
        )

    def _get_context(self, params: Dict[str, Any]) -> SkillResult:
        """Get current conversation context."""
        conversation_id = params.get("conversation_id")

        if not conversation_id or conversation_id not in self.context_manager.contexts:
            return SkillResult(
                success=False,
                error="Conversation not found"
            )

        context = self.context_manager.contexts[conversation_id]

        return SkillResult(
            success=True,
            output={
                "conversation_id": context.conversation_id,
                "turn_count": len(context.turns),
                "topic_stack": context.topic_stack,
                "emotional_state": context.emotional_state,
                "user_profile": context.user_profile,
                "session_facts": context.session_facts,
                "created_at": context.created_at,
                "updated_at": context.updated_at
            }
        )

    def _extract_learnings(self, params: Dict[str, Any]) -> SkillResult:
        """Manually extract learnings from a conversation."""
        conversation_id = params.get("conversation_id")

        if not conversation_id or conversation_id not in self.context_manager.contexts:
            return SkillResult(
                success=False,
                error="Conversation not found"
            )

        context = self.context_manager.contexts[conversation_id]
        learnings = self.learning_module.extract_learnings(context)

        return SkillResult(
            success=True,
            output={
                "learnings": learnings,
                "count": len(learnings)
            }
        )

    def _set_personality(self, params: Dict[str, Any]) -> SkillResult:
        """Update Alpha's personality traits."""
        name = params.get("name")
        traits = params.get("traits")
        style = params.get("style")

        if name:
            self.response_generator.personality["name"] = name
        if traits:
            self.response_generator.personality["traits"] = traits
        if style:
            self.response_generator.personality["style"] = style

        return SkillResult(
            success=True,
            output={"personality": self.response_generator.personality}
        )


def test_conversation_handler():
    """Test the conversation handler skill."""
    print("Testing Conversation Handler Skill")
    print("=" * 50)

    skill = ConversationHandlerSkill()

    # Test messages
    test_messages = [
        "Hello! I'm interested in learning about AI.",
        "What can you do?",
        "Can you help me understand how memory works?",
        "That's interesting. Tell me more about semantic memory.",
        "Thanks for explaining! Goodbye."
    ]

    conversation_id = None

    for message in test_messages:
        print(f"\nUser: {message}")

        result = skill.execute({
            "capability": "process_message",
            "message": message,
            "conversation_id": conversation_id,
            "use_llm": True  # Set to False for faster testing without LLM
        })

        if result.success:
            output = result.output
            conversation_id = output["conversation_id"]
            print(f"Alpha: {output['response']}")
            print(f"  Intent: {output['intent']['primary']} ({output['intent']['confidence']:.2f})")
            print(f"  Entities: {len(output['entities'])}")
            print(f"  Turn: {output['turn_count']}")
        else:
            print(f"Error: {result.error}")

    # Get final context
    context_result = skill.execute({
        "capability": "get_context",
        "conversation_id": conversation_id
    })

    if context_result.success:
        print(f"\n{'=' * 50}")
        print("Final Conversation Context:")
        print(f"  Topics discussed: {context_result.output['topic_stack']}")
        print(f"  Session facts: {context_result.output['session_facts']}")
        print(f"  Total turns: {context_result.output['turn_count']}")


if __name__ == "__main__":
    test_conversation_handler()
