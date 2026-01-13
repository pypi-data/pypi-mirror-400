# docs/STANDARDS.md — Hard Standards (Long-term)

These are non-negotiable rules for this repo.

## 1) Evidence-driven workflow
- Every behavior change MUST have an oracle (test or reproducible script).
- Every slice MUST produce evidence:
  - `run_id` + `logs/latest.log`
  - `verify_fast` result

## 2) Slice protocol
- Prefer <= 300 LOC per slice.
- Do not mix refactor + logic in the same slice.
- Mechanical moves first (rename/move/extract), logic last.
- After each slice: `run_with_log.sh verify_fast -- verify_fast.sh`

## 3) Fail-fast error handling
- No silent fallback. No swallowing exceptions.
- Errors must be actionable:
  - include `event=... module=...` and key context
- If input/config invalid: fail early with clear message.

## 4) Public API / config stability
- No breaking change unless explicitly requested.
- If change is required: document in `memory/STM.md` and add compatibility plan.

## 5) Logging (grep-first)
- Prefer one-line `key=value` logs.
- Always include `event=` and `module=`.
- If available, include `run_id=${RUN_ID}` (provided by run_with_log.sh).

## 6) Knowledge hygiene
- Short-term state goes to `memory/STM.md` (every task).
- Stable knowledge goes to `memory/LTM/*` with `kid/tags/updated`.
