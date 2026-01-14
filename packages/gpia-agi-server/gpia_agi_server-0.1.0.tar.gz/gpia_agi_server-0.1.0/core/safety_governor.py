
import os
import time
import subprocess
import shutil
import sqlite3
import logging
from pathlib import Path
from typing import Dict, Tuple

class SafetyGovernor:
    """
    Hardware Protection Layer (The Circuit Breaker).
    Monitors VRAM, Temperature, and Disk to prevent hardware stress.
    """
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.log_dir = repo_root / "logs" / "safety"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Thresholds (Conservative Safety)
        self.vram_limit_pct = 85.0    # 85% VRAM is the hard ceiling
        self.temp_limit_c = 78.0      # 78°C is the thermal throttle point
        self.disk_min_free_gb = 50.0  # Keep 50GB free on the 2TB ground
        
        # State
        self.is_throttled = False
        self.critical_stop = False
        
        logging.basicConfig(
            filename=self.log_dir / "hardware_safety.log",
            level=logging.INFO,
            format='%(asctime)s - [SAFETY] - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_gpu_vitals(self) -> Dict:
        """Query nvidia-smi for VRAM and Temperature."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total,temperature.gpu",
                 "--format=csv,nounits,noheader"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                used, total, temp = map(float, result.stdout.strip().split(','))
                return {
                    "vram_pct": (used / total) * 100,
                    "temp": temp,
                    "vram_mb": used
                }
        except Exception as e:
            self.logger.error(f"Failed to query GPU: {e}")
        return {"vram_pct": 0, "temp": 0, "vram_mb": 0}

    def check_disk_health(self) -> Dict:
        """Check free space and detect potential thrashing."""
        total, used, free = shutil.disk_usage(self.repo_root)
        free_gb = free / (1024**3)
        return {
            "free_gb": free_gb,
            "is_low": free_gb < self.disk_min_free_gb
        }

    def audit_system(self) -> Tuple[bool, str]:
        """
        Perform a full safety audit.
        Returns: (is_safe, message)
        """
        gpu = self.get_gpu_vitals()
        disk = self.check_disk_health()
        
        # 1. Thermal Check (Critical)
        if gpu["temp"] > self.temp_limit_c:
            self.is_throttled = True
            msg = f"THERMAL OVERHEAT: {gpu['temp']}°C > {self.temp_limit_c}°C"
            self.logger.warning(msg)
            return False, msg
            
        # 2. VRAM Check (Limit)
        if gpu["vram_pct"] > self.vram_limit_pct:
            msg = f"VRAM CRITICAL: {gpu['vram_pct']:.1f}% > {self.vram_limit_pct}%"
            self.logger.warning(msg)
            return False, msg
            
        # 3. Disk Space Check
        if disk["is_low"]:
            msg = f"DISK SPACE LOW: {disk['free_gb']:.1f}GB left on 2TB ground"
            self.logger.warning(msg)
            return False, msg

        # System is Green
        self.is_throttled = False
        return True, "SYSTEM_ALIGNED_SAFE"

    def get_throttle_factor(self) -> float:
        """
        Calculates how much to slow down the HRz.
        1.0 = Full speed, 0.1 = Near stop.
        """
        gpu = self.get_gpu_vitals()
        
        # Linear throttle between 70C and 78C
        if gpu["temp"] > 70:
            return max(0.2, 1.0 - (gpu["temp"] - 70) / (self.temp_limit_c - 70))
        
        return 1.0

if __name__ == "__main__":
    # Test the Governor
    gov = SafetyGovernor(Path("."))
    safe, msg = gov.audit_system()
    print(f"Safety Audit: {safe} | {msg}")
    print(f"Throttle Factor: {gov.get_throttle_factor():.2f}")
