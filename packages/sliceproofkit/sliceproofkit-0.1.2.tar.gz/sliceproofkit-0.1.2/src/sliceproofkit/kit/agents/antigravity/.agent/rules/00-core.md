# Antigravity Core Rules (must follow)

READ FIRST:
- `AGENT.md` (index + search order + DoD)

## Slice Protocol (no exceptions)
S0) Define target behavior + constraints (API/config stability)
S1) Lock behavior (test or reproducible script)
S2) Small change (prefer <= 300 LOC). Avoid refactor+logic mixing.
S3) Verify + Evidence:
    `./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh`
S4) Update memory:
    `memory/STM.md` (what changed + evidence + next slice)

## Fail-fast
- Never swallow errors (no silent fallback).
- Do not change public APIs/config formats unless explicitly asked.

## Evidence-driven output
Every completion message must include:
- run_id=...
- log=logs/latest.log
- verify=PASS/FAIL
- files_changed: (paths)
