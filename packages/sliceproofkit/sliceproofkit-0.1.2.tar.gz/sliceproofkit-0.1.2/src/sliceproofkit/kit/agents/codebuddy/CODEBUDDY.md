# CODEBUDDY.md - Project Memory (managed by sliceproofkit)

You must be evidence-driven:
- Prefer small, reviewable slices.
- Fail-fast: run verify early, stop on failure.
- Always cite the exact command and log path.

Start here:
1) Read docs/INDEX.md (repo map and entry points and verify commands)
2) Read AGENT.md (core rules)
3) Use scripts/run_with_log.sh to create timestamped logs
4) Use scripts/grep_logs.sh / scripts/kgrep.sh to locate evidence

When changing code:
- Avoid big refactors unless explicitly requested.
- Update docs/INDEX.md / memory/STM.md if you learned anything new.
