# Continue rules (short + hard)

READ FIRST: `AGENT.md`

- Work in slices (<=300 LOC). Don't mix refactor+logic.
- No silent fallback. No swallowed exceptions.
- After each slice:
  `./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh`
  Report evidence: run_id, log=logs/latest.log, verify=PASS/FAIL.
- Update `memory/STM.md` every task (evidence first).
