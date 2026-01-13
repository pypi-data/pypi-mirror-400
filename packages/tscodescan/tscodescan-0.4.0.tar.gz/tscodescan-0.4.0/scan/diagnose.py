from pathlib import Path

def render_diagnose(root: Path) -> str:
    out = []
    root = Path(root)

    if (root / ".git").exists():
        out.append("OK Git repository detected")
    else:
        out.append("WARN Not a git repository")

    for d in ["build", "dist", ".git", ".venv"]:
        if (root / d).exists():
            out.append(f"WARN Noise: {d}")

    size = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    out.append(f"Repo size: {size / 1024:.1f} KB")

    return "\n".join(out)
