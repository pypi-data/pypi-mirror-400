# docs/LOGGING.md — Logging & Evidence

## Rule: every run produces a new log
Always run commands via:
- `./scripts/run_with_log.sh <tag> -- <cmd...>`

It creates:
- `logs/<tag>_<YYYYMMDD_HHMMSS>.log`
- `logs/latest.log` -> newest log
- `logs/<...>.meta` (key=value)
- `logs/latest.meta`
- `logs/runs.tsv` (append-only index)

## Evidence to report (minimum)
- `run_id=...`
- `log=logs/latest.log`
- `exit_code=...` (in meta)

## Grep recipes
- latest log: `./scripts/grep_logs.sh "ERROR"`
- all logs:   `./scripts/grep_logs.sh "timeout" --all`
- runs index: `column -t -s $'\\t' logs/runs.tsv | tail -n 20`
