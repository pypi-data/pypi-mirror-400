
import os
import json
import time
import zipfile
import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime
import io

class DenseStateArchiver:
    """
    High-frequency archiver for Dense-State images.
    Streams mathematical snapshots to ZIP archives on the 2TB ground.
    """
    
    def __init__(self, repo_root: Path, session_id: str):
        self.repo_root = repo_root
        self.session_id = session_id
        self.archive_dir = repo_root / "data" / "dense_states" / session_id
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Significance Filter State
        self.last_energy = 0.0
        self.significance_threshold = 0.01 # Lowered from 0.05 for higher sensitivity
        
        # SQLite Index for fast lookup
        self.index_db = self.archive_dir / "state_index.db"
        self._init_index()
        
        # Buffer to avoid SSD thrashing
        self.buffer = []
        self.buffer_size_limit = 50 
        
        # Current active ZIP file
        self.current_zip_path = self.archive_dir / f"batch_{int(time.time())}.zip"

    def _init_index(self):
        """Initialize SQLite Index for fast lookup."""
        with sqlite3.connect(self.index_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS state_images (
                    id INTEGER PRIMARY KEY,
                    timestamp REAL,
                    state_type TEXT,
                    zip_file TEXT,
                    internal_path TEXT,
                    energy_level REAL,
                    vector_hash TEXT
                )
            """)
            conn.commit()

    def archive_image(self, state_data: np.ndarray, state_type: str = "hamiltonian"):
        """
        Archive only if the state is 'significant' compared to the last one.
        """
        energy_level = float(np.mean(np.abs(state_data)))
        
        # CALCULATE SIGNIFICANCE (The Delta)
        delta = abs(energy_level - self.last_energy)
        if delta < self.significance_threshold:
            return # Skip - too similar to last state (Prevents Noise)
            
        self.last_energy = energy_level
        timestamp = time.time()
        # Create a unique path inside the zip
        internal_path = f"{state_type}_{timestamp:.4f}.npy"
        
        # Simplified vector hash for fast indexing
        vector_hash = str(hash(state_data.tobytes()))
        energy_level = float(np.mean(np.abs(state_data))) # Heuristic
        
        self.buffer.append({
            "timestamp": timestamp,
            "state_type": state_type,
            "data": state_data,
            "internal_path": internal_path,
            "energy_level": energy_level,
            "vector_hash": vector_hash
        })
        
        if len(self.buffer) >= self.buffer_size_limit:
            self._flush_buffer()

    def _flush_buffer(self):
        """
        Writes the buffer to the ZIP archive and updates the index.
        """
        if not self.buffer:
            return
            
        print(f"  [ARCHIVER] Flushing {len(self.buffer)} images to {self.current_zip_path.name}")
        
        with zipfile.ZipFile(self.current_zip_path, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
            with sqlite3.connect(self.index_db) as conn:
                for item in self.buffer:
                    # Convert numpy to bytes for storage
                    buf = io.BytesIO()
                    np.save(buf, item["data"])
                    zf.writestr(item["internal_path"], buf.getvalue())
                    
                    # Update Index
                    conn.execute("""
                        INSERT INTO state_images 
                        (timestamp, state_type, zip_file, internal_path, energy_level, vector_hash)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        item["timestamp"], item["state_type"], 
                        self.current_zip_path.name, item["internal_path"],
                        item["energy_level"], item["vector_hash"]
                    ))
                conn.commit()
        
        self.buffer = []
        
        # Rotate ZIP if it gets too large (> 100MB)
        if self.current_zip_path.stat().st_size > 100 * 1024 * 1024:
            self.current_zip_path = self.archive_dir / f"batch_{int(time.time())}.zip"

    def close(self):
        self._flush_buffer()

if __name__ == "__main__":
    # Test/Demo of Thread A
    root = Path(".")
    archiver = DenseStateArchiver(root, "test_session")
    
    print("Simulating 1,000 Dense-State transitions...")
    for _ in range(1000):
        dummy_state = np.random.rand(64, 64).astype(np.float32)
        archiver.archive_image(dummy_state)
        
    archiver.close()
    print("Archive complete. Check data/dense_states/test_session/")
