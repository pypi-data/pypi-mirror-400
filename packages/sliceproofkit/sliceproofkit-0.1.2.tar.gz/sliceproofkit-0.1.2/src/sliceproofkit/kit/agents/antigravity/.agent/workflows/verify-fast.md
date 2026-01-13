# Workflow: verify-fast (evidence gate)

## Goal
Produce a **verifiable** result for the current slice.

## Steps
1) Run:
   `./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh`

2) If FAIL:
   - Read `logs/latest.log`
   - Grep errors: `./scripts/grep_logs.sh "ERROR"`
   - Fix in the smallest possible change, then rerun step (1)

3) Report (minimum):
   - run_id=...   (from log header)
   - log=logs/latest.log
   - verify=PASS/FAIL

4) Update `memory/STM.md`:
   - Add evidence block
   - Add what changed + next slice
