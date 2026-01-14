"""
Budget Allocator Agent - Superintelligent Enforcement via ML-based Priority Judge

Makes value-based resource allocation decisions using adaptive learning.
Learns from outcomes to improve decision quality over time.

Decision Factors:
- Agent type (Professor/Alpha/GPIA/custom)
- Task urgency (immediate/normal/background)
- Task complexity (tokens, model size)
- Historical success rate
- Current system load
- Fairness (recent allocation history)
- Resource efficiency
"""

import os
import time
import json
import sqlite3
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class TaskUrgency(Enum):
    """Task urgency levels."""
    IMMEDIATE = 3  # System-critical, user-facing
    NORMAL = 2     # Standard operations
    BACKGROUND = 1 # Low-priority maintenance


class AgentTier(Enum):
    """Agent importance levels."""
    SYSTEM = 3     # GPIA core operations
    PRIMARY = 2    # Professor, Alpha
    SECONDARY = 1  # Custom agents


@dataclass
class AllocationRequest:
    """Represents a resource allocation request."""
    task_id: str
    agent: str
    model: str
    prompt: str
    requested_tokens: int
    urgency: TaskUrgency
    complexity_score: float  # 0.0-1.0
    timestamp: float


@dataclass
class DecisionFactors:
    """Features used for priority ranking."""
    urgency_score: float  # 0.0-1.0
    agent_tier_score: float  # 0.0-1.0
    complexity_score: float  # 0.0-1.0
    historical_success_rate: float  # 0.0-1.0
    current_load_factor: float  # 0.0-1.0 (lower = less load)
    fairness_score: float  # 0.0-1.0 (higher = agent hasn't used much recently)
    resource_efficiency: float  # 0.0-1.0 (tokens per second)


@dataclass
class DecisionWeights:
    """Learned weights for priority calculation."""
    urgency: float = 0.30
    agent_tier: float = 0.15
    complexity: float = 0.15
    success_rate: float = 0.15
    load_factor: float = 0.10
    fairness: float = 0.10
    efficiency: float = 0.05


class BudgetAllocatorAgent:
    """
    Autonomous agent that makes value-based resource allocation decisions.

    Learning Mechanism:
    - Tracks (request_features, decision, outcome) tuples
    - Outcome metrics: task_success, resource_efficiency, completion_time
    - Updates decision weights via gradient descent on outcome quality
    """

    def __init__(self, db_path: str = "/app/memories/budget_allocator.db"):
        """Initialize the allocator agent."""
        self.db_path = db_path
        self._init_decision_db()
        self.weights = self._load_weights()
        self._recent_allocations: Dict[str, List[float]] = {}
        self._running = True

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

    def _shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        self._running = False
        self._save_weights()

    def _init_decision_db(self) -> None:
        """Initialize decision tracking database."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                agent TEXT,
                model TEXT,
                tokens INTEGER,
                urgency INTEGER,
                approved INTEGER,
                priority_score REAL,

                -- Decision factors (features)
                urgency_score REAL,
                agent_tier_score REAL,
                complexity_score REAL,
                success_rate REAL,
                load_factor REAL,
                fairness_score REAL,
                efficiency_score REAL,

                -- Outcome metrics (for learning)
                task_success INTEGER,
                completion_time REAL,
                actual_tokens_used INTEGER,
                resource_efficiency REAL
            );

            CREATE INDEX IF NOT EXISTS idx_timestamp ON decisions(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_agent ON decisions(agent);
            CREATE INDEX IF NOT EXISTS idx_approved ON decisions(approved);
        """)
        conn.commit()
        conn.close()

    def _load_weights(self) -> DecisionWeights:
        """Load learned weights from disk."""
        weights_file = Path("/app/memories/priority_weights.json")
        if weights_file.exists():
            try:
                data = json.loads(weights_file.read_text())
                return DecisionWeights(**data)
            except:
                pass
        return DecisionWeights()

    def _save_weights(self) -> None:
        """Save learned weights to disk."""
        weights_file = Path("/app/memories/priority_weights.json")
        weights_file.parent.mkdir(parents=True, exist_ok=True)
        weights_file.write_text(json.dumps(asdict(self.weights), indent=2))

    def compute_factors(self, request: AllocationRequest) -> DecisionFactors:
        """Compute decision factors for a request."""
        # Urgency score (normalized to 0-1)
        urgency_score = request.urgency.value / 3.0

        # Agent tier score
        agent_tier_map = {
            "gpia": AgentTier.SYSTEM.value,
            "professor": AgentTier.PRIMARY.value,
            "alpha": AgentTier.PRIMARY.value,
        }
        agent_tier = agent_tier_map.get(request.agent.lower(), AgentTier.SECONDARY.value)
        agent_tier_score = agent_tier / 3.0

        # Complexity score (from request)
        complexity_score = request.complexity_score

        # Historical success rate
        success_rate = self._get_agent_success_rate(request.agent)

        # Current load factor (from budget service if available)
        load_factor = self._get_current_load_factor()

        # Fairness score (inverse of recent usage)
        fairness_score = self._compute_fairness_score(request.agent)

        # Resource efficiency (tokens per second from history)
        efficiency = self._get_agent_efficiency(request.agent, request.model)

        return DecisionFactors(
            urgency_score=urgency_score,
            agent_tier_score=agent_tier_score,
            complexity_score=complexity_score,
            historical_success_rate=success_rate,
            current_load_factor=load_factor,
            fairness_score=fairness_score,
            resource_efficiency=efficiency
        )

    def compute_priority_score(self, factors: DecisionFactors) -> float:
        """Compute priority score using learned weights."""
        score = (
            factors.urgency_score * self.weights.urgency +
            factors.agent_tier_score * self.weights.agent_tier +
            factors.complexity_score * self.weights.complexity +
            factors.historical_success_rate * self.weights.success_rate +
            factors.current_load_factor * self.weights.load_factor +
            factors.fairness_score * self.weights.fairness +
            factors.resource_efficiency * self.weights.efficiency
        )
        return max(0.0, min(1.0, score))

    def evaluate_request(self, request: AllocationRequest) -> Tuple[bool, float, str]:
        """
        Evaluate an allocation request.

        Returns (approved, priority_score, reason).
        """
        factors = self.compute_factors(request)
        priority_score = self.compute_priority_score(factors)

        # Dynamic threshold based on current load
        load = factors.current_load_factor
        if load > 0.5:  # Low load
            threshold = 0.3
        elif load > 0.3:  # Medium load
            threshold = 0.5
        elif load > 0.15:  # High load
            threshold = 0.7
        else:  # Critical load
            threshold = 0.9

        approved = priority_score >= threshold

        reason = f"priority={priority_score:.2f} threshold={threshold:.2f} "
        if not approved:
            reason += f"(denied: urgency={factors.urgency_score:.2f} "
            reason += f"tier={factors.agent_tier_score:.2f} load={1-load:.2f})"
        else:
            reason += "(approved)"

        # Log decision
        self._log_decision(request, factors, priority_score, approved)

        return approved, priority_score, reason

    def _log_decision(self, request: AllocationRequest, factors: DecisionFactors,
                     priority_score: float, approved: bool) -> None:
        """Log decision to database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO decisions (
                id, timestamp, agent, model, tokens, urgency, approved, priority_score,
                urgency_score, agent_tier_score, complexity_score, success_rate,
                load_factor, fairness_score, efficiency_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.task_id,
            request.timestamp,
            request.agent,
            request.model,
            request.requested_tokens,
            request.urgency.value,
            1 if approved else 0,
            priority_score,
            factors.urgency_score,
            factors.agent_tier_score,
            factors.complexity_score,
            factors.historical_success_rate,
            factors.current_load_factor,
            factors.fairness_score,
            factors.resource_efficiency
        ))
        conn.commit()
        conn.close()

        # Update recent allocations
        if approved:
            if request.agent not in self._recent_allocations:
                self._recent_allocations[request.agent] = []
            self._recent_allocations[request.agent].append(request.timestamp)
            # Keep only last 10 minutes
            cutoff = request.timestamp - 600
            self._recent_allocations[request.agent] = [
                t for t in self._recent_allocations[request.agent] if t > cutoff
            ]

    def record_outcome(self, task_id: str, success: bool, completion_time: float,
                      actual_tokens: int) -> None:
        """Record task outcome for learning."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT tokens FROM decisions WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        if not row:
            conn.close()
            return

        requested_tokens = row[0]
        efficiency = actual_tokens / max(completion_time, 0.1)  # tokens/sec

        conn.execute("""
            UPDATE decisions
            SET task_success = ?, completion_time = ?,
                actual_tokens_used = ?, resource_efficiency = ?
            WHERE id = ?
        """, (
            1 if success else 0,
            completion_time,
            actual_tokens,
            efficiency,
            task_id
        ))
        conn.commit()
        conn.close()

        # Trigger learning update periodically
        self._maybe_update_weights()

    def _maybe_update_weights(self) -> None:
        """Update weights based on recent outcomes (every 100 decisions)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM decisions WHERE task_success IS NOT NULL"
        )
        completed_count = cursor.fetchone()[0]
        conn.close()

        if completed_count % 100 == 0 and completed_count > 0:
            self._update_weights_from_outcomes()

    def _update_weights_from_outcomes(self) -> None:
        """Update decision weights using gradient descent on outcome quality."""
        conn = sqlite3.connect(self.db_path)

        cursor = conn.execute("""
            SELECT urgency_score, agent_tier_score, complexity_score, success_rate,
                   load_factor, fairness_score, efficiency_score,
                   task_success, priority_score, approved
            FROM decisions
            WHERE task_success IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 200
        """)

        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 50:  # Need enough data
            return

        # Find successful high-priority tasks
        successful_high_priority = []
        for row in rows:
            factors = row[:7]
            task_success = row[7]
            priority_score = row[8]

            if task_success == 1 and priority_score > 0.7:
                successful_high_priority.append(factors)

        # Reinforce patterns that led to success
        if successful_high_priority:
            learning_rate = 0.01
            avg_success = [
                sum(f[i] for f in successful_high_priority) / len(successful_high_priority)
                for i in range(7)
            ]

            weight_attrs = [
                'urgency', 'agent_tier', 'complexity', 'success_rate',
                'load_factor', 'fairness', 'efficiency'
            ]
            for i, attr in enumerate(weight_attrs):
                current = getattr(self.weights, attr)
                adjustment = avg_success[i] * learning_rate
                setattr(self.weights, attr, max(0.0, min(1.0, current + adjustment)))

        # Normalize weights
        total = sum(asdict(self.weights).values())
        for attr in asdict(self.weights).keys():
            setattr(self.weights, attr, getattr(self.weights, attr) / total)

        self._save_weights()

    def _get_agent_success_rate(self, agent: str) -> float:
        """Get historical success rate for an agent."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT AVG(task_success)
            FROM decisions
            WHERE agent = ? AND task_success IS NOT NULL
        """, (agent,))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result is not None else 0.7  # Default to 70%

    def _get_agent_efficiency(self, agent: str, model: str) -> float:
        """Get resource efficiency for agent/model combo."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT AVG(resource_efficiency)
            FROM decisions
            WHERE agent = ? AND model = ? AND resource_efficiency IS NOT NULL
        """, (agent, model))
        result = cursor.fetchone()[0]
        conn.close()
        return (result / 100.0) if result is not None else 0.5  # Normalize to 0-1

    def _compute_fairness_score(self, agent: str) -> float:
        """Compute fairness score (inverse of recent usage)."""
        recent = self._recent_allocations.get(agent, [])
        if not recent:
            return 1.0  # Max fairness if not used recently

        # More recent allocations = lower fairness score
        now = time.time()
        recency_weight = sum(1.0 / max(now - t, 1.0) for t in recent)

        # Normalize to 0-1 (inverse relationship)
        return max(0.0, 1.0 - min(recency_weight / 10.0, 1.0))

    def _get_current_load_factor(self) -> float:
        """Get current system load (1.0 = low load, 0.0 = high load)."""
        try:
            from core.kernel.budget_service import get_budget_service
            snapshot = get_budget_service().get_resource_snapshot()
            if snapshot.vram_util is not None:
                return 1.0 - snapshot.vram_util
            return 1.0
        except:
            return 0.5  # Default to medium load if unavailable

    def run(self) -> None:
        """Main agent loop."""
        while self._running:
            time.sleep(1)
            # Periodic maintenance
            self._cleanup_old_data()

    def _cleanup_old_data(self) -> None:
        """Remove old decision records (keep last 30 days)."""
        cutoff = time.time() - (30 * 24 * 60 * 60)
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM decisions WHERE timestamp < ?", (cutoff,))
        conn.commit()
        conn.close()


# Global singleton
_ALLOCATOR: Optional[BudgetAllocatorAgent] = None


def get_allocator() -> BudgetAllocatorAgent:
    """Get or create the global allocator agent."""
    global _ALLOCATOR
    if _ALLOCATOR is None:
        _ALLOCATOR = BudgetAllocatorAgent()
    return _ALLOCATOR
