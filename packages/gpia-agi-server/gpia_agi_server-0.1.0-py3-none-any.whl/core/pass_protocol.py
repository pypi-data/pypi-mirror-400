"""
PASS Protocol - Cooperative Agent Dependency Resolution
========================================================

Implements deterministic "PASS" state for recursive dependency resolution.

Flow:
    Agent A (Stuck) -> PASS -> Orchestrator -> Agent B/C/D (Assist) -> Agent A (Resume)

Key Features:
1. Explicit Capsule Object: Context encapsulated, grows as assists arrive
2. Strict JSON Protocol: No prose "I don't know" - structured PASS instead
3. Persistence: Every step saved, recovery from any point
4. Recursive Resolution: Handles nested PASS chains with depth limits

Protocol States:
    ACTIVE    -> Agent working on task
    PASSED    -> Agent blocked, waiting for assist
    ASSISTED  -> Agent received help, ready to resume
    RESUMED   -> Agent continuing with enriched context
    COMPLETED -> Task finished successfully
    FAILED    -> Task failed after max attempts

Example PASS Output:
{
    "status": "pass",
    "needs": [
        {"type": "knowledge", "id": "react.hooks", "description": "..."},
        {"type": "capability", "id": "http.client", "description": "..."}
    ],
    "partial_work": "Analyzed X, computed Y, but need Z to continue",
    "resume_hint": "After receiving hook info, implement component"
}
"""

import json
import hashlib
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

class CapsuleState(str, Enum):
    """State of a task capsule."""
    ACTIVE = "active"
    PASSED = "passed"
    ASSISTED = "assisted"
    RESUMED = "resumed"
    COMPLETED = "completed"
    FAILED = "failed"


class NeedType(str, Enum):
    """Types of needs an agent can express."""
    KNOWLEDGE = "knowledge"      # Missing information/facts
    CAPABILITY = "capability"    # Missing skill/tool
    FILE = "file"                # Need to read/access a file
    FILE_WRITE_ACCESS = "file-write-access"  # Need permission to write files
    PERMISSION = "permission"    # Need authorization
    RESOURCE = "resource"        # Need compute/memory/etc
    DEPENDENCY = "dependency"    # Need another agent's output


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Need:
    """A specific need that blocks task completion."""
    type: NeedType
    id: str                          # Unique identifier (e.g., "react.hooks", "/src/config.json")
    description: str                 # Human-readable explanation
    priority: int = 1                # 1=critical, 2=important, 3=nice-to-have
    resolver_hint: Optional[str] = None  # Hint for which agent can resolve this

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value if isinstance(self.type, Enum) else self.type,
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "resolver_hint": self.resolver_hint
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Need":
        return cls(
            type=NeedType(data["type"]),
            id=data["id"],
            description=data["description"],
            priority=data.get("priority", 1),
            resolver_hint=data.get("resolver_hint")
        )


@dataclass
class AssistRecord:
    """Record of an assist provided to resolve a need."""
    assist_id: str
    need_id: str                     # Which need this resolves
    provider_agent: str              # Which agent provided the assist
    content: Any                     # The actual assistance
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True

    def to_dict(self) -> Dict:
        return {
            "assist_id": self.assist_id,
            "need_id": self.need_id,
            "provider_agent": self.provider_agent,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AssistRecord":
        return cls(
            assist_id=data["assist_id"],
            need_id=data["need_id"],
            provider_agent=data["provider_agent"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            success=data.get("success", True)
        )


@dataclass
class PassRecord:
    """Record of a PASS event."""
    pass_id: str
    needs: List[Need]
    partial_work: str                # Work completed before blocking
    resume_hint: str                 # How to continue after assists
    timestamp: datetime = field(default_factory=datetime.now)
    depth: int = 0                   # Recursion depth (for nested PASS)

    def to_dict(self) -> Dict:
        return {
            "pass_id": self.pass_id,
            "needs": [n.to_dict() for n in self.needs],
            "partial_work": self.partial_work,
            "resume_hint": self.resume_hint,
            "timestamp": self.timestamp.isoformat(),
            "depth": self.depth
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PassRecord":
        return cls(
            pass_id=data["pass_id"],
            needs=[Need.from_dict(n) for n in data["needs"]],
            partial_work=data["partial_work"],
            resume_hint=data["resume_hint"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            depth=data.get("depth", 0)
        )


@dataclass
class Capsule:
    """
    Task Capsule - Encapsulates all context for a task.

    This is the core data structure that travels through the PASS protocol.
    It accumulates context as assists come in and maintains full history.
    """
    capsule_id: str
    task: str                        # Original task description
    agent_id: str                    # Agent currently working on this
    state: CapsuleState = CapsuleState.ACTIVE
    context: Dict[str, Any] = field(default_factory=dict)
    assists: List[AssistRecord] = field(default_factory=list)
    passes: List[PassRecord] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    parent_capsule_id: Optional[str] = None  # For recursive chains
    attempt_count: int = 0
    max_attempts: int = 3
    max_depth: int = 5               # Max recursion depth

    def __post_init__(self):
        if not self.capsule_id:
            self.capsule_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique capsule ID."""
        content = f"{self.task}{datetime.now().isoformat()}"
        return f"cap_{hashlib.sha256(content.encode()).hexdigest()[:12]}"

    @property
    def current_depth(self) -> int:
        """Current recursion depth."""
        return len(self.passes)

    @property
    def is_blocked(self) -> bool:
        """Is the capsule currently blocked waiting for assists?"""
        return self.state == CapsuleState.PASSED

    @property
    def pending_needs(self) -> List[Need]:
        """Needs that haven't been resolved yet."""
        if not self.passes:
            return []
        last_pass = self.passes[-1]
        resolved_ids = {a.need_id for a in self.assists}
        return [n for n in last_pass.needs if n.id not in resolved_ids]

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "capsule_id": self.capsule_id,
            "task": self.task,
            "agent_id": self.agent_id,
            "state": self.state.value,
            "context": self.context,
            "assists": [a.to_dict() for a in self.assists],
            "passes": [p.to_dict() for p in self.passes],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "parent_capsule_id": self.parent_capsule_id,
            "attempt_count": self.attempt_count,
            "max_attempts": self.max_attempts,
            "max_depth": self.max_depth
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Capsule":
        """Deserialize from dictionary."""
        return cls(
            capsule_id=data["capsule_id"],
            task=data["task"],
            agent_id=data["agent_id"],
            state=CapsuleState(data["state"]),
            context=data.get("context", {}),
            assists=[AssistRecord.from_dict(a) for a in data.get("assists", [])],
            passes=[PassRecord.from_dict(p) for p in data.get("passes", [])],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data.get("updated_at", data["created_at"])),
            parent_capsule_id=data.get("parent_capsule_id"),
            attempt_count=data.get("attempt_count", 0),
            max_attempts=data.get("max_attempts", 3),
            max_depth=data.get("max_depth", 5)
        )


# =============================================================================
# PROTOCOL MESSAGES
# =============================================================================

@dataclass
class SuccessResponse:
    """Agent successfully completed task."""
    status: str = "success"
    output: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "status": self.status,
            "output": self.output,
            "metadata": self.metadata
        }, default=str)


@dataclass
class PassResponse:
    """Agent is blocked and needs assistance."""
    status: str = "pass"
    needs: List[Need] = field(default_factory=list)
    partial_work: str = ""
    resume_hint: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "status": self.status,
            "needs": [n.to_dict() for n in self.needs],
            "partial_work": self.partial_work,
            "resume_hint": self.resume_hint
        }, default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "PassResponse":
        data = json.loads(json_str)
        return cls(
            status=data["status"],
            needs=[Need.from_dict(n) for n in data.get("needs", [])],
            partial_work=data.get("partial_work", ""),
            resume_hint=data.get("resume_hint", "")
        )


@dataclass
class AssistResponse:
    """Response providing assistance to a blocked agent."""
    status: str = "assist"
    need_id: str = ""
    content: Any = None
    success: bool = True
    notes: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "status": self.status,
            "need_id": self.need_id,
            "content": self.content,
            "success": self.success,
            "notes": self.notes
        }, default=str)


# =============================================================================
# PROTOCOL PARSER
# =============================================================================

class ProtocolParser:
    """
    Parse agent outputs into protocol messages.

    Handles:
    - Strict JSON parsing
    - Fallback extraction from prose
    - Validation of protocol messages
    """

    @staticmethod
    def parse(output: str) -> Union[SuccessResponse, PassResponse, None]:
        """
        Parse agent output into a protocol message.

        Args:
            output: Raw agent output (should be JSON)

        Returns:
            SuccessResponse, PassResponse, or None if invalid
        """
        # Try direct JSON parse
        try:
            data = json.loads(output.strip())
            return ProtocolParser._parse_dict(data)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from prose
        json_str = ProtocolParser._extract_json(output)
        if json_str:
            try:
                data = json.loads(json_str)
                return ProtocolParser._parse_dict(data)
            except json.JSONDecodeError:
                pass

        # Check for "I don't know" patterns and convert to PASS
        if ProtocolParser._is_blocked_prose(output):
            return ProtocolParser._prose_to_pass(output)

        # Assume success with raw output
        return SuccessResponse(output=output)

    @staticmethod
    def _parse_dict(data: Dict) -> Union[SuccessResponse, PassResponse, None]:
        """Parse a dictionary into a protocol message."""
        status = data.get("status", "").lower()

        if status == "success":
            return SuccessResponse(
                output=data.get("output"),
                metadata=data.get("metadata", {})
            )
        elif status == "pass":
            needs = [Need.from_dict(n) for n in data.get("needs", [])]
            return PassResponse(
                needs=needs,
                partial_work=data.get("partial_work", ""),
                resume_hint=data.get("resume_hint", "")
            )
        else:
            # Unknown status, treat as success
            return SuccessResponse(output=data)

    @staticmethod
    def _extract_json(text: str) -> Optional[str]:
        """Extract JSON from text that might contain prose."""
        # Find JSON object
        start = text.find("{")
        if start == -1:
            return None

        # Find matching closing brace
        depth = 0
        for i, char in enumerate(text[start:], start):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i+1]

        return None

    @staticmethod
    def _is_blocked_prose(text: str) -> bool:
        """Detect if text indicates agent is blocked."""
        blocked_patterns = [
            "i don't know",
            "i cannot",
            "i can't",
            "i'm not sure",
            "i need more information",
            "i need to know",
            "i would need",
            "unable to",
            "missing information",
            "don't have access",
            "cannot determine",
            "insufficient",
        ]
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in blocked_patterns)

    @staticmethod
    def _prose_to_pass(text: str) -> PassResponse:
        """Convert blocked prose to a PASS response."""
        # Extract what they need from the text
        needs = []

        # Pattern matching for common needs
        if "file" in text.lower() or "read" in text.lower():
            needs.append(Need(
                type=NeedType.FILE,
                id="unknown_file",
                description="Agent needs to access a file"
            ))

        if "api" in text.lower() or "http" in text.lower():
            needs.append(Need(
                type=NeedType.CAPABILITY,
                id="http.client",
                description="Agent needs HTTP/API capability"
            ))

        if "information" in text.lower() or "know" in text.lower():
            needs.append(Need(
                type=NeedType.KNOWLEDGE,
                id="missing_knowledge",
                description="Agent needs additional information"
            ))

        if not needs:
            needs.append(Need(
                type=NeedType.KNOWLEDGE,
                id="unspecified",
                description=text[:200]
            ))

        return PassResponse(
            needs=needs,
            partial_work="Agent indicated inability to proceed",
            resume_hint="Provide the missing information and retry"
        )


# =============================================================================
# CAPSULE STORE (Persistence)
# =============================================================================

class CapsuleStore:
    """
    Persistent storage for capsules.

    Features:
    - Save/load capsules to disk
    - Track capsule history
    - Recovery from any state
    """

    def __init__(self, store_path: str = "data/capsules"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self._index: Dict[str, str] = {}  # capsule_id -> file_path
        self._load_index()

    def _load_index(self):
        """Load capsule index from disk."""
        index_path = self.store_path / "index.json"
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                self._index = json.load(f)

    def _save_index(self):
        """Save capsule index to disk."""
        index_path = self.store_path / "index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(self._index, f, indent=2)

    def save(self, capsule: Capsule) -> str:
        """Save a capsule to disk."""
        capsule.updated_at = datetime.now()
        file_name = f"{capsule.capsule_id}.json"
        file_path = self.store_path / file_name

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(capsule.to_dict(), f, indent=2, default=str)

        self._index[capsule.capsule_id] = str(file_path)
        self._save_index()

        logger.debug(f"Saved capsule {capsule.capsule_id} to {file_path}")
        return str(file_path)

    def load(self, capsule_id: str) -> Optional[Capsule]:
        """Load a capsule from disk."""
        if capsule_id not in self._index:
            return None

        file_path = Path(self._index[capsule_id])
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Capsule.from_dict(data)

    def list_active(self) -> List[str]:
        """List all active (non-completed) capsule IDs."""
        active = []
        for capsule_id in self._index:
            capsule = self.load(capsule_id)
            if capsule and capsule.state not in [CapsuleState.COMPLETED, CapsuleState.FAILED]:
                active.append(capsule_id)
        return active

    def list_passed(self) -> List[str]:
        """List all capsules waiting for assists."""
        passed = []
        for capsule_id in self._index:
            capsule = self.load(capsule_id)
            if capsule and capsule.state == CapsuleState.PASSED:
                passed.append(capsule_id)
        return passed


# =============================================================================
# PASS ORCHESTRATOR
# =============================================================================

class PassOrchestrator:
    """
    Orchestrates the PASS protocol flow.

    Responsibilities:
    - Create capsules for new tasks
    - Handle PASS events and spawn assist agents
    - Deliver assists and trigger resumes
    - Detect and prevent infinite loops
    """

    def __init__(self, store: Optional[CapsuleStore] = None):
        self.store = store or CapsuleStore()
        self.agent_registry: Dict[str, Any] = {}  # agent_id -> agent instance
        self.resolver_map: Dict[NeedType, str] = {
            # Map need types to resolver agents
            NeedType.KNOWLEDGE: "research_agent",
            NeedType.CAPABILITY: "skill_installer",
            NeedType.FILE: "file_reader",
            NeedType.PERMISSION: "auth_agent",
            NeedType.RESOURCE: "resource_manager",
            NeedType.DEPENDENCY: "dependency_resolver",
        }

    def register_agent(self, agent_id: str, agent: Any):
        """Register an agent that can provide assists."""
        self.agent_registry[agent_id] = agent

    def create_capsule(self, task: str, agent_id: str, context: Dict = None) -> Capsule:
        """Create a new task capsule."""
        capsule = Capsule(
            capsule_id="",  # Will be generated
            task=task,
            agent_id=agent_id,
            context=context or {}
        )
        self.store.save(capsule)
        logger.info(f"Created capsule {capsule.capsule_id} for task: {task[:50]}...")
        return capsule

    def handle_pass(self, capsule: Capsule, pass_response: PassResponse) -> Capsule:
        """
        Handle a PASS event from an agent.

        1. Update capsule state
        2. Record the PASS
        3. Check for loops/depth limits
        4. Queue assist requests
        """
        # Check depth limit
        if capsule.current_depth >= capsule.max_depth:
            logger.error(f"Max depth reached for capsule {capsule.capsule_id}")
            capsule.state = CapsuleState.FAILED
            self.store.save(capsule)
            return capsule

        # Check attempt limit
        capsule.attempt_count += 1
        if capsule.attempt_count > capsule.max_attempts:
            logger.error(f"Max attempts reached for capsule {capsule.capsule_id}")
            capsule.state = CapsuleState.FAILED
            self.store.save(capsule)
            return capsule

        # Record the PASS
        pass_record = PassRecord(
            pass_id=f"pass_{uuid.uuid4().hex[:8]}",
            needs=pass_response.needs,
            partial_work=pass_response.partial_work,
            resume_hint=pass_response.resume_hint,
            depth=capsule.current_depth
        )
        capsule.passes.append(pass_record)
        capsule.state = CapsuleState.PASSED
        self.store.save(capsule)

        logger.info(f"Capsule {capsule.capsule_id} PASSED with {len(pass_response.needs)} needs")

        return capsule

    def provide_assist(self, capsule: Capsule, assist: AssistResponse, provider: str) -> Capsule:
        """
        Provide an assist to a blocked capsule.

        1. Record the assist
        2. Update context with assist content
        3. Check if all needs resolved
        4. If yes, mark as ASSISTED (ready to resume)
        """
        assist_record = AssistRecord(
            assist_id=f"assist_{uuid.uuid4().hex[:8]}",
            need_id=assist.need_id,
            provider_agent=provider,
            content=assist.content,
            success=assist.success
        )
        capsule.assists.append(assist_record)

        # Update context with assist content
        capsule.context[f"assist_{assist.need_id}"] = assist.content

        # Check if all needs resolved
        if not capsule.pending_needs:
            capsule.state = CapsuleState.ASSISTED
            logger.info(f"Capsule {capsule.capsule_id} fully assisted, ready to resume")
        else:
            logger.info(f"Capsule {capsule.capsule_id} has {len(capsule.pending_needs)} pending needs")

        self.store.save(capsule)
        return capsule

    def resume(self, capsule: Capsule) -> Capsule:
        """Mark capsule as resumed, ready for agent to continue."""
        if capsule.state != CapsuleState.ASSISTED:
            logger.warning(f"Cannot resume capsule {capsule.capsule_id} in state {capsule.state}")
            return capsule

        capsule.state = CapsuleState.RESUMED
        self.store.save(capsule)
        logger.info(f"Capsule {capsule.capsule_id} resumed")
        return capsule

    def complete(self, capsule: Capsule, output: Any) -> Capsule:
        """Mark capsule as completed successfully."""
        capsule.state = CapsuleState.COMPLETED
        capsule.context["final_output"] = output
        self.store.save(capsule)
        logger.info(f"Capsule {capsule.capsule_id} completed")
        return capsule

    def get_resolver_for_need(self, need: Need) -> Optional[str]:
        """Get the appropriate resolver agent for a need."""
        # Check explicit hint first
        if need.resolver_hint:
            return need.resolver_hint

        # Use default mapping
        return self.resolver_map.get(need.type)

    def build_assist_context(self, capsule: Capsule) -> str:
        """Build context string from all assists for agent prompt."""
        if not capsule.assists:
            return ""

        context_parts = ["\n## ASSISTS RECEIVED ##"]
        for assist in capsule.assists:
            context_parts.append(f"\n### {assist.need_id} (from {assist.provider_agent}):")
            context_parts.append(str(assist.content)[:1000])

        return "\n".join(context_parts)


# =============================================================================
# SYSTEM PROMPT BUILDER
# =============================================================================

def build_protocol_prompt(capsule: Capsule, orchestrator: PassOrchestrator) -> str:
    """
    Build the system prompt for an agent with PASS protocol rules.

    This prompt instructs the agent on how to use the protocol.
    """
    assist_context = orchestrator.build_assist_context(capsule)

    return f"""PROTOCOL RULES:
1. If you can solve the task, output valid JSON with {{"status": "success", "output": "..."}}.
2. If you are BLOCKED by missing knowledge, capabilities, or files, you MUST output a PASS object.
3. NEVER say "I don't know" in prose - use structured PASS instead.
4. Output ONLY valid JSON.

PASS FORMAT (when blocked):
{{
  "status": "pass",
  "needs": [
    {{"type": "knowledge|capability|file|permission|resource|dependency", "id": "unique_id", "description": "What you need"}}
  ],
  "partial_work": "What you accomplished before blocking",
  "resume_hint": "How to continue after receiving assist"
}}

SUCCESS FORMAT (when complete):
{{
  "status": "success",
  "output": "Your complete response/result"
}}

TASK: {capsule.task}

CONTEXT: {json.dumps(capsule.context, default=str)[:2000]}
{assist_context}

Execute the task. Output ONLY valid JSON."""


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Demo the protocol
    logging.basicConfig(level=logging.INFO)

    # Create store and orchestrator
    store = CapsuleStore("data/capsules_demo")
    orch = PassOrchestrator(store)

    # Create a capsule
    capsule = orch.create_capsule(
        task="Analyze the React hooks implementation in /src/hooks/",
        agent_id="gpia",
        context={"project": "web-app"}
    )
    print(f"Created capsule: {capsule.capsule_id}")

    # Simulate a PASS (agent is blocked)
    pass_resp = PassResponse(
        needs=[
            Need(NeedType.FILE, "/src/hooks/useAuth.js", "Need to read auth hook"),
            Need(NeedType.KNOWLEDGE, "react.hooks.lifecycle", "Need React hooks lifecycle info")
        ],
        partial_work="Identified hooks directory structure",
        resume_hint="After reading files and learning lifecycle, analyze patterns"
    )
    capsule = orch.handle_pass(capsule, pass_resp)
    print(f"Capsule state: {capsule.state}")

    # Simulate assists
    assist1 = AssistResponse(
        need_id="/src/hooks/useAuth.js",
        content="export function useAuth() { ... }",
        success=True
    )
    capsule = orch.provide_assist(capsule, assist1, "file_reader")

    assist2 = AssistResponse(
        need_id="react.hooks.lifecycle",
        content="React hooks lifecycle: mount -> update -> unmount...",
        success=True
    )
    capsule = orch.provide_assist(capsule, assist2, "research_agent")

    print(f"Capsule state after assists: {capsule.state}")
    print(f"Pending needs: {capsule.pending_needs}")

    # Resume
    capsule = orch.resume(capsule)
    print(f"Capsule state after resume: {capsule.state}")

    # Complete
    capsule = orch.complete(capsule, "Analysis complete: Found 5 custom hooks...")
    print(f"Final state: {capsule.state}")

    # Show the full audit trail
    print("\n=== AUDIT TRAIL ===")
    print(json.dumps(capsule.to_dict(), indent=2, default=str))
