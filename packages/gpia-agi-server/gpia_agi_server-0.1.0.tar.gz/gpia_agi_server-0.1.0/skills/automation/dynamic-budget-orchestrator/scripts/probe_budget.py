import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.dynamic_budget_orchestrator import compute_budget


def make_prompt(chars: int) -> str:
    return "x" * chars


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe dynamic token budgets")
    parser.add_argument("--model", default="qwen3:latest")
    parser.add_argument("--requested", type=int, default=800)
    parser.add_argument("--short", type=int, default=200)
    parser.add_argument("--long", type=int, default=2400)
    args = parser.parse_args()

    prompts = [
        ("short", make_prompt(args.short)),
        ("long", make_prompt(args.long)),
    ]

    profiles = ["safe", "fast", "balanced", "quality"]

    print("Dynamic Budget Probe")
    print("model=", args.model)
    print("requested=", args.requested)
    print("")

    snapshot = None
    for profile in profiles:
        for label, prompt in prompts:
            budget, details = compute_budget(
                prompt,
                args.requested,
                model_id=args.model,
                profile=profile,
            )
            snapshot = details.get("resource_snapshot")
            print(
                "profile={profile:<8} prompt={label:<5} tokens={budget:<5} "
                "prompt_cap={prompt_cap:<5} resource_cap={resource_cap}".format(
                    profile=profile,
                    label=label,
                    budget=budget,
                    prompt_cap=details.get("prompt_cap"),
                    resource_cap=details.get("resource_cap"),
                )
            )
        print("")

    if snapshot:
        print("resource_snapshot=")
        print(json.dumps(snapshot, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
