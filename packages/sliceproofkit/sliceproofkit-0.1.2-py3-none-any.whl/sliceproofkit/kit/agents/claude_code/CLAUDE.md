# Claude Code — Project Instructions (short + hard)

READ FIRST: `AGENT.md`

## Non-negotiables
- Slice protocol: oracle -> small change -> verify_fast -> STM update
- Fail-fast: no silent fallback / no swallowed exceptions
- Evidence: every completion must include:
  - run_id=...
  - log=logs/latest.log
  - verify=PASS/FAIL
  - files_changed: (paths)

## Commands
- Run with logs:
  `./scripts/run_with_log.sh <tag> -- <cmd...>`
- Fast verify:
  `./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh`
