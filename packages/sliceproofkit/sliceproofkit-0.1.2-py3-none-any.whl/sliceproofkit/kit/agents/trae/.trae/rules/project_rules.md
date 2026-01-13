# Trae Project Rules (must follow)

READ FIRST:
- `AGENT.md` (index + search order + DoD)
- then `docs/INDEX.md`, `memory/STM.md`

## Workflow (Slices + Evidence)
- Work in slices (prefer <= 300 LOC). Do not mix refactor+logic.
- Before changing behavior: lock an oracle (test or repro script).
- After each slice: run and report evidence:
  - `./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh`
  - report: `run_id=...`, `log=logs/latest.log`, `verify=PASS/FAIL`

## Fail-fast
- No silent fallback. No `try/except: pass`. Errors must be explicit.
- Do not change public APIs / config formats unless explicitly asked.

## Knowledge updates
- Update `memory/STM.md` every task (what changed + evidence + next slice).
- Stable findings go to `memory/LTM/*` with required header:
  - `kid:` / `tags:` / `updated:`
  - and add it to `memory/INDEX.md`

## Logging
- Prefer grep-friendly one-line `key=value` logs.
- Include `event=` and `module=`.
- Include `run_id=${RUN_ID}` when available.
