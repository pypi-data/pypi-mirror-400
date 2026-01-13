# docs/INDEX.md — Repo Map (fill the blanks)

This is the **repo navigation map**. Keep it short, updated, and grep-friendly.

## Entry points
- CLI:
  - path: (fill)
  - command: (fill)
- Service / main:
  - path: (fill)
  - command: (fill)
- Config:
  - path: (fill)
  - format: (fill)

## Key modules
- domain (core logic):
  - (fill paths)
- infra (IO/DB/HTTP/third-party):
  - (fill paths)
- utils (shared helpers, keep small):
  - (fill paths)

## Verification (required evidence)
- Fast gate (run after each slice):
  - `./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh`
  - evidence: `run_id` + `logs/latest.log`
- Full gate (optional, e2e/perf):
  - `./scripts/run_with_log.sh verify_full -- ./scripts/verify_full.sh`

## Where to write knowledge
- Short-term (every task): `memory/STM.md`
- Long-term (stable): `memory/LTM/*` and index it in `memory/INDEX.md`
- Standards (hard rules): `docs/STANDARDS.md`
- Decisions: `docs/ADR/*`

## Grep shortcuts
- knowledge/docs: `./scripts/kgrep.sh "<pattern>"`
- add code:       `./scripts/kgrep.sh "<pattern>" --code`
- latest log:     `./scripts/grep_logs.sh "<pattern>"`
