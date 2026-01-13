# IFLOW.md - Project Memory (managed by sliceproofkit)

## Prime directive
Follow sliceproof workflow: small slice -> fail-fast verify -> log evidence -> update indexes.

## What to read first
@./AGENT.md
@./docs/INDEX.md
@./docs/STANDARDS.md
@./docs/LOGGING.md
@./memory/INDEX.md
@./memory/STM.md
@./memory/LTM/0000-LTM_OVERVIEW.md

## Working loop (always)
1) Read docs/INDEX.md to find entry points and verify commands.
2) Make minimal change (avoid large refactor).
3) Run scripts/verify_fast.sh (or scripts/verify_fast.local.sh if exists).
4) Paste log path and key grep hints in your reply.
5) If a rule/doc/index is wrong, update it in same PR.
