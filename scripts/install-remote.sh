#!/usr/bin/env bash

set -euo pipefail

REPOSITORY="wenhaiz/daily-skills"
RAW_BASE_URL="https://raw.githubusercontent.com/${REPOSITORY}"
ARCHIVE_BASE_URL="https://codeload.github.com/${REPOSITORY}/tar.gz/refs/tags"

usage() {
  cat <<'EOF'
Install a released skill without cloning the repository.

Usage:
  install-remote.sh <skill> [options]

Options:
  --platform <codex|claude>  Installation target (default: codex)
  --version <version>        Install an exact SemVer version
  --dest <directory>         Override the installation directory
  --replace                  Back up and replace an existing installation
  -h, --help                 Show this help
EOF
}

fail() {
  printf 'ERROR %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

skill=""
platform="codex"
version=""
destination=""
replace=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform)
      [[ $# -ge 2 ]] || fail "--platform requires a value"
      platform="$2"
      shift 2
      ;;
    --version)
      [[ $# -ge 2 ]] || fail "--version requires a value"
      version="$2"
      shift 2
      ;;
    --dest)
      [[ $# -ge 2 ]] || fail "--dest requires a value"
      destination="$2"
      shift 2
      ;;
    --replace)
      replace=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      fail "unknown option: $1"
      ;;
    *)
      [[ -z "$skill" ]] || fail "only one skill can be installed at a time"
      skill="$1"
      shift
      ;;
  esac
done

[[ -n "$skill" ]] || {
  usage >&2
  exit 1
}
[[ "$skill" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || fail "invalid skill name: $skill"
[[ "$platform" == "codex" || "$platform" == "claude" ]] || fail "unsupported platform: $platform"
if [[ -n "$version" ]]; then
  [[ "$version" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]] || fail "invalid version: $version"
fi

require_command curl
require_command python3
require_command tar

if [[ -z "$destination" ]]; then
  if [[ "$platform" == "claude" ]]; then
    destination="${HOME}/.claude/skills"
  else
    destination="${CODEX_HOME:-${HOME}/.codex}/skills"
  fi
fi

target="$destination/$skill"
if [[ -e "$target" || -L "$target" ]]; then
  $replace || fail "target exists: $target; pass --replace to back it up and continue"
fi

work_directory="$(mktemp -d)"
staging_directory=""
cleanup() {
  rm -rf "$work_directory"
  if [[ -n "$staging_directory" ]]; then
    rm -rf "$staging_directory"
  fi
}
trap cleanup EXIT

if [[ -z "$version" ]]; then
  catalog="$work_directory/skills.json"
  curl -fsSL --retry 3 "${RAW_BASE_URL}/main/skills.json" -o "$catalog"
  version="$(python3 - "$catalog" "$skill" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as catalog_file:
    catalog = json.load(catalog_file)

config = catalog.get("skills", {}).get(sys.argv[2])
if not config:
    raise SystemExit(f"unknown skill: {sys.argv[2]}")
print(config["version"])
PY
)"
fi

tag="${skill}-v${version}"
archive="$work_directory/${tag}.tar.gz"
extracted="$work_directory/extracted"
mkdir -p "$extracted"

printf 'DOWNLOAD %s %s\n' "$skill" "$tag"
curl -fsSL --retry 3 "${ARCHIVE_BASE_URL}/${tag}" -o "$archive"
tar -xzf "$archive" -C "$extracted"

source_directory="$(find "$extracted" -type d -path "*/skills/${skill}" -print -quit)"
[[ -n "$source_directory" && -f "$source_directory/SKILL.md" ]] || fail "release does not contain a valid skill: $tag"

mkdir -p "$destination"
staging_directory="$(mktemp -d "${destination}/.${skill}.install.XXXXXX")"
staged_target="$staging_directory/$skill"
cp -R "$source_directory" "$staged_target"

backup=""
if [[ -e "$target" || -L "$target" ]]; then
  backup_root="$destination/.daily-skills-backups"
  mkdir -p "$backup_root"
  timestamp="$(date +%Y%m%d-%H%M%S)"
  backup="$backup_root/${skill}-${timestamp}"
  counter=1
  while [[ -e "$backup" || -L "$backup" ]]; do
    backup="$backup_root/${skill}-${timestamp}-${counter}"
    counter=$((counter + 1))
  done
  mv "$target" "$backup"
  printf 'BACKUP %s -> %s\n' "$target" "$backup"
fi

if ! mv "$staged_target" "$target"; then
  if [[ -n "$backup" && ! -e "$target" && ! -L "$target" ]]; then
    mv "$backup" "$target"
    printf 'RESTORE %s -> %s\n' "$backup" "$target"
  fi
  fail "could not install to: $target"
fi
rm -rf "$staging_directory"
staging_directory=""
printf 'INSTALL %s %s -> %s\n' "$skill" "$version" "$target"
