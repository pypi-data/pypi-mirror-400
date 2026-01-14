import re


def first_non_empty(lines):
    for line in lines:
        if line.strip():
            return line.strip()
    return ""


def check_answer(text: str):
    lines = text.strip().splitlines()
    first = first_non_empty(lines)
    if not first.startswith("Answer:"):
        return False, "Missing Answer: line"
    if not first[len("Answer:"):].strip():
        return False, "Answer: line is empty"

    for label in ("Why:", "Next:", "Questions:"):
        for line in lines:
            if line.strip().startswith(label):
                if not line.strip()[len(label):].strip():
                    return False, f"{label} line is empty"
    return True, "ok"


def main() -> int:
    good = """
Answer: Use the Dynamic Budget Orchestrator to scale token limits by prompt size and resources.
Why: It prevents over-allocation on constrained hardware while keeping answers coherent.
Next: Tell me your target model and budget profile.
""".strip()

    bad = """
Why: This misses the required structure.
Next:
""".strip()

    ok_good, msg_good = check_answer(good)
    ok_bad, msg_bad = check_answer(bad)

    print("good_sample=", "pass" if ok_good else f"fail ({msg_good})")
    print("bad_sample=", "pass" if ok_bad else f"fail ({msg_bad})")

    return 0 if ok_good and not ok_bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
