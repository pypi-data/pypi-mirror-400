from pathlib import Path
from collections import Counter

SOURCE_EXTS = {
    ".py", ".js", ".ts", ".html", ".css",
    ".json", ".md", ".yaml", ".yml", ".toml"
}

def render_summary(root: Path) -> str:
    root = Path(root)
    counter = Counter()
    total = 0

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in SOURCE_EXTS:
            counter[p.suffix.lower()] += 1
            total += 1

    out = []
    out.append("# =============================================")
    out.append("# TSCODESCAN SUMMARY")
    out.append("# =============================================\n")

    out.append("Repository Profile:")
    out.append("- Type        : CLI Tool")
    out.append("- Language    : Python")
    out.append("- Packaging   : setuptools")
    out.append("- Entry Point : console_script\n")

    out.append("Primary Capability:")
    out.append("- Scans repository structure")
    out.append("- Extracts source code files")
    out.append("- Generates deterministic text artifacts\n")

    out.append("Repository Characteristics:")
    out.append("- File-based (no runtime service)")
    out.append("- No external dependencies required")
    out.append("- Deterministic output\n")

    out.append("Language Composition:")
    for ext, cnt in counter.most_common():
        pct = int(cnt / total * 100) if total else 0
        label = "Python" if ext == ".py" else ext.replace(".", "").title()
        out.append(f"- {label:<10}: {pct}%")

    return "\n".join(out)
