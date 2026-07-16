#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "skills.json"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def fail(message: str) -> None:
    raise ValueError(message)


def load_catalog() -> dict:
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot read {CATALOG}: {error}")
    if data.get("schema_version") != 1:
        fail("skills.json schema_version must be 1")
    if not isinstance(data.get("skills"), dict) or not data["skills"]:
        fail("skills.json must contain at least one skill")
    return data


def read_frontmatter(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(content)
    if not match:
        fail(f"invalid frontmatter: {path}")
    result = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if ":" not in line or line.startswith((" ", "\t")):
            fail(f"unsupported frontmatter line in {path}: {line}")
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def validate_python(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    compile(source, str(path), "exec")


def validate_shell(path: Path) -> None:
    result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"invalid shell script {path}: {result.stderr.strip()}")


def validate_openai_yaml(path: Path, name: str) -> None:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines or lines[0] != "interface:":
        fail(f"missing interface mapping: {path}")

    values = {}
    for line in lines[1:]:
        match = re.fullmatch(r'  ([a-z_]+):\s+"([^"\\\n]+)"', line)
        if not match:
            fail(f"invalid agents/openai.yaml line: {path}: {line}")
        key, value = match.groups()
        if key in values:
            fail(f"duplicate interface.{key}: {path}")
        values[key] = value

    required = {"display_name", "short_description", "default_prompt"}
    if set(values) != required:
        fail(f"agents/openai.yaml must contain exactly {sorted(required)}: {path}")

    if not 25 <= len(values["short_description"]) <= 64:
        fail(f"interface.short_description must contain 25-64 characters: {path}")
    if f"${name}" not in values["default_prompt"]:
        fail(f"interface.default_prompt must mention ${name}: {path}")


def validate_skill(name: str, config: dict) -> None:
    if not SKILL_NAME.fullmatch(name):
        fail(f"invalid skill name: {name}")
    version = config.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        fail(f"invalid version for {name}: {version}")

    relative_path = config.get("path")
    expected_path = f"skills/{name}"
    if relative_path != expected_path:
        fail(f"{name} path must be {expected_path}")

    directory = ROOT / relative_path
    skill_md = directory / "SKILL.md"
    if not skill_md.is_file():
        fail(f"missing SKILL.md for {name}")

    frontmatter = read_frontmatter(skill_md)
    if frontmatter.get("name") != name:
        fail(f"SKILL.md name does not match directory: {name}")
    if not frontmatter.get("description"):
        fail(f"SKILL.md description is missing: {name}")
    openai_yaml = directory / "agents/openai.yaml"
    if not openai_yaml.is_file():
        fail(f"missing agents/openai.yaml for {name}")
    validate_openai_yaml(openai_yaml, name)

    for forbidden in ("README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md"):
        if (directory / forbidden).exists():
            fail(f"repository documentation must not be inside a skill: {directory / forbidden}")

    for path in directory.rglob("*.py"):
        validate_python(path)
    for path in directory.rglob("*.sh"):
        validate_shell(path)

    print(f"OK {name} {version}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate all skills and an optional release tag.")
    parser.add_argument("--tag", help="Require an exact <skill>-v<version> tag from skills.json.")
    args = parser.parse_args()

    try:
        catalog = load_catalog()
        catalog_names = set(catalog["skills"])
        directory_names = {
            path.name
            for path in (ROOT / "skills").iterdir()
            if path.is_dir() and not path.name.startswith(".")
        }
        if directory_names != catalog_names:
            missing = sorted(directory_names - catalog_names)
            absent = sorted(catalog_names - directory_names)
            fail(f"skills.json mismatch: unregistered={missing}, missing_directories={absent}")

        for name, config in sorted(catalog["skills"].items()):
            validate_skill(name, config)

        if args.tag:
            expected_tags = {
                f"{name}-v{config['version']}"
                for name, config in catalog["skills"].items()
            }
            if args.tag not in expected_tags:
                fail(f"release tag does not match skills.json: {args.tag}")
            print(f"OK release tag {args.tag}")
    except ValueError as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
