import argparse
from pathlib import Path


def slugify(text):
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")


def render_python(steps):
    lines = ["import argparse", "", "", "def main():", "    parser = argparse.ArgumentParser()", "    args = parser.parse_args()", ""]
    for idx, step in enumerate(steps, 1):
        slug = slugify(step) or f"step_{idx:02d}"
        lines.append(f"    # Step {idx}: {step}")
        lines.append(f"    {slug}()")
        lines.append("")
    for idx, step in enumerate(steps, 1):
        slug = slugify(step) or f"step_{idx:02d}"
        lines.append(f"def {slug}():")
        lines.append(f"    \"\"\"{step}\"\"\"")
        lines.append("    # TODO: implement")
        lines.append("    pass")
        lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    main()")
    return "\n".join(lines) + "\n"


def render_ps1(steps):
    lines = ["param()", ""]
    for idx, step in enumerate(steps, 1):
        name = slugify(step) or f"step_{idx:02d}"
        lines.append(f"function {name} {{")
        lines.append(f"    # {step}")
        lines.append("    # TODO: implement")
        lines.append("}")
        lines.append("")
    for idx, step in enumerate(steps, 1):
        name = slugify(step) or f"step_{idx:02d}"
        lines.append(f"{name}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate a script template from steps")
    parser.add_argument("--steps", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--lang", choices=["python", "powershell"], default="python")
    args = parser.parse_args()

    steps = [line.strip() for line in Path(args.steps).read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.lang == "python":
        content = render_python(steps)
    else:
        content = render_ps1(steps)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
