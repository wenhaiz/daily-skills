#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path


CURRENT_CONTRACT_VERSION = 2
MANIFEST_PATH = Path("Docs/.project-docs.json")

SCAFFOLD = {
    "docs-root.md": Path("Docs/README.md"),
    "product-fact-root.md": Path("Docs/0-ProductFact/README.md"),
    "domain-fact-template.md": Path("Docs/0-ProductFact/90-templates/domain-fact-template.md"),
    "plans-root.md": Path("Docs/1-Plans/README.md"),
    "plans-archive-root.md": Path("Docs/1-Plans/archived/README.md"),
    "ideas-root.md": Path("Docs/2-Ideas/README.md"),
    "changelog-root.md": Path("Docs/3-Changelog/README.md"),
    "product-fact-check.sh": Path("Docs/0-ProductFact/check.sh"),
}


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def repository_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"repository root does not exist: {root}")
    return root


def read_manifest(root: Path):
    path = root / MANIFEST_PATH
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError(f"cannot read manifest {path}: {error}") from error


def inspect(root: Path) -> int:
    manifest = read_manifest(root)
    manifest_paths = manifest.get("paths", {}) if manifest else {}
    product_fact_path = Path(manifest_paths.get("product_fact", "Docs/0-ProductFact"))
    if not (root / product_fact_path).exists() and (root / "docs/product-fact").exists():
        product_fact_path = Path("docs/product-fact")
    plans_path = Path(manifest_paths.get("plans", "Docs/1-Plans"))
    plans_archive_path = Path(manifest_paths.get("plans_archive", plans_path / "archived"))
    fact_check_path = root / product_fact_path / "check.sh"
    legacy_fact_check_path = root / "scripts/product_fact/check.sh"
    if not fact_check_path.exists() and legacy_fact_check_path.exists():
        fact_check_path = legacy_fact_check_path
    known_paths = {
        "docs": root / "Docs",
        "product_fact": root / product_fact_path,
        "plans": root / plans_path,
        "plans_archive": root / plans_archive_path,
        "ideas": root / "Docs/2-Ideas",
        "changelog": root / "Docs/3-Changelog",
        "fact_check": fact_check_path,
    }
    result = {
        "root": str(root),
        "git_repository": (root / ".git").exists(),
        "current_contract_version": CURRENT_CONTRACT_VERSION,
        "manifest": manifest,
        "paths": {name: path.exists() for name, path in known_paths.items()},
    }
    if manifest:
        recorded = manifest.get("contract_version", 0)
        result["upgrade_required"] = recorded < CURRENT_CONTRACT_VERSION
    else:
        result["upgrade_required"] = None
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def render_asset(name: str, project_name: str) -> str:
    path = skill_root() / "assets" / name
    return path.read_text(encoding="utf-8").replace("{{PROJECT_NAME}}", project_name)


def baseline_manifest(project_name: str):
    return {
        "skill": "project-docs-manager",
        "contract_version": 0,
        "target_contract_version": CURRENT_CONTRACT_VERSION,
        "applied_migrations": [],
        "project_name": project_name,
        "paths": {
            "entrypoint": "Docs/README.md",
            "product_fact": "Docs/0-ProductFact",
            "plans": "Docs/1-Plans",
            "plans_archive": "Docs/1-Plans/archived",
            "ideas": "Docs/2-Ideas",
            "changelog": "Docs/3-Changelog",
        },
    }


def initialize(root: Path, project_name: str, apply: bool) -> int:
    actions = []
    conflicts = []

    for asset_name, relative_path in SCAFFOLD.items():
        target = root / relative_path
        if target.exists():
            conflicts.append(str(relative_path))
        else:
            actions.append((asset_name, relative_path))

    manifest_target = root / MANIFEST_PATH
    if manifest_target.exists():
        conflicts.append(str(MANIFEST_PATH))
    else:
        actions.append((None, MANIFEST_PATH))

    print("mode:", "apply" if apply else "preview")
    for _, path in actions:
        print("CREATE", path)
    for path in conflicts:
        print("KEEP  ", path)

    if not apply:
        return 0

    for asset_name, relative_path in actions:
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if asset_name is None:
            content = json.dumps(baseline_manifest(project_name), ensure_ascii=False, indent=2) + "\n"
        else:
            content = render_asset(asset_name, project_name)
        target.write_text(content, encoding="utf-8")
        if target.suffix == ".sh":
            target.chmod(target.stat().st_mode | 0o111)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect or initialize a project documentation lifecycle.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect without modifying files.")
    inspect_parser.add_argument("--root", default=".", help="Repository root.")

    init_parser = subparsers.add_parser("init", help="Preview or create missing baseline files.")
    init_parser.add_argument("--root", default=".", help="Repository root.")
    init_parser.add_argument("--project-name", required=True, help="Human-readable project name.")
    init_parser.add_argument("--apply", action="store_true", help="Create missing files. Existing files are kept.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        root = repository_root(args.root)
        if args.command == "inspect":
            return inspect(root)
        return initialize(root, args.project_name, args.apply)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
