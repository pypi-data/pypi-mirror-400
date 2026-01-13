# GitHub Copilot Instructions

Always follow this repo's control plane:
- Read `AGENT.md` first.
- Work in slices (small, verifiable changes).
- Never swallow errors.
- After each slice, run:
  `./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh`
- Report evidence: run_id + log + PASS/FAIL, then update `memory/STM.md`.
