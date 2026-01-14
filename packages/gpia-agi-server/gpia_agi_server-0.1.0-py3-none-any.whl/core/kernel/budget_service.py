"""
Budget Service - Kernel-level resource allocation and safety enforcement.

Provides:
- Real-time resource monitoring (CPU, GPU, NPU, RAM, VRAM, Disk I/O)
- Hard safety limits to prevent GPU damage
- Transaction-style allocation tracking
- Integration with telemetry and budget orchestrator

This service is initialized once at boot and persists across all modes.
"""

import os
import time
import psutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from core.budget_ledger import get_budget_ledger
from core.dynamic_budget_orchestrator import compute_budget


@dataclass
class ResourceSnapshot:
    """Current system resource state."""
    timestamp: float
    cpu_percent: float
    ram_total_mb: int
    ram_free_mb: int
    ram_used_mb: int
    vram_total_mb: Optional[int]
    vram_free_mb: Optional[int]
    vram_used_mb: Optional[int]
    disk_read_mbps: float
    disk_write_mbps: float
    npu_available: bool

    @property
    def ram_util(self) -> float:
        """RAM utilization ratio (0.0-1.0)."""
        return self.ram_used_mb / max(self.ram_total_mb, 1)

    @property
    def vram_util(self) -> Optional[float]:
        """VRAM utilization ratio (0.0-1.0)."""
        if self.vram_total_mb and self.vram_used_mb is not None:
            return self.vram_used_mb / max(self.vram_total_mb, 1)
        return None


@dataclass
class SafetyLimits:
    """Hard safety limits to prevent hardware damage."""
    max_vram_util: float = 0.90  # 90% - leave headroom for system
    max_ram_util: float = 0.90   # 90%
    max_cpu_util: float = 0.95   # 95%
    max_disk_write_mbps: float = 500.0  # Prevent SSD wear
    vram_reserve_mb: int = 1024  # Always keep 1GB VRAM free
    ram_reserve_mb: int = 2048   # Always keep 2GB RAM free


class BudgetService:
    """
    Kernel service for resource allocation and safety enforcement.

    Initialized once at boot, persists across all modes.
    Provides API for resource requests and tracks allocations.
    """

    def __init__(self):
        """Initialize budget service."""
        self.ledger = get_budget_ledger()
        self.limits = SafetyLimits()
        self._last_snapshot = None
        self._last_snapshot_time = 0.0
        self._snapshot_ttl = 2.0  # 2 seconds (much faster than 20s)

        # Disk I/O tracking
        self._last_disk_io = None
        self._last_disk_io_time = 0.0

        # Emergency shutdown flag
        self._emergency_shutdown = False

    def get_resource_snapshot(self, force_refresh: bool = False) -> ResourceSnapshot:
        """
        Get current resource state with caching.

        Args:
            force_refresh: Skip cache and get fresh data

        Returns:
            ResourceSnapshot with current resource state
        """
        now = time.time()
        if not force_refresh and self._last_snapshot and \
                (now - self._last_snapshot_time) < self._snapshot_ttl:
            return self._last_snapshot

        # Get RAM/CPU
        try:
            proc = psutil.Process()
            psutil_available = True
            cpu_percent = psutil.cpu_percent(interval=0.1)
            vm = psutil.virtual_memory()
            ram_total_mb = int(vm.total / (1024 * 1024))
            ram_used_mb = int(vm.used / (1024 * 1024))
        except:
            psutil_available = False
            cpu_percent = 0.0
            ram_total_mb = 0
            ram_used_mb = 0

        # Get VRAM (nvidia-smi)
        vram_total_mb = None
        vram_used_mb = None
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.total,memory.used",
                    "--format=csv,noheader,nounits"
                ],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                line = (result.stdout or "").strip().split("\n")[0]
                parts = [int(x.strip()) for x in line.split(",")[:2]]
                if len(parts) == 2:
                    vram_total_mb, vram_used_mb = parts
        except:
            pass

        # Get disk I/O
        disk_read_mbps, disk_write_mbps = self._get_disk_io_rates()

        # Check NPU availability
        npu_available = False
        try:
            from core.npu_utils import has_npu
            npu_available = has_npu()
        except:
            pass

        snapshot = ResourceSnapshot(
            timestamp=now,
            cpu_percent=cpu_percent,
            ram_total_mb=ram_total_mb,
            ram_free_mb=ram_total_mb - ram_used_mb,
            ram_used_mb=ram_used_mb,
            vram_total_mb=vram_total_mb,
            vram_free_mb=(vram_total_mb - vram_used_mb) if vram_total_mb else None,
            vram_used_mb=vram_used_mb,
            disk_read_mbps=disk_read_mbps,
            disk_write_mbps=disk_write_mbps,
            npu_available=npu_available
        )

        self._last_snapshot = snapshot
        self._last_snapshot_time = now
        return snapshot

    def _get_disk_io_rates(self) -> Tuple[float, float]:
        """
        Calculate disk I/O rates in MB/s.

        Returns:
            Tuple of (read_mbps, write_mbps)
        """
        try:
            counters = psutil.disk_io_counters()
            now = time.time()

            if self._last_disk_io is None:
                self._last_disk_io = (counters.read_bytes, counters.write_bytes)
                self._last_disk_io_time = now
                return 0.0, 0.0

            elapsed = now - self._last_disk_io_time
            if elapsed < 0.1:  # Too soon
                return 0.0, 0.0

            read_delta = counters.read_bytes - self._last_disk_io[0]
            write_delta = counters.write_bytes - self._last_disk_io[1]

            read_mbps = (read_delta / elapsed) / (1024 * 1024)
            write_mbps = (write_delta / elapsed) / (1024 * 1024)

            self._last_disk_io = (counters.read_bytes, counters.write_bytes)
            self._last_disk_io_time = now

            return max(0.0, read_mbps), max(0.0, write_mbps)
        except:
            return 0.0, 0.0

    def check_safety(self, snapshot: Optional[ResourceSnapshot] = None) -> Tuple[bool, str]:
        """
        Check if current resource state is safe.

        Args:
            snapshot: ResourceSnapshot to check (or None to get fresh)

        Returns:
            Tuple of (is_safe, reason)
        """
        if snapshot is None:
            snapshot = self.get_resource_snapshot(force_refresh=True)

        # Check VRAM (CRITICAL - prevents GPU damage)
        if snapshot.vram_util is not None and snapshot.vram_util >= self.limits.max_vram_util:
            self._emergency_shutdown = True
            return False, (
                f"VRAM critical: {snapshot.vram_util*100:.1f}% >= "
                f"{self.limits.max_vram_util*100:.0f}%"
            )

        if snapshot.vram_free_mb is not None and \
                snapshot.vram_free_mb < self.limits.vram_reserve_mb:
            return False, (
                f"VRAM reserve breach: {snapshot.vram_free_mb}MB < "
                f"{self.limits.vram_reserve_mb}MB"
            )

        # Check RAM
        if snapshot.ram_util >= self.limits.max_ram_util:
            return False, (
                f"RAM critical: {snapshot.ram_util*100:.1f}% >= "
                f"{self.limits.max_ram_util*100:.0f}%"
            )

        # Check CPU
        if snapshot.cpu_percent >= self.limits.max_cpu_util * 100:
            return False, (
                f"CPU critical: {snapshot.cpu_percent:.1f}% >= "
                f"{self.limits.max_cpu_util*100:.0f}%"
            )

        # Check disk write rate (prevent SSD wear)
        if snapshot.disk_write_mbps > self.limits.max_disk_write_mbps:
            return False, (
                f"Disk write critical: {snapshot.disk_write_mbps:.1f} MB/s > "
                f"{self.limits.max_disk_write_mbps:.0f} MB/s"
            )

        return True, "ok"

    def request_allocation(self, task_id: str, agent: str, model: str,
                          prompt: str, requested_tokens: int) -> Tuple[bool, int, str]:
        """
        Request token allocation for a task.

        Performs safety check and computes budget using existing orchestrator.

        Args:
            task_id: Unique task identifier
            agent: Agent name (professor, alpha, gpia, etc.)
            model: Model ID (e.g., codegemma:latest)
            prompt: The prompt text
            requested_tokens: Requested token count

        Returns:
            Tuple of (approved, allocated_tokens, reason)
        """
        # Check safety first
        snapshot = self.get_resource_snapshot(force_refresh=True)
        is_safe, safety_reason = self.check_safety(snapshot)

        if not is_safe:
            return False, 0, f"Safety check failed: {safety_reason}"

        # Compute budget using existing orchestrator
        effective_tokens, details = compute_budget(
            prompt=prompt,
            requested_tokens=requested_tokens,
            model_id=model
        )

        # Try to reserve in ledger
        reserved = self.ledger.reserve(task_id, agent, model, effective_tokens)

        if not reserved:
            return False, 0, "Insufficient global budget"

        return True, effective_tokens, "approved"

    def activate_allocation(self, task_id: str) -> None:
        """Mark allocation as active (execution started)."""
        self.ledger.activate(task_id)

    def release_allocation(self, task_id: str, success: bool = True) -> None:
        """
        Release allocated tokens.

        Args:
            task_id: Task identifier
            success: Whether task completed successfully
        """
        status = "completed" if success else "failed"
        self.ledger.release(task_id, status)

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics."""
        return self.ledger.get_usage_stats()

    def is_emergency_shutdown(self) -> bool:
        """Check if emergency shutdown was triggered."""
        return self._emergency_shutdown


# Global singleton
_BUDGET_SERVICE: Optional[BudgetService] = None
_BUDGET_SERVICE_LOCK = None


def get_budget_service() -> BudgetService:
    """Get or create the global budget service."""
    global _BUDGET_SERVICE, _BUDGET_SERVICE_LOCK
    if _BUDGET_SERVICE_LOCK is None:
        import threading
        _BUDGET_SERVICE_LOCK = threading.Lock()

    if _BUDGET_SERVICE is None:
        with _BUDGET_SERVICE_LOCK:
            if _BUDGET_SERVICE is None:
                _BUDGET_SERVICE = BudgetService()
    return _BUDGET_SERVICE
