#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/run_with_log.sh <tag> -- <command...>

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <tag> -- <command...>" >&2
  exit 2
fi

TAG="$1"; shift
if [[ "${1:-}" != "--" ]]; then
  echo "Usage: $0 <tag> -- <command...>" >&2
  exit 2
fi
shift

TS="$(date '+%Y%m%d_%H%M%S')"
SAFE_TAG="$(echo "$TAG" | tr ' /:' '___' | tr -cd 'A-Za-z0-9_-' )"
[[ -z "$SAFE_TAG" ]] && SAFE_TAG="run"

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

LOG_FILE="${LOG_DIR}/${SAFE_TAG}_${TS}.log"
META_FILE="${LOG_DIR}/${SAFE_TAG}_${TS}.meta"

ln -sfn "$(basename "$LOG_FILE")" "${LOG_DIR}/latest.log"
ln -sfn "$(basename "$META_FILE")" "${LOG_DIR}/latest.meta"

RUN_ID="${SAFE_TAG}_${TS}"

# Git info (best-effort)
GIT_COMMIT=""; GIT_BRANCH=""; GIT_DIRTY=""
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  GIT_COMMIT="$(git rev-parse --short HEAD 2>/dev/null || true)"
  GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  if ! git diff --quiet 2>/dev/null; then GIT_DIRTY="1"; else GIT_DIRTY="0"; fi
fi

CMD_STR="$*"

# meta (key=value, grep-friendly)
{
  echo "ts=$(date '+%Y-%m-%d %H:%M:%S')"
  echo "run_id=$RUN_ID"
  echo "tag=$TAG"
  echo "log_file=$LOG_FILE"
  echo "cmd=$CMD_STR"
  echo "git_commit=$GIT_COMMIT"
  echo "git_branch=$GIT_BRANCH"
  echo "git_dirty=$GIT_DIRTY"
} > "$META_FILE"

# runs.tsv index
RUNS_TSV="${LOG_DIR}/runs.tsv"
if [[ ! -f "$RUNS_TSV" ]]; then
  echo -e "ts\trun_id\ttag\texit_code\tlog_file\tcmd\tgit_commit\tgit_branch\tgit_dirty" > "$RUNS_TSV"
fi

# header
{
  echo "===== RUN HEADER ====="
  echo "ts=$(date '+%Y-%m-%d %H:%M:%S') run_id=$RUN_ID tag=$TAG"
  echo "cmd=$CMD_STR"
  echo "git_commit=$GIT_COMMIT git_branch=$GIT_BRANCH git_dirty=$GIT_DIRTY"
  echo "log_file=$LOG_FILE meta_file=$META_FILE"
  echo "======================"
} | tee -a "$LOG_FILE"

export RUN_ID LOG_FILE LOG_DIR

# line-buffered if possible (Linux has stdbuf; macOS often doesn't)
BUF_CMD=()
if command -v stdbuf >/dev/null 2>&1; then
  BUF_CMD=(stdbuf -oL -eL)
elif command -v gstdbuf >/dev/null 2>&1; then
  BUF_CMD=(gstdbuf -oL -eL)
fi

set +e
if [[ ${#BUF_CMD[@]} -gt 0 ]]; then
  "${BUF_CMD[@]}" "$@" 2>&1 | tee -a "$LOG_FILE"
  EC=${PIPESTATUS[0]}
else
  "$@" 2>&1 | tee -a "$LOG_FILE"
  EC=${PIPESTATUS[0]}
fi
set -e

echo "exit_code=$EC" >> "$META_FILE"
echo -e "$(date '+%Y-%m-%d %H:%M:%S')\t$RUN_ID\t$TAG\t$EC\t$LOG_FILE\t$CMD_STR\t$GIT_COMMIT\t$GIT_BRANCH\t$GIT_DIRTY" >> "$RUNS_TSV"
echo "[run_with_log] exit_code=$EC run_id=$RUN_ID log=$LOG_FILE" | tee -a "$LOG_FILE"

exit "$EC"
