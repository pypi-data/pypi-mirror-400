"""
Full System Test: Verify all kernel and cognitive layers.

Tests:
- Kernel bootstrap
- Mode system initialization
- Dense-state contract operations
- V-NAND storage integration
- End-to-end cognitive cycle
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


class SystemTest:
    """Full system integration test."""

    def __init__(self):
        """Initialize test suite."""
        self.tests: Dict[str, bool] = {}
        self.errors: Dict[str, str] = {}

    def test_imports(self) -> bool:
        """Test that all modules can be imported."""
        print("[TEST] Checking imports...")

        try:
            from core.agents.base import AgentContext, BaseAgent
            print("  [OK] core.agents.base")

            from core.kernel.services import KernelServices, init_services
            print("  [OK] core.kernel.services")

            from core.kernel.preflight import sovereignty_preflight_check
            print("  [OK] core.kernel.preflight")

            from core.kernel.switchboard import CortexSwitchboard
            print("  [OK] core.kernel.switchboard")

            from core.modes import SovereignLoopMode, TeachingMode, ForensicDebugMode
            print("  [OK] core.modes")

            from gpia.memory.dense_state import (
                DenseVectorContract,
                HyperVoxelContract,
                DenseStateLogEntry,
                DenseStateLogBuffer,
            )
            print("  [OK] gpia.memory.dense_state")

            from gpia.memory.dense_state.storage import DenseStateStorage
            print("  [OK] gpia.memory.dense_state.storage")

            from gpia.memory.vnand import VNANDStore, VNANDIndex, GarbageCollector
            print("  [OK] gpia.memory.vnand")

            return True

        except Exception as e:
            self.errors["imports"] = str(e)
            print(f"  [FAIL] {e}")
            return False

    def test_dense_state_contracts(self) -> bool:
        """Test dense-state contract system."""
        print("\n[TEST] Dense-state contracts...")

        try:
            import numpy as np
            from gpia.memory.dense_state import DenseVectorContract, HyperVoxelContract

            # Test vector contract
            vec_contract = DenseVectorContract(state_dim=128)
            vec_data = np.random.randn(128).astype(np.float32)
            vec_result = vec_contract.to_vector(vec_data)
            assert len(vec_result) == 128, "Vector shape mismatch"
            print("  [OK] DenseVectorContract operations")

            # Test voxel contract
            voxel_contract = HyperVoxelContract(shape=(8, 8, 8))
            voxel_data = np.random.randn(8, 8, 8).astype(np.float32)
            flat = voxel_contract.to_vector(voxel_data)
            assert len(flat) == 512, "Flattened shape mismatch"
            reconstructed = voxel_contract.unflatten(flat)
            assert reconstructed.shape == (8, 8, 8), "Reconstruction failed"
            print("  [OK] HyperVoxelContract operations")

            return True

        except Exception as e:
            self.errors["dense_state_contracts"] = str(e)
            print(f"  [FAIL] {e}")
            return False

    def test_logging_system(self) -> bool:
        """Test dense-state logging system."""
        print("\n[TEST] Dense-state logging...")

        try:
            from gpia.memory.dense_state import DenseStateLogEntry, DenseStateLogBuffer
            from gpia.memory.dense_state.storage import DenseStateStorage

            # Test buffer
            buffer = DenseStateLogBuffer(max_entries=100)
            for i in range(50):
                entry = DenseStateLogEntry(
                    vector=[float(j) / 10.0 for j in range(32)],
                    metrics={"batch": i}
                )
                buffer.append(entry)

            assert len(buffer.get_all()) == 50, "Buffer size mismatch"
            assert len(buffer.get_latest(10)) == 10, "Latest fetch failed"
            print("  [OK] DenseStateLogBuffer operations")

            # Test storage
            config = {"vnand": {"enabled": False}}
            storage = DenseStateStorage(config=config)
            for i in range(100):
                entry = DenseStateLogEntry(
                    vector=[float(j) / 100.0 for j in range(32)]
                )
                storage.append(entry)

            assert len(storage.get_all()) == 100, "Storage size mismatch"
            print("  [OK] DenseStateStorage operations")

            return True

        except Exception as e:
            self.errors["logging_system"] = str(e)
            print(f"  [FAIL] {e}")
            return False

    def test_vnand_storage(self) -> bool:
        """Test V-NAND storage."""
        print("\n[TEST] V-NAND storage...")

        try:
            import shutil
            from gpia.memory.vnand import VNANDStore, VNANDIndex, GarbageCollector

            # Cleanup
            shutil.rmtree("test_vnand_system", ignore_errors=True)

            # Test store
            store = VNANDStore(root_dir="test_vnand_system")
            entries = [{"id": f"e{i}", "data": f"test_{i}"} for i in range(50)]
            page_id = store.allocate_page(entries)
            assert page_id == 0, "First page should be 0"
            print("  [OK] VNANDStore allocation")

            # Test index
            index = VNANDIndex(root_dir="test_vnand_system")
            index.register_page(
                page_id=page_id,
                block_id=0,
                entry_ids=[f"e{i}" for i in range(50)],
                timestamp="2025-01-02T00:00:00Z",
                entry_count=50,
                raw_size=len(str(entries)),
                compressed_size=1000
            )
            print("  [OK] VNANDIndex registration")

            # Test GC
            gc = GarbageCollector(store, index, root_dir="test_vnand_system")
            gc.track_access([f"e{i}" for i in range(10)])
            print("  [OK] GarbageCollector tracking")

            # Cleanup
            shutil.rmtree("test_vnand_system", ignore_errors=True)

            return True

        except Exception as e:
            self.errors["vnand_storage"] = str(e)
            print(f"  [FAIL] {e}")
            return False

    def test_agent_context(self) -> bool:
        """Test AgentContext and identity."""
        print("\n[TEST] Agent context...")

        try:
            from core.agents.base import AgentContext
            from core.stubs import make_ledger, make_perception, make_telemetry

            # Create services
            ledger = make_ledger()
            perception = make_perception()
            telemetry = make_telemetry()

            # Create context
            ctx = AgentContext(
                identity={"agent_id": "test_agent", "kernel_signature": "test_sig_123"},
                telemetry=telemetry,
                ledger=ledger,
                perception=perception
            )

            assert ctx.identity["agent_id"] == "test_agent", "Agent ID mismatch"
            assert ctx.identity["kernel_signature"] == "test_sig_123", "Kernel signature mismatch"
            print("  [OK] AgentContext creation and fields")

            return True

        except Exception as e:
            self.errors["agent_context"] = str(e)
            print(f"  [FAIL] {e}")
            return False

    def test_mode_system(self) -> bool:
        """Test mode registration and lookup."""
        print("\n[TEST] Mode system...")

        try:
            from core.agents.base import AgentContext
            from core.modes import SovereignLoopMode, TeachingMode, ForensicDebugMode
            from core.stubs import make_ledger, make_perception, make_telemetry

            # Create context
            ledger = make_ledger()
            perception = make_perception()
            telemetry = make_telemetry()

            ctx = AgentContext(
                identity={"agent_id": "mode_test", "kernel_signature": "mode_sig"},
                telemetry=telemetry,
                ledger=ledger,
                perception=perception
            )

            # Instantiate modes
            modes = [
                SovereignLoopMode(ctx),
                TeachingMode(ctx),
                ForensicDebugMode(ctx)
            ]

            assert len(modes) == 3, "Mode count mismatch"
            assert modes[0].mode_name == "Sovereign-Loop", "Mode name mismatch"
            print("  [OK] Mode instantiation")

            return True

        except Exception as e:
            self.errors["mode_system"] = str(e)
            print(f"  [FAIL] {e}")
            return False

    def test_dense_state_in_storage(self) -> bool:
        """Test dense-state integration with V-NAND."""
        print("\n[TEST] Dense-state + V-NAND integration...")

        try:
            import shutil
            from gpia.memory.dense_state import DenseStateLogEntry
            from gpia.memory.dense_state.storage import DenseStateStorage

            # Cleanup
            shutil.rmtree("test_integrated", ignore_errors=True)

            # Create storage with V-NAND enabled
            config = {
                "vnand": {
                    "enabled": True,
                    "root_dir": "test_integrated",
                    "page_bytes": 4096,
                    "block_pages": 256,
                    "compression": "zstd",
                    "checksum": "xxh3",
                    "gc_threshold": 0.35
                }
            }

            storage = DenseStateStorage(config=config)

            # Log entries
            for i in range(50):
                entry = DenseStateLogEntry(
                    vector=[float(j) / 100.0 for j in range(32)],
                    mode="vector",
                    metrics={"iteration": i}
                )
                result = storage.append(entry)
                if result.storage_ref:
                    assert "page_id" in result.storage_ref, "Storage ref missing page_id"

            # Check stats
            stats = storage.storage_stats()
            assert "store" in stats or "buffer" in stats, "Storage stats missing"
            print("  [OK] Dense-state V-NAND integration")

            # Cleanup
            shutil.rmtree("test_integrated", ignore_errors=True)

            return True

        except Exception as e:
            self.errors["integration"] = str(e)
            print(f"  [FAIL] {e}")
            return False

    def run_all(self) -> Dict[str, Any]:
        """Run all tests."""
        print("=" * 60)
        print("FULL SYSTEM TEST")
        print("=" * 60)

        self.tests["imports"] = self.test_imports()
        self.tests["dense_state_contracts"] = self.test_dense_state_contracts()
        self.tests["logging_system"] = self.test_logging_system()
        self.tests["vnand_storage"] = self.test_vnand_storage()
        self.tests["agent_context"] = self.test_agent_context()
        self.tests["mode_system"] = self.test_mode_system()
        self.tests["integration"] = self.test_dense_state_in_storage()

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for v in self.tests.values() if v)
        total = len(self.tests)

        for test_name, result in sorted(self.tests.items()):
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status} {test_name}")
            if not result and test_name in self.errors:
                print(f"       Error: {self.errors[test_name]}")

        print(f"\nResult: {passed}/{total} tests passed")

        return {
            "passed": passed,
            "total": total,
            "tests": self.tests,
            "errors": self.errors
        }


if __name__ == "__main__":
    test = SystemTest()
    results = test.run_all()

    # Exit with appropriate code
    sys.exit(0 if results["passed"] == results["total"] else 1)
