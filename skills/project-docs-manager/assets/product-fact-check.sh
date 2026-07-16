#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
fact_root="$repo_root/Docs/0-ProductFact/10-domains"
current_head="$(git -C "$repo_root" rev-parse HEAD)"
exit_code=0
domain_count=0

if [[ ! -d "$fact_root" ]]; then
    echo "MISSING_DOMAIN $fact_root"
    exit 1
fi

while IFS= read -r doc; do
    domain_count=$((domain_count + 1))
    verified_commit="$(sed -n 's/^verified_commit: //p' "$doc" | head -n 1)"
    if [[ -z "$verified_commit" ]]; then
        echo "MISSING verified_commit $doc"
        exit_code=1
        continue
    fi

    watch_paths=()
    while IFS= read -r path; do
        [[ -n "$path" ]] && watch_paths+=("$path")
    done < <(sed -n '/^watch_paths:/,/^[^ -]/p' "$doc" | sed -n 's/^  - //p')

    if [[ "${#watch_paths[@]}" -eq 0 ]]; then
        echo "MISSING watch_paths $doc"
        exit_code=1
        continue
    fi

    for path in "${watch_paths[@]}"; do
        if [[ ! -e "$repo_root/$path" ]]; then
            echo "BROKEN_PATH $doc -> $path"
            exit_code=1
        fi
    done

    if ! git -C "$repo_root" rev-parse --verify "${verified_commit}^{commit}" >/dev/null 2>&1; then
        echo "UNKNOWN_COMMIT $doc -> $verified_commit"
        exit_code=1
    elif ! git -C "$repo_root" diff --quiet "$verified_commit" "$current_head" -- "${watch_paths[@]}"; then
        echo "STALE $doc"
        exit_code=1
    else
        echo "OK $doc"
    fi
done < <(find "$fact_root" -name README.md | sort)

if [[ "$domain_count" -eq 0 ]]; then
    echo "MISSING_DOMAIN $fact_root"
    exit_code=1
fi

exit "$exit_code"
