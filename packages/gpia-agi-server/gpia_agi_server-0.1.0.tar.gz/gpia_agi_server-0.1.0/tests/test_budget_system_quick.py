"""
Quick tests for Budget Allocator System

Verifies:
- Kernel service initialization
- Safety limit enforcement
- Budget ledger tracking
- Allocator decision making
- Validator risk assessment
"""

import time
import pytest
from core.kernel.budget_service import get_budget_service, ResourceSnapshot, SafetyLimits
from core.budget_ledger import get_budget_ledger
from agents.budget_allocator_autonomous import BudgetAllocatorAgent, AllocationRequest, TaskUrgency
from agents.budget_validator_autonomous import BudgetValidatorAgent


class TestBudgetService:
    """Test kernel-level budget service."""

    def test_service_initialization(self):
        """Test budget service can be initialized."""
        service = get_budget_service()
        assert service is not None

    def test_resource_snapshot(self):
        """Test resource monitoring."""
        service = get_budget_service()
        snapshot = service.get_resource_snapshot(force_refresh=True)

        assert snapshot is not None
        assert snapshot.cpu_percent >= 0.0
        assert snapshot.ram_total_mb > 0
        assert snapshot.ram_used_mb >= 0
        assert snapshot.timestamp > 0

    def test_safety_check(self):
        """Test safety limit checking."""
        service = get_budget_service()
        snapshot = service.get_resource_snapshot(force_refresh=True)

        is_safe, reason = service.check_safety(snapshot)
        assert isinstance(is_safe, bool)
        assert isinstance(reason, str)

        # Should be safe under normal conditions
        if snapshot.vram_util is None or snapshot.vram_util < 0.8:
            assert is_safe

    def test_allocation_request(self):
        """Test allocation request flow."""
        service = get_budget_service()

        approved, tokens, reason = service.request_allocation(
            task_id="test_001",
            agent="test_agent",
            model="codegemma:latest",
            prompt="Test prompt for allocation",
            requested_tokens=500
        )

        assert isinstance(approved, bool)
        assert isinstance(tokens, int)
        assert isinstance(reason, str)

        if approved:
            assert tokens > 0
            assert tokens <= 500
            service.release_allocation("test_001")


class TestBudgetLedger:
    """Test global budget tracking."""

    def test_ledger_initialization(self):
        """Test ledger can be initialized."""
        ledger = get_budget_ledger()
        assert ledger is not None

    def test_allocation_tracking(self):
        """Test allocation reservation and release."""
        ledger = get_budget_ledger()

        # Reserve
        reserved = ledger.reserve(
            task_id="ledger_test_001",
            agent="test",
            model="test:latest",
            tokens=300
        )
        assert reserved

        # Activate
        ledger.activate("ledger_test_001")

        # Check stats
        stats = ledger.get_usage_stats()
        assert stats['total_active_tokens'] >= 300

        # Release
        ledger.release("ledger_test_001")


class TestBudgetAllocator:
    """Test ML-based allocator decisions."""

    def test_allocator_initialization(self):
        """Test allocator can be initialized."""
        allocator = BudgetAllocatorAgent(
            db_path="/tmp/test_budget_allocator.db"
        )
        assert allocator is not None

    def test_decision_factors(self):
        """Test factor computation."""
        allocator = BudgetAllocatorAgent(
            db_path="/tmp/test_budget_allocator.db"
        )

        request = AllocationRequest(
            task_id="test_001",
            agent="professor",
            model="deepseek-r1:latest",
            prompt="Test prompt",
            requested_tokens=800,
            urgency=TaskUrgency.IMMEDIATE,
            complexity_score=0.7,
            timestamp=time.time()
        )

        factors = allocator.compute_factors(request)
        assert factors is not None
        assert 0.0 <= factors.urgency_score <= 1.0
        assert 0.0 <= factors.agent_tier_score <= 1.0
        assert 0.0 <= factors.complexity_score <= 1.0

    def test_priority_scoring(self):
        """Test priority score calculation."""
        allocator = BudgetAllocatorAgent(
            db_path="/tmp/test_budget_allocator.db"
        )

        request = AllocationRequest(
            task_id="test_002",
            agent="professor",
            model="deepseek-r1:latest",
            prompt="Test prompt",
            requested_tokens=800,
            urgency=TaskUrgency.IMMEDIATE,
            complexity_score=0.6,
            timestamp=time.time()
        )

        approved, priority, reason = allocator.evaluate_request(request)
        assert 0.0 <= priority <= 1.0
        assert isinstance(reason, str)
        # Immediate urgency should score reasonably high
        assert priority > 0.2


class TestBudgetValidator:
    """Test QA/validation layer."""

    def test_validator_initialization(self):
        """Test validator can be initialized."""
        validator = BudgetValidatorAgent(
            validation_log="/tmp/test_validations.jsonl"
        )
        assert validator is not None

    def test_low_risk_validation(self):
        """Test validation of low-risk allocation."""
        validator = BudgetValidatorAgent(
            validation_log="/tmp/test_validations.jsonl"
        )

        result = validator.validate_allocation(
            task_id="val_001",
            agent="test_agent",
            model="codegemma:latest",
            requested_tokens=500,
            allocator_priority=0.8,
            current_vram_util=0.3  # Low VRAM usage
        )

        assert result.risk_level == "low"
        assert result.approved

    def test_high_risk_validation(self):
        """Test validation of high-risk allocation."""
        validator = BudgetValidatorAgent(
            validation_log="/tmp/test_validations.jsonl"
        )

        result = validator.validate_allocation(
            task_id="val_002",
            agent="test_agent",
            model="gpt-oss:latest",
            requested_tokens=3000,
            allocator_priority=0.5,  # Low priority
            current_vram_util=0.85   # High VRAM usage
        )

        assert result.risk_level in ["high", "critical"]
        # Low priority with high risk should be denied
        assert not result.approved


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_allocation_flow(self):
        """Test complete allocation flow."""
        service = get_budget_service()
        ledger = get_budget_ledger()

        # Request allocation
        approved, tokens, reason = service.request_allocation(
            task_id="e2e_001",
            agent="test_agent",
            model="qwen3:latest",
            prompt="End-to-end test prompt",
            requested_tokens=600
        )

        if approved:
            # Activate
            service.activate_allocation("e2e_001")

            # Check ledger
            alloc = ledger.get_allocation("e2e_001")
            assert alloc is not None

            # Release
            service.release_allocation("e2e_001", success=True)

            # Verify released
            alloc = ledger.get_allocation("e2e_001")
            assert alloc.status == "completed"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
