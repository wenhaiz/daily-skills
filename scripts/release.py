#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=ROOT, check=check, capture_output=True, text=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a version tag for one skill.")
    parser.add_argument("skill")
    parser.add_argument("--push", action="store_true", help="Push the new tag to origin.")
    args = parser.parse_args()

    try:
        catalog = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
        config = catalog.get("skills", {}).get(args.skill)
        if not config:
            raise ValueError(f"unknown skill: {args.skill}")

        tag = f"{args.skill}-v{config['version']}"
        subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate.py"), "--tag", tag],
            cwd=ROOT,
            check=True,
        )
        if run("git", "status", "--porcelain").stdout.strip():
            raise ValueError("working tree is not clean")

        if run("git", "rev-parse", "--verify", tag, check=False).returncode == 0:
            raise ValueError(f"tag already exists: {tag}")

        run("git", "tag", "-a", tag, "-m", f"Release {tag}")
        print(f"TAG {tag}")
        if args.push:
            run("git", "push", "origin", tag)
            print(f"PUSH {tag}")
    except (OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
