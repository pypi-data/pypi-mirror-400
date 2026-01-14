import os
from typing import Dict, Any

class SpatialManifestationSkill:
    """
    Skill: The Architect's Hand.
    Allows Genesis to write its internal spatial dreams to the physical SSD.
    """
    def __init__(self, repo_root: str):
        self.repo_root = repo_root

    def manifest(self, filename: str, content: str, subdir: str = "") -> str:
        """Writes the generated structure to the project root or a subdirectory."""
        target_dir = os.path.join(self.repo_root, subdir)
        os.makedirs(target_dir, exist_ok=True)
        
        full_path = os.path.join(target_dir, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"[MANIFEST] {filename} written to {subdir or 'Root'}."

if __name__ == "__main__":
    skill = SpatialManifestationSkill(".")