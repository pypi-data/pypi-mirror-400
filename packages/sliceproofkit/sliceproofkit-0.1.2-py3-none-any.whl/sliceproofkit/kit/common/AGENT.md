# AGENT.md — Control Plane (READ FIRST)

This repo is agent-driven. Your job is to **change in slices**, **fail fast**, and **ship evidence**.

## What to read (Search Order)
1) `docs/INDEX.md`          — repo map / entry points
2) `memory/STM.md`          — current goal + freshest evidence
3) `docs/STANDARDS.md`      — hard rules (long-term)
4) `memory/INDEX.md` + `memory/LTM/*` — stable knowledge / traps
5) `logs/latest.log`        — freshest runtime evidence
6) `./scripts/kgrep.sh "<pattern>"`  — grep across knowledge/docs/code

## Must-use commands
- Run anything with logs:
  - `./scripts/run_with_log.sh <tag> -- <cmd...>`
- Verify (required after each slice):
  - `./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh`
- Grep knowledge/docs/code:
  - `./scripts/kgrep.sh "<pattern>" [--code] [--logs]`
- Grep logs:
  - `./scripts/grep_logs.sh "<pattern>" [--all]`

## Slice Protocol (no exceptions)
S0. **Define** target behavior + constraints (API/config compatibility).
S1. **Lock behavior**: add test or a reproducible script (oracle).
S2. **Small change** (prefer <= 300 LOC), avoid mixing refactor+logic.
S3. **Verify + Evidence**: run verify_fast via `run_with_log.sh`.
S4. **Update memory**: write evidence + next step into `memory/STM.md`.
Only then start the next slice.

## Definition of Done (DoD)
A task is DONE only if:
- The oracle exists (test/repro).
- `verify_fast` PASS with evidence:
  - `run_id=...`
  - `log=logs/latest.log` (or concrete file)
- `memory/STM.md` updated (what changed + evidence + next step).

## Fail-fast rules
- No silent fallback. No `try/except: pass`. Errors must be explicit and actionable.
- Don’t change public API/config formats unless explicitly asked.
- If unsure: search first, cite file paths in your answer.
