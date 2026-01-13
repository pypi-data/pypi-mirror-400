#!/usr/bin/env bash
set -euo pipefail

echo "[lint_gate] ts=$(date '+%Y-%m-%d %H:%M:%S') run_id=${RUN_ID:-none}"

# Always validate agent-generated artifacts first
if [[ -x "./scripts/check_outputs.sh" ]]; then
  ./scripts/check_outputs.sh
fi

# Per-project override
if [[ -x "./scripts/lint_gate.local.sh" ]]; then
  echo "[lint_gate] using ./scripts/lint_gate.local.sh"
  exec ./scripts/lint_gate.local.sh
fi

FOUND=0

# Python lint/format/type (strict if pyproject.toml exists)
if [[ -f "pyproject.toml" ]]; then
  FOUND=1
  if ! command -v ruff >/dev/null 2>&1; then
    echo "ERROR: ruff not found but pyproject.toml exists. Install ruff or provide lint_gate.local.sh" >&2
    exit 2
  fi
  ruff format .
  ruff check .
  if command -v pyright >/dev/null 2>&1; then
    pyright
  fi
fi

# Go basic formatting (soft) + vet (soft)
if [[ $FOUND -eq 0 ]] && [[ -f "go.mod" ]]; then
  FOUND=1
  if command -v go >/dev/null 2>&1; then
    gofmt -w . >/dev/null 2>&1 || true
    go vet ./... >/dev/null 2>&1 || true
  else
    echo "ERROR: go.mod exists but 'go' not found." >&2
    exit 2
  fi
fi

# Node lint (soft; only if script exists)
if [[ $FOUND -eq 0 ]] && [[ -f "package.json" ]]; then
  FOUND=1
  if command -v pnpm >/dev/null 2>&1; then
    pnpm -s lint || true
  elif command -v npm >/dev/null 2>&1; then
    npm -s run lint || true
  else
    echo "ERROR: package.json exists but pnpm/npm not found." >&2
    exit 2
  fi
fi

echo "[lint_gate] OK"
