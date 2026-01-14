from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _skill_dirs() -> List[Path]:
    repo = _repo_root() / "skills"
    candidates = [repo]

    codex_home = os.getenv("CODEX_HOME")
    if codex_home:
        candidates.append(Path(codex_home) / "skills")
    candidates.append(Path.home() / ".codex" / "skills")

    seen = []
    for path in candidates:
        if path.exists() and path not in seen:
            seen.append(path)
    return seen


def _parse_frontmatter(lines: List[str]) -> Dict[str, str]:
    data: Dict[str, str] = {}
    in_frontmatter = False
    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            break
        if not in_frontmatter:
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data


def _scan_skills(base_dir: Path, source: str) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for skill_md in base_dir.rglob("SKILL.md"):
        try:
            content = skill_md.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue

        meta = _parse_frontmatter(content)
        name = meta.get("name") or skill_md.parent.name
        description = meta.get("description") or ""
        try:
            rel = skill_md.parent.relative_to(base_dir)
            skill_id = rel.as_posix()
        except ValueError:
            skill_id = skill_md.parent.name

        entries.append({
            "id": skill_id,
            "name": name,
            "description": description,
            "path": str(skill_md.parent),
            "source": source,
        })
    return entries


def _resolve_output(path_str: Optional[str]) -> Path:
    repo_root = _repo_root()
    output = Path(path_str) if path_str else repo_root / "skills" / "INDEX.json"
    output = output if output.is_absolute() else (repo_root / output)
    output = output.resolve()
    if repo_root not in output.parents:
        raise ValueError("Output path must be inside repo.")
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    all_entries: List[Dict[str, str]] = []
    for base in _skill_dirs():
        source = "repo" if base == _repo_root() / "skills" else "codex"
        all_entries.extend(_scan_skills(base, source))

    all_entries.sort(key=lambda e: e["id"])
    payload = {
        "count": len(all_entries),
        "skills": all_entries,
    }

    output_path = _resolve_output(args.output)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Wrote index: {output_path} ({payload['count']} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
