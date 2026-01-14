import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

DENSE_STATE_LOG = Path("logs/gpia_server_dense_state.jsonl")


def _read_latest_dense_state_for_capsule(log_path: Path, capsule_id: str, attempts: int = 4, delay: float = 0.5) -> Dict[str, Any]:
    """
    Try a few times to find the most recent dense-state entry matching the capsule_id.
    This mitigates races where the agent writes the log slightly after the run returns.
    """
    for _ in range(attempts):
        try:
            if log_path.exists():
                with log_path.open("rb") as handle:
                    handle.seek(0, 2)
                    pos = handle.tell()
                    buf = b""
                    while pos > 0:
                        pos -= 1
                        handle.seek(pos, 0)
                        ch = handle.read(1)
                        if ch == b"\n" and buf:
                            line = buf[::-1].decode("utf-8", errors="ignore")
                            buf = b""
                            try:
                                entry = json.loads(line)
                                if entry.get("capsule_id") == capsule_id:
                                    return entry
                            except Exception:
                                pass
                        else:
                            buf += ch
                    if buf:
                        line = buf[::-1].decode("utf-8", errors="ignore")
                        entry = json.loads(line)
                        if entry.get("capsule_id") == capsule_id:
                            return entry
        except Exception:
            pass
        time.sleep(delay)
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a task through the local GPIA agent.")
    parser.add_argument("--task", required=True, help="Task to execute via GPIA")
    parser.add_argument(
        "--mode",
        default="full",
        choices=["full", "quick", "analyze", "create"],
        help="Execution mode",
    )
    parser.add_argument(
        "--context",
        default=None,
        help="Optional JSON context to pass into GPIA (full mode only)",
    )
    parser.add_argument(
        "--context-file",
        default=None,
        help="Path to a JSON file to load as context (full mode only)",
    )
    parser.add_argument(
        "--dense-state",
        action="store_true",
        help="Inject latest dense-state snapshot (if available) into context/prompt.",
    )
    parser.add_argument(
        "--dense-state-log",
        default=str(DENSE_STATE_LOG),
        help="Path to dense-state jsonl log (default: logs/gpia_server_dense_state.jsonl).",
    )
    parser.add_argument(
        "--force-complete",
        action="store_true",
        help="Hint to the agent to return immediately after first successful response.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(repo_root))

    try:
        from gpia import GPIA
    except Exception as exc:
        print(f"Failed to import GPIA: {exc}", file=sys.stderr)
        return 1

    agent = GPIA(verbose=False)

    dense_state_context: Optional[Dict[str, Any]] = None
    if args.dense_state:
        log_path = Path(args.dense_state_log)
        if log_path.exists():
            try:
                # Read the last line safely
                last_line = None
                with log_path.open("rb") as handle:
                    handle.seek(0, 2)
                    pos = handle.tell()
                    while pos > 0:
                        pos -= 1
                        handle.seek(pos, 0)
                        if handle.read(1) == b"\n":
                            last_line = handle.readline().decode("utf-8", errors="ignore")
                            break
                    if last_line is None:
                        handle.seek(0)
                        last_line = handle.readline().decode("utf-8", errors="ignore")
                entry = json.loads(last_line) if last_line else {}
                dense_state_context = {
                    "dense_state": {
                        "timestamp": entry.get("timestamp"),
                        "session_id": entry.get("session_id"),
                        "model": entry.get("model"),
                        "resonance_hash": entry.get("resonance_hash"),
                        "token_count": entry.get("tokens"),
                        "prompt_snippet": entry.get("prompt_snippet"),
                    }
                }
            except Exception:
                dense_state_context = {"dense_state": {"error": "unavailable"}}
        else:
            dense_state_context = {"dense_state": {"error": "log_not_found"}}

    if args.mode == "quick":
        if dense_state_context:
            prompt = f"[DENSE_STATE:{json.dumps(dense_state_context)}]\n{args.task}"
        else:
            prompt = args.task
        response = agent.quick(prompt)
        payload = {"mode": args.mode, "response": response}
    elif args.mode == "analyze":
        if dense_state_context:
            prompt = f"[DENSE_STATE:{json.dumps(dense_state_context)}]\n{args.task}"
        else:
            prompt = args.task
        response = agent.analyze(prompt)
        payload = {"mode": args.mode, "response": response}
    elif args.mode == "create":
        if dense_state_context:
            prompt = f"[DENSE_STATE:{json.dumps(dense_state_context)}]\n{args.task}"
        else:
            prompt = args.task
        response = agent.create(prompt)
        payload = {"mode": args.mode, "response": response}
    else:
        context = {}
        if args.context_file:
            try:
                context = json.loads(Path(args.context_file).read_text(encoding="utf-8"))
            except Exception as exc:
                print(f"Invalid --context-file JSON: {exc}", file=sys.stderr)
                return 1
        elif args.context:
            try:
                context = json.loads(args.context)
            except json.JSONDecodeError as exc:
                print(f"Invalid --context JSON: {exc}", file=sys.stderr)
                return 1
        if dense_state_context:
            context.update(dense_state_context)
        if args.force_complete:
            context["force_complete"] = True
        # Simple prediction: estimate tokens from task length and a nominal speed of 1 tok/s.
        predicted_tokens = max(8, int(len(args.task.split()) * 1.5))
        predicted_time = float(predicted_tokens)
        start = time.time()
        result = agent.run(args.task, context=context)
        elapsed = time.time() - start
        # Try to pull the latest dense-state entry for this capsule to report actual tokens/resonance.
        entry = _read_latest_dense_state_for_capsule(Path(args.dense_state_log), result.capsule_id)
        actual_tokens = entry.get("tokens")
        resonance_score = entry.get("resonance_score")
        resonance_hash = entry.get("resonance_hash")
        perf_tag = {
            "predicted_tokens": predicted_tokens,
            "predicted_time_s": round(predicted_time, 2),
            "actual_tokens": actual_tokens,
            "actual_time_s": round(elapsed, 2),
            "speed_tok_s": None if actual_tokens is None else round(actual_tokens / max(elapsed, 1e-6), 2),
            "resonance_score": resonance_score,
            "resonance_hash": resonance_hash,
        }
        payload = {
            "mode": args.mode,
            "success": result.success,
            "response": result.response,
            "capsule_id": result.capsule_id,
            "pass_count": result.pass_count,
            "assist_count": result.assist_count,
            "skills_used": result.skills_used,
            "execution_time": result.execution_time,
            "perf_tag": perf_tag,
        }

    print(json.dumps(payload, indent=2, ensure_ascii=True))
    # Also emit a compact tag for easy scanning.
    if "perf_tag" in payload:
        pt = payload["perf_tag"]
        tag = (
            f"[pred_tokens={pt['predicted_tokens']}"
            f" pred_time={pt['predicted_time_s']}s"
            f" actual_tokens={pt.get('actual_tokens')}"
            f" actual_time={pt['actual_time_s']}s"
            f" speed={pt.get('speed_tok_s')} tok/s"
            f" resonance={pt.get('resonance_score')}]"
        )
        print(tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
