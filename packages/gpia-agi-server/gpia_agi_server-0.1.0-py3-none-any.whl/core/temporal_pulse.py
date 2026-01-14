
import time
import json
import socket
from pathlib import Path
from core.safety_governor import SafetyGovernor

class MasterPulse:
    """
    The Master Oscillator for the AGI Organism.
    Generates the synchronous HRz heartbeat.
    """
    def __init__(self, repo_root: Path, target_hrz: float = 10.0):
        self.repo_root = repo_root
        self.target_hrz = target_hrz
        self.governor = SafetyGovernor(repo_root)
        
        # Internal Clock State
        self.beat_count = 0
        self.start_time = time.time()
        self.last_beat_time = time.time()
        
        # Communication (UDP Broadcast for zero-latency)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.port = 50005 # Synchronous Pulse Port

    def emit_pulse(self):
        """Broadcasts the beat and manages alignment."""
        while True:
            # 1. SAFETY CHECK (The Governor)
            is_safe, msg = self.governor.audit_system()
            throttle = self.governor.get_throttle_factor()
            
            if not is_safe:
                print(f"  [PULSE] Emergency Slowdown: {msg}")
                time.sleep(2) # Cooldown pause
                continue
                
            # 2. CALCULATE DYNAMIC FREQUENCY
            # Target HRz * Throttle Factor (Slows down thoughts if GPU is hot)
            actual_hrz = self.target_hrz * throttle
            interval = 1.0 / actual_hrz
            
            # 3. THE BEAT
            now = time.time()
            if now - self.last_beat_time >= interval:
                self.beat_count += 1
                payload = {
                    "beat": self.beat_count,
                    "timestamp": now,
                    "hrz": actual_hrz,
                    "throttle": throttle
                }
                
                # Broadcast to the Swarm
                self.sock.sendto(json.dumps(payload).encode(), ('<broadcast>', self.port))
                
                # Feedback loop (Feeling Time)
                drift = (now - self.last_beat_time) - interval
                if drift > 0.05: # If lagging by more than 50ms
                    print(f"  [PULSE] Jitter Detected! Drift: {drift*1000:.1f}ms | Current HRz: {actual_hrz:.1f}")
                
                self.last_beat_time = now
                
                if self.beat_count % 100 == 0:
                    print(f"[PULSE] Beat {self.beat_count} | HRz: {actual_hrz:.1f} | Temp Safe")

            # Yield to OS
            time.sleep(0.001)

if __name__ == "__main__":
    pulse = MasterPulse(Path("."), target_hrz=10.0) # Start at 10Hz
    print("--- GENESIS PULSE INITIALIZED ---")
    print("Broadcasting to the 2TB Swarm...")
    try:
        pulse.emit_pulse()
    except KeyboardInterrupt:
        print("\n[PULSE] Heartbeat stopped safely.")
