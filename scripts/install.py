#!/usr/bin/env python3

import argparse
import json
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_skill(name: str) -> Path:
    catalog = json.loads((ROOT / "skills.json").read_text(encoding="utf-8"))
    config = catalog.get("skills", {}).get(name)
    if not config:
        raise ValueError(f"unknown skill: {name}")
    source = (ROOT / config["path"]).resolve()
    if not (source / "SKILL.md").is_file():
        raise ValueError(f"invalid skill source: {source}")
    return source


def backup_existing(target: Path) -> Path:
    backup_root = target.parent / ".daily-skills-backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_root / f"{target.name}-{timestamp}"
    counter = 1
    while backup.exists() or backup.is_symlink():
        backup = backup_root / f"{target.name}-{timestamp}-{counter}"
        counter += 1
    shutil.move(str(target), str(backup))
    return backup


def install(name: str, mode: str, destination: Path, replace: bool) -> None:
    source = load_skill(name)
    target = destination / name
    destination.mkdir(parents=True, exist_ok=True)

    if target.is_symlink() and target.resolve() == source:
        print(f"ALREADY_INSTALLED {target} -> {source}")
        return

    if target.exists() or target.is_symlink():
        if not replace:
            raise ValueError(f"target exists: {target}; pass --replace to back it up and continue")

    temporary = destination / f".{name}.install-{uuid.uuid4().hex[:8]}"
    backup = None
    try:
        if mode == "symlink":
            temporary.symlink_to(source, target_is_directory=True)
        else:
            shutil.copytree(source, temporary)

        if target.exists() or target.is_symlink():
            backup = backup_existing(target)
            print(f"BACKUP {target} -> {backup}")

        temporary.rename(target)
    except OSError:
        if temporary.is_symlink() or temporary.is_file():
            temporary.unlink(missing_ok=True)
        elif temporary.exists():
            shutil.rmtree(temporary)
        if backup is not None and not target.exists() and not target.is_symlink():
            shutil.move(str(backup), str(target))
            print(f"RESTORE {backup} -> {target}")
        raise

    if mode == "symlink":
        print(f"LINK {target} -> {source}")
    else:
        print(f"COPY {source} -> {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install a skill managed by daily-skills.")
    parser.add_argument("skill")
    parser.add_argument("--mode", choices=("symlink", "copy"), default="symlink")
    parser.add_argument("--dest", default=str(Path.home() / ".codex/skills"))
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    try:
        install(args.skill, args.mode, Path(args.dest).expanduser().resolve(), args.replace)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
