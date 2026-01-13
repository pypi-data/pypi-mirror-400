# Aider Conventions (short + hard)

- Read `AGENT.md` first.
- Make small slices; don't mix refactor+logic.
- No silent fallback. Errors must be actionable.
- After each slice:
  `./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh`
  Provide run_id + log=logs/latest.log + verify result.
- Update `memory/STM.md` (evidence first).
