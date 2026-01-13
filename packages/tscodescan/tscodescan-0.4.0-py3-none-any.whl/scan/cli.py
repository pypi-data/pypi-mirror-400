
import argparse
from pathlib import Path

from scan.warn import safe_call
from scan.tree import render_tree
from scan.summary import render_summary
from scan.diagnose import render_diagnose
from scan.collect import collect_files
from scan.artifact import write_artifact

def main():
    p = argparse.ArgumentParser("tsc")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("-i", nargs="?", const=True)
    p.add_argument("-r", action="store_true")
    args = p.parse_args()

    root = Path(args.path).resolve()
    repo = root.name

    tree = safe_call("tree", render_tree, root)
    summary = safe_call("summary", render_summary, root)
    diagnose = safe_call("diagnose", render_diagnose, root)

    results = {
        "tree": tree,
        "summary": summary,
        "diagnose": diagnose,
    }

    if not args.i:
        print(tree.output)
        print(summary.output)
        print("DIAGNOSE:")
        print(diagnose.output)
        return 0

    files = safe_call("collect", collect_files, root, args.r).output

    write_artifact(
        repo=repo,
        results=results,
        files=files,
        raw=args.r,
        idtag=None if args.i is True else args.i
    )

if __name__ == "__main__":
    main()
