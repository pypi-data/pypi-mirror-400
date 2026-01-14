import argparse
import json
import re
from pathlib import Path


def load_rules(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_input(path):
    if path:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    return ""


def main():
    parser = argparse.ArgumentParser(description="Verify output with deterministic rules")
    parser.add_argument("--input")
    parser.add_argument("--rules", required=True)
    parser.add_argument("--output", default="runs/verification_report.json")
    args = parser.parse_args()

    text = read_input(args.input)
    rules = load_rules(args.rules)

    checks = []
    ok = True

    for item in rules.get("must_contain", []):
        passed = item in text
        checks.append({"rule": f"must_contain:{item}", "pass": passed})
        ok = ok and passed

    for item in rules.get("must_not_contain", []):
        passed = item not in text
        checks.append({"rule": f"must_not_contain:{item}", "pass": passed})
        ok = ok and passed

    for pattern in rules.get("regex", []):
        passed = re.search(pattern, text) is not None
        checks.append({"rule": f"regex:{pattern}", "pass": passed})
        ok = ok and passed

    min_len = rules.get("min_len")
    max_len = rules.get("max_len")
    if min_len is not None:
        passed = len(text) >= int(min_len)
        checks.append({"rule": f"min_len:{min_len}", "pass": passed})
        ok = ok and passed
    if max_len is not None:
        passed = len(text) <= int(max_len)
        checks.append({"rule": f"max_len:{max_len}", "pass": passed})
        ok = ok and passed

    report = {"ok": ok, "checks": checks}
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
