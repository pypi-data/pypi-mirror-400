#!/usr/bin/env bash
set -euo pipefail

LOCK_FILE="LOCKED_FILES.txt"
[[ -f "$LOCK_FILE" ]] || exit 0

command -v git >/dev/null 2>&1 || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

CHANGED="$(git diff --name-only --cached)"
[[ -z "$CHANGED" ]] && CHANGED="$(git diff --name-only)"

[[ -z "$CHANGED" ]] && exit 0

while IFS= read -r pattern; do
  [[ -z "$pattern" ]] && continue
  if echo "$CHANGED" | grep -E "^${pattern//\//\\/}" >/dev/null 2>&1; then
    echo "ERROR: Locked path modified: $pattern" >&2
    echo "Revert changes to locked paths listed in $LOCK_FILE." >&2
    exit 1
  fi
done < "$LOCK_FILE"

exit 0
