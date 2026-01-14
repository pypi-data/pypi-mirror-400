#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    source = Path(__file__).resolve().parent / "heuristics_registry.py"
    destination = repo_root / "core" / "sovereignty_v2" / "heuristics_registry.py"

    if args.dry_run:
        print(f"Would copy {source} -> {destination}")
        return 0

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    print(f"Installed heuristics registry: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

