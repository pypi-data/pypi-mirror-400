from pathlib import Path

SOURCE_EXTS = {
    ".py", ".js", ".ts", ".html", ".css", ".json",
    ".md", ".yaml", ".yml", ".toml", ".ini", ".sh"
}

BINARY_EXTS = {
    ".exe", ".zip", ".tar", ".gz", ".whl", ".apk"
}

IGNORE_DIRS = {
    ".git", ".venv", "venv", "dist", "build",
    "__pycache__", ".egg-info"
}

def collect_files(root: Path, raw: bool):
    files = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(d in p.parts for d in IGNORE_DIRS):
            continue
        if p.suffix.lower() in BINARY_EXTS:
            continue
        if not raw and p.suffix.lower() not in SOURCE_EXTS:
            continue
        files.append(p)
    return files
