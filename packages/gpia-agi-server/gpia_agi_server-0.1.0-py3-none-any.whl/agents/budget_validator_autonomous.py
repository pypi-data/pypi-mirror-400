"""
Budget Validator Agent - QA layer for high-risk allocation decisions

Reviews priority judge decisions before approval.
Can override/veto allocations that seem risky.
Focuses on preventing GPU damage and system instability.
"""

import os
import time
import json
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validation decision."""
    approved: bool
    confidence: float  # 0.0-1.0
    reason: str
    risk_level: str  # "low", "medium", "high", "critical"
    recommended_action: str  # "approve", "reduce", "deny", "defer"


class BudgetValidatorAgent:
    """
    QA agent that validates budget allocator decisions.

    Focuses on:
    - Detecting patterns that could lead to GPU damage
    - Identifying resource allocation anomalies
    - Enforcing conservative limits during high-risk periods
    """

    def __init__(self, validation_log: str = "/app/logs/budget_validations.jsonl"):
        """Initialize the validator agent."""
        self.validation_log = Path(validation_log)
        self._running = True

        # Risk thresholds
        self.vram_critical_threshold = 0.90
        self.vram_warning_threshold = 0.75

        # Historical context
        self._recent_validations = []

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

    def _shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        self._running = False

    def validate_allocation(self, task_id: str, agent: str, model: str,
                           requested_tokens: int, allocator_priority: float,
                           current_vram_util: Optional[float]) -> ValidationResult:
        """
        Validate an allocation decision from the priority judge.

        Args:
            task_id: Task identifier
            agent: Agent name
            model: Model ID
            requested_tokens: Tokens requested
            allocator_priority: Priority score from allocator (0-1)
            current_vram_util: Current VRAM utilization (0-1)

        Returns:
            ValidationResult with recommendation
        """
        risks = []
        risk_level = "low"

        # Default VRAM utilization if not provided
        if current_vram_util is None:
            try:
                from core.kernel.budget_service import get_budget_service
                snapshot = get_budget_service().get_resource_snapshot()
                current_vram_util = snapshot.vram_util or 0.5
            except:
                current_vram_util = 0.5

        # 1. VRAM risk
        if current_vram_util >= self.vram_critical_threshold:
            risks.append(f"VRAM critical: {current_vram_util*100:.1f}%")
            risk_level = "critical"
        elif current_vram_util >= self.vram_warning_threshold:
            risks.append(f"VRAM high: {current_vram_util*100:.1f}%")
            risk_level = max(risk_level, "high")

        # 2. Token volume risk (large allocations)
        if requested_tokens > 2000:
            risks.append(f"Large token request: {requested_tokens}")
            risk_level = max(risk_level, "medium")

        # 3. Model size risk
        large_models = ["gpt-oss", "deepseek", "20b"]
        if any(m in model.lower() for m in large_models):
            if current_vram_util > 0.6:
                risks.append(f"Large model on high VRAM: {model}")
                risk_level = max(risk_level, "high")

        # 4. Rapid allocation pattern (could indicate runaway process)
        recent_count = len([
            v for v in self._recent_validations
            if time.time() - v < 10
        ])
        if recent_count > 20:
            risks.append(f"Rapid allocation pattern: {recent_count} in 10s")
            risk_level = "critical"

        # 5. Historical failure pattern
        recent_failures = self._get_recent_failures(agent)
        if recent_failures > 3:
            risks.append(f"Agent has {recent_failures} recent failures")
            risk_level = max(risk_level, "medium")

        # Decision logic
        if risk_level == "critical":
            return ValidationResult(
                approved=False,
                confidence=0.95,
                reason="; ".join(risks),
                risk_level=risk_level,
                recommended_action="deny"
            )

        if risk_level == "high":
            # High risk: only approve if priority is very high
            if allocator_priority < 0.85:
                return ValidationResult(
                    approved=False,
                    confidence=0.85,
                    reason=f"High risk with priority {allocator_priority:.2f}: {'; '.join(risks)}",
                    risk_level=risk_level,
                    recommended_action="deny"
                )
            else:
                # Approve but recommend token reduction
                return ValidationResult(
                    approved=True,
                    confidence=0.7,
                    reason=f"High risk but high priority: {allocator_priority:.2f}",
                    risk_level=risk_level,
                    recommended_action="reduce"
                )

        if risk_level == "medium":
            # Medium risk: approve with caution
            return ValidationResult(
                approved=True,
                confidence=0.8,
                reason=f"Medium risk: {'; '.join(risks) if risks else 'none'}",
                risk_level=risk_level,
                recommended_action="approve"
            )

        # Low risk: approve
        return ValidationResult(
            approved=True,
            confidence=0.95,
            reason="Low risk",
            risk_level=risk_level,
            recommended_action="approve"
        )

    def _get_recent_failures(self, agent: str) -> int:
        """Get count of recent failures for an agent."""
        try:
            import sqlite3
            allocator_db = "/app/memories/budget_allocator.db"
            if not Path(allocator_db).exists():
                return 0

            conn = sqlite3.connect(allocator_db)
            cursor = conn.execute("""
                SELECT COUNT(*)
                FROM decisions
                WHERE agent = ? AND task_success = 0
                  AND timestamp > ?
            """, (agent, time.time() - 3600))  # Last hour
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0

    def log_validation(self, task_id: str, result: ValidationResult) -> None:
        """Log validation decision."""
        self._recent_validations.append(time.time())

        # Clean old entries (keep last minute)
        cutoff = time.time() - 60
        self._recent_validations = [
            t for t in self._recent_validations if t > cutoff
        ]

        # Log to file
        self.validation_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.validation_log, "a") as f:
            f.write(json.dumps({
                "timestamp": time.time(),
                "task_id": task_id,
                "approved": result.approved,
                "confidence": result.confidence,
                "risk_level": result.risk_level,
                "reason": result.reason,
                "action": result.recommended_action
            }) + "\n")

    def run(self) -> None:
        """Main agent loop."""
        while self._running:
            time.sleep(1)
            # Could implement active monitoring here


# Global singleton
_VALIDATOR: Optional[BudgetValidatorAgent] = None


def get_validator() -> BudgetValidatorAgent:
    """Get or create the global validator agent."""
    global _VALIDATOR
    if _VALIDATOR is None:
        _VALIDATOR = BudgetValidatorAgent()
    return _VALIDATOR
