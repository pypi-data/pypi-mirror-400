#!/usr/bin/env bash
set -euo pipefail

echo "[verify_fast] ts=$(date '+%Y-%m-%d %H:%M:%S') run_id=${RUN_ID:-none}"

# Always enforce locked paths first (fail-fast)
if [[ -x "./scripts/check_locked.sh" ]]; then
  ./scripts/check_locked.sh
fi

if [[ -x "./scripts/check_memory.sh" ]]; then
  ./scripts/check_memory.sh
fi

if [[ -x "./scripts/lint_gate.sh" ]]; then
  ./scripts/lint_gate.sh
fi

# Allow per-project override without editing the common template
if [[ -x "./scripts/verify_fast.local.sh" ]]; then
  echo "[verify_fast] using ./scripts/verify_fast.local.sh"
  exec ./scripts/verify_fast.local.sh
fi

# --- Auto-detect minimal stacks (best-effort) ---
FOUND=0

# Python stack
if [[ -f "pyproject.toml" ]] && command -v python >/dev/null 2>&1; then
  FOUND=1
  echo "[1/4] python format"
  if command -v ruff >/dev/null 2>&1; then
    ruff format .
  else
    echo "ERROR: ruff not found. Provide scripts/verify_fast.local.sh or install ruff." >&2
    exit 2
  fi

  echo "[2/4] python lint/type"
  ruff check .
  if command -v pyright >/dev/null 2>&1; then
    pyright
  else
    echo "WARN: pyright not found (skipped)"
  fi

  echo "[3/4] python tests"
  if command -v pytest >/dev/null 2>&1; then
    pytest -q
  else
    echo "WARN: pytest not found (skipped)"
  fi

  echo "[4/4] python smoke"
  python -c "import sys; print('smoke_ok', sys.version.split()[0])" >/dev/null
fi

# Node stack
if [[ $FOUND -eq 0 ]] && [[ -f "package.json" ]]; then
  FOUND=1
  echo "[verify_fast] node stack"
  if command -v pnpm >/dev/null 2>&1; then
    pnpm -s lint || true
    pnpm -s test || true
  elif command -v npm >/dev/null 2>&1; then
    npm -s test || true
  else
    echo "ERROR: pnpm/npm not found." >&2
    exit 2
  fi
fi

# Go stack
if [[ $FOUND -eq 0 ]] && [[ -f "go.mod" ]]; then
  FOUND=1
  echo "[verify_fast] go stack"
  go test ./...
fi

if [[ $FOUND -eq 0 ]]; then
  echo "ERROR: verify_fast cannot auto-detect stack." >&2
  echo "Create ./scripts/verify_fast.local.sh (executable) as the oracle runner." >&2
  exit 2
fi

echo "[verify_fast] OK"
