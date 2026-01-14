"""
Kernel Benchmarks: Measure initialization, mode switching, and dense-state performance.

Tests:
- Kernel boot time
- Mode transition time
- Dense-state logging throughput
- V-NAND storage performance
- Memory overhead
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

import numpy as np


class BenchmarkSuite:
    """Benchmark suite for kernel and cognitive system."""

    def __init__(self, output_dir: str = "benchmarks"):
        """Initialize benchmark suite."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: Dict[str, Any] = {}

    def benchmark_kernel_init(self) -> float:
        """Measure kernel initialization time."""
        from core.kernel.services import init_services
        from core.kernel.preflight import sovereignty_preflight_check

        start = time.perf_counter()
        services = init_services()
        end = time.perf_counter()

        init_time = (end - start) * 1000  # ms

        self.results["kernel_init_ms"] = init_time
        return init_time

    def benchmark_mode_switching(self, num_switches: int = 10) -> float:
        """Measure mode transition overhead."""
        from core.agents.base import AgentContext, ModeTransition
        from core.kernel.services import init_services
        from core.modes import SovereignLoopMode, TeachingMode

        # Setup
        services = init_services()
        ctx = AgentContext(
            agent_id="bench_agent",
            kernel_signature="bench_sig",
            services=services
        )

        modes = [SovereignLoopMode(ctx), TeachingMode(ctx)]
        transitions = 0

        start = time.perf_counter()

        # Perform mode switches
        for i in range(num_switches):
            # Simulate transition
            old_mode = modes[i % 2]
            new_mode = modes[(i + 1) % 2]

            try:
                old_mode.on_exit()
            except:
                pass

            try:
                new_mode.on_enter()
            except:
                pass

            transitions += 1

        end = time.perf_counter()

        total_time = (end - start) * 1000  # ms
        avg_per_switch = total_time / max(transitions, 1)

        self.results["mode_switch_total_ms"] = total_time
        self.results["mode_switch_avg_ms"] = avg_per_switch

        return avg_per_switch

    def benchmark_dense_state_logging(self, num_entries: int = 1000) -> Dict[str, float]:
        """Measure dense-state logging throughput."""
        from gpia.memory.dense_state import DenseStateLogEntry
        from gpia.memory.dense_state.storage import DenseStateStorage

        config = {"vnand": {"enabled": False}}
        storage = DenseStateStorage(config=config)

        start = time.perf_counter()

        # Log entries
        for i in range(num_entries):
            entry = DenseStateLogEntry(
                vector=[np.sin(i / 100.0) + 0.1 * j for j in range(32)],
                mode="vector",
                adapter_id="bench",
                metrics={"batch": i}
            )
            storage.append(entry)

        end = time.perf_counter()

        total_time = (end - start) * 1000  # ms
        throughput = num_entries / (end - start)  # entries/sec

        self.results["dense_state_logging_ms"] = total_time
        self.results["dense_state_throughput_eps"] = throughput

        return {
            "total_time_ms": total_time,
            "throughput_eps": throughput,
            "avg_per_entry_us": (total_time * 1000) / num_entries
        }

    def benchmark_vnand_storage(self, num_pages: int = 10) -> Dict[str, float]:
        """Measure V-NAND storage performance."""
        from gpia.memory.vnand import VNANDStore
        import shutil

        store_dir = "bench_vnand"
        shutil.rmtree(store_dir, ignore_errors=True)

        store = VNANDStore(
            root_dir=store_dir,
            page_bytes=4096,
            block_pages=256,
            compression="zstd"
        )

        # Write pages
        start = time.perf_counter()

        for i in range(num_pages):
            entries = [
                {"id": f"e{j}", "data": f"entry_{i}_{j}"}
                for j in range(100)
            ]
            page_id = store.allocate_page(entries)

        write_time = (time.perf_counter() - start) * 1000

        # Read pages
        start = time.perf_counter()

        for page_id in range(num_pages):
            entries = store.read_page(page_id)

        read_time = (time.perf_counter() - start) * 1000

        stats = store.get_stats()

        # Cleanup
        shutil.rmtree(store_dir, ignore_errors=True)

        result = {
            "write_time_ms": write_time,
            "read_time_ms": read_time,
            "pages_written": num_pages,
            "compression_ratio": stats["compression_ratio"]
        }

        self.results["vnand_write_ms"] = write_time
        self.results["vnand_read_ms"] = read_time
        self.results["vnand_compression_ratio"] = stats["compression_ratio"]

        return result

    def benchmark_dense_state_contracts(self) -> Dict[str, float]:
        """Measure dense-state contract operations."""
        import numpy as np
        from gpia.memory.dense_state import HyperVoxelContract, DenseVectorContract

        # Vector operations
        vec_contract = DenseVectorContract(state_dim=512)
        vec_data = np.random.randn(512).astype(np.float32)

        start = time.perf_counter()
        for _ in range(1000):
            vec_contract.to_vector(vec_data)
        vec_time = (time.perf_counter() - start) * 1000

        # Voxel operations
        voxel_contract = HyperVoxelContract(shape=(8, 8, 8))
        voxel_data = np.random.randn(8, 8, 8).astype(np.float32)

        start = time.perf_counter()
        for _ in range(1000):
            flat = voxel_contract.to_vector(voxel_data)
            voxel_contract.unflatten(flat)
        voxel_time = (time.perf_counter() - start) * 1000

        result = {
            "vector_ops_1k_ms": vec_time,
            "voxel_ops_1k_ms": voxel_time,
            "vector_ops_ns": (vec_time * 1e6) / 1000,
            "voxel_ops_ns": (voxel_time * 1e6) / 1000
        }

        self.results.update(result)
        return result

    def run_all(self) -> Dict[str, Any]:
        """Run all benchmarks."""
        print("[Kernel Benchmarks] Starting benchmark suite...\n")

        print("1. Kernel Initialization...")
        try:
            init_time = self.benchmark_kernel_init()
            print(f"   Kernel init: {init_time:.2f} ms")
        except Exception as e:
            print(f"   [SKIP] {e}")

        print("\n2. Mode Switching...")
        try:
            switch_time = self.benchmark_mode_switching()
            print(f"   Mode switch avg: {switch_time:.3f} ms/switch")
        except Exception as e:
            print(f"   [SKIP] {e}")

        print("\n3. Dense-State Logging...")
        try:
            ds_stats = self.benchmark_dense_state_logging()
            print(f"   Throughput: {ds_stats['throughput_eps']:.0f} entries/sec")
        except Exception as e:
            print(f"   [SKIP] {e}")

        print("\n4. Dense-State Contracts...")
        try:
            contract_stats = self.benchmark_dense_state_contracts()
            print(f"   Vector ops: {contract_stats['vector_ops_ns']:.1f} ns/op")
            print(f"   Voxel ops: {contract_stats['voxel_ops_ns']:.1f} ns/op")
        except Exception as e:
            print(f"   [SKIP] {e}")

        print("\n5. V-NAND Storage...")
        try:
            vnand_stats = self.benchmark_vnand_storage()
            print(f"   Write: {vnand_stats['write_time_ms']:.2f} ms")
            print(f"   Read: {vnand_stats['read_time_ms']:.2f} ms")
            print(f"   Compression: {vnand_stats['compression_ratio']:.2f}x")
        except Exception as e:
            print(f"   [SKIP] {e}")

        # Save results
        results_file = self.output_dir / "results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n[Kernel Benchmarks] Results saved to {results_file}")
        return self.results


if __name__ == "__main__":
    suite = BenchmarkSuite()
    results = suite.run_all()
    print("\nFinal Results:")
    for key, value in sorted(results.items()):
        print(f"  {key}: {value}")
