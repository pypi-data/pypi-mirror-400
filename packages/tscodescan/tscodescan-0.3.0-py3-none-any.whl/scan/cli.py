
def human_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            if unit == "B":
                return f"{num_bytes} {unit}"
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024

import os
from pathlib import Path
import argparse

# ==============================
# Utilities (ported from dirscan)
# ==============================
DEFAULT_IGNORE = {
    "__pycache__",
    ".git",
    "Scan",
    "dist",
    "build",
    "*.egg-info",
}

LANG_MAP = {
    ".py": "Python",
    ".php": "PHP",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".html": "HTML",
    ".css": "CSS",
    ".md": "Markdown",
}

def should_ignore(path):
    parts = path.split(os.sep)
    for p in parts:
        if p in DEFAULT_IGNORE:
            return True
    return False

def build_tree(root):
    root = Path(root).resolve()
    lines = []

    def walk(base, prefix=""):
        entries = sorted(base.iterdir(), key=lambda x: (x.is_file(), x.name))
        for i, p in enumerate(entries):
            if should_ignore(str(p)):
                continue
            connector = "└── " if i == len(entries) - 1 else "├── "
            lines.append(prefix + connector + p.name)
            if p.is_dir():
                extension = "    " if i == len(entries) - 1 else "│   "
                walk(p, prefix + extension)

    lines.append(".")
    walk(root)
    return "\n".join(lines)

def run_summary(root):
    root = Path(root)
    lang_count = {}
    md_headers = []

    for base, _, files in os.walk(root):
        for f in files:
            path = Path(base) / f
            if should_ignore(str(path)):
                continue
            ext = path.suffix
            if ext in LANG_MAP:
                lang = LANG_MAP[ext]
                lang_count[lang] = lang_count.get(lang, 0) + 1
            if ext == ".md":
                try:
                    for line in path.read_text(errors="ignore").splitlines():
                        if line.startswith("#"):
                            md_headers.append(line.lstrip("# ").strip())
                except:
                    pass

    total = sum(lang_count.values()) or 1

    out = []
    out.append("# =============================================")
    out.append("# TSCODESCAN SUMMARY")
    out.append("# =============================================\n")
    out.append("Identity:")
    if "Python" in lang_count:
        out.append("- Python Package")
    else:
        out.append("- Unknown Project Type")
    out.append("\nLanguage Composition:")
    for k, v in sorted(lang_count.items(), key=lambda x: -x[1]):
        pct = int((v / total) * 100)
        out.append(f"- {k:<10}: {v} files ({pct}%)")

    if md_headers:
        out.append("\nDocumentation Signals:")
        for h in md_headers:
            out.append(f"- {h}")

    return "\n".join(out)

def run_doctor(root):
    root = Path(root)
    out = []
    out.append("=== TSCODESCAN DOCTOR ===\n")

    if (root / ".git").exists():
        out.append("✔ Git repository detected")
    else:
        out.append("✖ Not a git repository")

    for d in ["Scan", ".git"]:
        if (root / d).exists():
            out.append(f"⚠ Noise: {d}")

    total_bytes = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    size_str = human_size(total_bytes)
    out.append(f"\nRepo size: {size_str}")
    return "\n".join(out)

def write_artifact(mode, repo, content, ident=None):
    base = Path.home() / "storage" / "downloads" / "Scan" / repo
    base.mkdir(parents=True, exist_ok=True)
    name = mode
    if ident:
        name = f"{name}-{ident}"
    out = base / f"{name}-{repo}.txt"
    out.write_text(content)
    print(f"[OK] Artifact created: {out}")

# ==============================
# Main
# ==============================
def main():
    p = argparse.ArgumentParser("tsc", description="repository artifact generator")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("-i", nargs="?", const=True, metavar="ID")
    p.add_argument("-d", action="store_true")

    args = p.parse_args()
    root = os.path.abspath(args.path)
    repo = os.path.basename(root)

    if args.d:
        report = run_doctor(root)
        if args.i is not None:
            ident = None if args.i is True else str(args.i)
            write_artifact("diagnose", repo, report, ident)
        else:
            print(report)
        return

    tree = build_tree(root)
    summary = run_summary(root)

    if args.i is not None:
        ident = None if args.i is True else str(args.i)
        content = f"REPOSITORY: {repo}\n\nTREE:\n{tree}\n\n{summary}"
        write_artifact("scan", repo, content, ident)
        return

    print(tree)
    print()
    print(summary)

if __name__ == "__main__":
    main()
