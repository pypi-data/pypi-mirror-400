#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <pattern> [--all]" >&2
  exit 2
fi

PATTERN="$1"
MODE="${2:-}"
LOG_DIR="logs"
LATEST="${LOG_DIR}/latest.log"

if [[ "$MODE" == "--all" ]]; then
  if command -v rg >/dev/null 2>&1; then
    rg -n --hidden --no-ignore-vcs "$PATTERN" "$LOG_DIR" || true
  else
    grep -RIn -- "$PATTERN" "$LOG_DIR" || true
  fi
  exit 0
fi

if [[ ! -f "$LATEST" ]]; then
  echo "No latest log found: $LATEST" >&2
  exit 1
fi

grep -n -- "$PATTERN" "$LATEST" || true
