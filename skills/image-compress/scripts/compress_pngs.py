#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CACHE_FILE_NAME = ".image-compress-cache.json"
DEFAULT_LOSSY_ABOVE_BYTES = 256 * 1024


@dataclass
class FileRecord:
    mtime_ns: int
    size: int
    sha256: str
    mode: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compress PNG files with oxipng first and optional pngquant fallback.",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="PNG files or directories to scan.",
    )
    parser.add_argument(
        "--allow-lossy",
        action="store_true",
        help="Allow pngquant fallback for files that remain large after oxipng.",
    )
    parser.add_argument(
        "--lossy-above-bytes",
        type=int,
        default=DEFAULT_LOSSY_ABOVE_BYTES,
        help="Only try pngquant when the PNG is still at or above this size after oxipng.",
    )
    parser.add_argument(
        "--cache-file",
        help="Override the cache manifest path. Default: <scan-root>/.image-compress-cache.json",
    )
    return parser.parse_args()


def require_command(name: str) -> None:
    if shutil.which(name):
        return
    print(f"Missing required command: {name}", file=sys.stderr)
    sys.exit(2)


def iter_png_files(paths: list[str]) -> list[Path]:
    files: set[Path] = set()
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.exists():
            print(f"Skip missing path: {path}", file=sys.stderr)
            continue
        if path.is_file():
            if path.suffix.lower() == ".png":
                files.add(path)
            continue
        for child in path.rglob("*"):
            if child.is_file() and child.suffix.lower() == ".png":
                files.add(child.resolve())
    return sorted(files)


def common_root(files: Iterable[Path]) -> Path:
    file_list = [str(path.parent) for path in files]
    if not file_list:
        return Path.cwd()
    return Path(os.path.commonpath(file_list))


def default_cache_path(files: list[Path]) -> Path:
    return common_root(files) / CACHE_FILE_NAME


def load_cache(path: Path) -> dict[str, dict[str, object]]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def save_cache(path: Path, cache: dict[str, dict[str, object]]) -> None:
    path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n")


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stat_record(path: Path) -> tuple[int, int]:
    stat = path.stat()
    return stat.st_mtime_ns, stat.st_size


def relative_key(path: Path, scan_root: Path) -> str:
    try:
        return str(path.relative_to(scan_root))
    except ValueError:
        return str(path)


def should_skip(path: Path, scan_root: Path, cache: dict[str, dict[str, object]]) -> bool:
    key = relative_key(path, scan_root)
    cached = cache.get(key)
    if not cached:
        return False

    current_mtime_ns, current_size = stat_record(path)
    if cached.get("mtime_ns") == current_mtime_ns and cached.get("size") == current_size:
        return True

    current_sha = sha256_of(path)
    if cached.get("sha256") != current_sha:
        return False

    cache[key] = {
        "mtime_ns": current_mtime_ns,
        "size": current_size,
        "sha256": current_sha,
        "mode": cached.get("mode", "unknown"),
    }
    return True


def update_cache(path: Path, scan_root: Path, cache: dict[str, dict[str, object]], mode: str) -> None:
    mtime_ns, size = stat_record(path)
    cache[relative_key(path, scan_root)] = {
        "mtime_ns": mtime_ns,
        "size": size,
        "sha256": sha256_of(path),
        "mode": mode,
    }


def run_command(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        message = stderr or stdout or "unknown command failure"
        raise RuntimeError(message)


def run_oxipng(path: Path) -> bool:
    before = path.stat().st_size
    run_command(["oxipng", "-o", "4", str(path)])
    after = path.stat().st_size
    return after < before


def run_pngquant(path: Path) -> bool:
    before = path.stat().st_size
    result = subprocess.run(
        [
            "pngquant",
            "--quality=80-95",
            "--skip-if-larger",
            "--force",
            "--ext",
            ".png",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode in {0, 98, 99}:
        after = path.stat().st_size
        return after < before
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()
    message = stderr or stdout or "unknown command failure"
    raise RuntimeError(message)


def main() -> int:
    args = parse_args()
    require_command("oxipng")
    if args.allow_lossy:
        require_command("pngquant")

    files = iter_png_files(args.paths)
    if not files:
        print("No PNG files found.")
        return 0

    scan_root = common_root(files)
    cache_path = Path(args.cache_file).expanduser().resolve() if args.cache_file else default_cache_path(files)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache = load_cache(cache_path)

    summary = {
        "scanned": len(files),
        "skipped_cached": 0,
        "lossless_changed": 0,
        "lossy_changed": 0,
        "no_gain": 0,
        "failed": 0,
    }
    failed_files: list[str] = []

    for path in files:
        if should_skip(path, scan_root, cache):
            summary["skipped_cached"] += 1
            continue

        mode = "lossless-no-gain"
        try:
            lossless_changed = run_oxipng(path)
            if lossless_changed:
                summary["lossless_changed"] += 1
                mode = "lossless"

            if args.allow_lossy and path.stat().st_size >= args.lossy_above_bytes:
                lossy_changed = run_pngquant(path)
                if lossy_changed:
                    summary["lossy_changed"] += 1
                    mode = "lossy"
            if mode == "lossless-no-gain":
                summary["no_gain"] += 1

            update_cache(path, scan_root, cache, mode)
        except Exception as exc:  # noqa: BLE001
            summary["failed"] += 1
            failed_files.append(f"{path}: {exc}")

    save_cache(cache_path, cache)

    print(json.dumps({"cache_file": str(cache_path), "summary": summary, "failed_files": failed_files}, indent=2))
    return 1 if failed_files else 0


if __name__ == "__main__":
    raise SystemExit(main())
