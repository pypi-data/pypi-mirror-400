from pathlib import Path
import os

IGNORE_DIRS = {
    ".git", ".venv", "venv", "dist", "build",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".egg-info"
}

def render_tree(root: Path) -> str:
    root = Path(root)
    lines = []

    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        level = len(Path(base).relative_to(root).parts)
        indent = "  " * level
        lines.append(f"{indent}{Path(base).name}/")
        for f in files:
            lines.append(f"{indent}  {f}")

    return "\n".join(lines)
