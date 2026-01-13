#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <pattern> [--code] [--logs]" >&2
  echo "Default search: AGENT.md docs/ memory/" >&2
  exit 2
fi

PATTERN="$1"
shift || true

SEARCH=( "AGENT.md" "docs" "memory" )

while [[ $# -gt 0 ]]; do
  case "$1" in
    --code) SEARCH+=( "src" "tests" ) ;;
    --logs) SEARCH+=( "logs/latest.log" ) ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

if command -v rg >/dev/null 2>&1; then
  rg -n --hidden --no-ignore-vcs "$PATTERN" "${SEARCH[@]}" || true
else
  grep -RIn -- "$PATTERN" "${SEARCH[@]}" 2>/dev/null || true
fi
