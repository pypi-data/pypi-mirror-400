#!/usr/bin/env bash
set -euo pipefail

echo "[verify_full] ts=$(date '+%Y-%m-%d %H:%M:%S') run_id=${RUN_ID:-none}"

if [[ -x "./scripts/check_locked.sh" ]]; then
  ./scripts/check_locked.sh
fi

if [[ -x "./scripts/verify_full.local.sh" ]]; then
  echo "[verify_full] using ./scripts/verify_full.local.sh"
  exec ./scripts/verify_full.local.sh
fi

echo "WARN: verify_full not configured. Create ./scripts/verify_full.local.sh if you need e2e/perf gates."
exit 0
