
from pathlib import Path
import datetime

def write_artifact(repo, results, files, raw=False, idtag=None):
    outdir = Path.home() / "storage" / "downloads" / "Scan" / repo
    outdir.mkdir(parents=True, exist_ok=True)

    name = "scan"
    if raw:
        name += "-raw"
    if idtag:
        name += f"-{idtag}"
    name += f"-{repo}.txt"

    out = outdir / name

    with out.open("w", errors="ignore") as f:
        f.write("=" * 40 + "\n")
        f.write(f"ARTIFACT: {repo}\n")
        f.write(f"GENERATED: {datetime.datetime.now()}\n")
        f.write("=" * 40 + "\n\n")

        for key, res in results.items():
            f.write(key.upper() + "\n")
            f.write("-" * len(key) + "\n")
            f.write(res.output + "\n\n")

            if not res.ok:
                f.write("ERROR TRACE\n")
                f.write("-----------\n")
                f.write(res.error + "\n\n")

        f.write("CONTEXT (SOURCE)\n")
        f.write("----------------\n")
        for p in files:
            f.write(f"\n=== {p.relative_to(Path.cwd())} ===\n")
            try:
                f.write(p.read_text(errors="ignore"))
            except:
                f.write("[READ ERROR]\n")

    print(f"[OK] Artifact created: {out}")
