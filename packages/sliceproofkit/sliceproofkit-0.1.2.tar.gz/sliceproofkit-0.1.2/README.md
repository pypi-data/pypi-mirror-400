# sliceproofkit

A small, opinionated **control-plane kit** for code agents:

- **Slice refactors** (small, verifiable changes)
- **Fail-fast gates** (stop regressions early)
- **Evidence-driven runs** via **timestamped logs** (grep-friendly)

> Think of it as “repo-native muscle memory” for you + your code agent: what to read first, how to validate, where evidence lives, and how to persist knowledge across tasks.

---

## Why

If you’ve ever had a code agent:

- refactor too much → features disappear / bugs reappear
- “fix” via silent fallbacks → problems get hidden until later
- leave progress only in chat → nothing is grep-able next time

…then you don’t need a smarter agent. You need a **workflow that constrains the agent**.

sliceproofkit installs that workflow into your repo as **files + scripts**.

---

## Quick start

### Install

```bash
pip install sliceproofkit
# or (no env pollution)
uvx sliceproofkit --help
````

### Apply to a repo

```bash
sliceproofkit apply --dest . --agents all
# or pick some
sliceproofkit apply --dest . --agents antigravity,trae,cursor
# from this repo (no install)
sliceproofkit apply --kit src/sliceproofkit/kit --dest . --agents all
```

### List supported agents

```bash
sliceproofkit list-agents
```

### Run anything with evidence logs

```bash
./scripts/run_with_log.sh smoke -- echo "hello"
./scripts/grep_logs.sh "hello"
```

### Run the fail-fast gate

```bash
./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh
```

---

## One-time manual setup (recommended, ~10 minutes)

The kit provides the **control plane**, but your repo must define two “facts” for maximum agent speed:

### 1) Fill `docs/INDEX.md`

This is the **repo navigation map**. Minimal fill is enough:

* entry points (CLI / main / service)
* how to run locally
* where config lives (path + format)
* key modules (domain/infra/utils)

### 2) Create `scripts/verify_fast.local.sh`

Most real repos have custom commands (monorepo, Makefile, just, tox/nox, etc.).
Create a local fast gate and make it executable:

```bash
cat > scripts/verify_fast.local.sh << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Example (edit to match your repo)
# python -m compileall -q .
# ruff check .
# pytest -q

echo "TODO: define your project fast gate"
exit 2
EOF

chmod +x scripts/verify_fast.local.sh
```

`verify_fast.sh` will prefer `verify_fast.local.sh` if present.

> Optional but valuable: tune `docs/STANDARDS.md` (architecture boundaries + “don’t change these contracts”) and `LOCKED_FILES.txt`.

---

## How it works

### Flow

```mermaid
flowchart TD
  classDef entry fill:#f8fafc,stroke:#64748b,stroke-width:1px,color:#111;
  classDef doc fill:#ecfeff,stroke:#06b6d4,stroke-width:1px,color:#111;
  classDef mem fill:#eef2ff,stroke:#6366f1,stroke-width:1px,color:#111;
  classDef gate fill:#f0fdf4,stroke:#22c55e,stroke-width:1px,color:#111;
  classDef run fill:#fff7ed,stroke:#fb923c,stroke-width:1px,color:#111;
  classDef log fill:#fdf2f8,stroke:#db2777,stroke-width:1px,color:#111;
  classDef done fill:#f5f3ff,stroke:#8b5cf6,stroke-width:1px,color:#111;

  A["Start: Agent receives task"]:::entry
  B["Read AGENT.md<br/>(Search Order + DoD + Commands)"]:::doc
  C["Slice Protocol<br/>S0 Define constraints<br/>S1 Lock oracle (test/repro)<br/>S2 Small change (<=300 LOC)"]:::gate
  D["Run with evidence<br/>./scripts/run_with_log.sh <tag> -- <cmd>"]:::run
  E["verify_fast gate (fail-fast)<br/>check_locked<br/>check_memory<br/>check_outputs<br/>lint_gate<br/>tests/smoke"]:::gate
  F{"PASS?"}:::gate
  G["Fix smallest delta<br/>re-run verify_fast"]:::gate
  H["Evidence produced<br/>logs/<tag>_<YYYYMMDD_HHMMSS>.log<br/>logs/latest.log -> newest<br/>logs/runs.tsv index"]:::log
  I["Update STM<br/>memory/STM.md: run_id/log/verify<br/>changes + next slice"]:::mem
  J["If stable knowledge found<br/>Write LTM note (kid/tags/updated)<br/>Update memory/INDEX.md"]:::mem
  K["Done (DoD satisfied)<br/>Oracle exists + verify_fast PASS<br/>Evidence linked + STM updated"]:::done

  A --> B --> C --> D --> E --> F
  F -- "No" --> G --> D
  F -- "Yes" --> H --> I --> J --> K
```

---

## User ↔ Agent interaction 

```mermaid
sequenceDiagram
  autonumber
  participant U as User
  participant CLI as sliceproofkit (CLI)
  participant R as Repo (files/scripts)
  participant AG as Code Agent
  participant SH as Shell (run_with_log)
  participant LG as Logs (logs/*)
  participant MEM as Memory (STM/LTM)
  participant V as verify_fast (gates)

  U->>CLI: pip install sliceproofkit
  U->>CLI: sliceproofkit apply --dest . --agents <selected>
  CLI->>R: Copy control plane (AGENT/docs/memory/scripts) + agent rules
  CLI->>R: Merge .gitignore + ensure scripts executable

  Note over U,R: One-time manual setup (recommended, ~10 min)
  U->>R: Edit docs/INDEX.md (entry points / modules / config / verify)
  U->>R: Create scripts/verify_fast.local.sh (project-specific fast gate)
  opt Optional hardening
    U->>R: Tune docs/STANDARDS.md + LOCKED_FILES.txt
  end

  U->>AG: Give task + repo context
  AG->>R: Read AGENT.md (search order + DoD)
  AG->>R: Read docs/INDEX.md + memory/STM.md
  AG->>AG: Plan in slices (S0-S4)

  loop Each slice
    AG->>R: Add/adjust oracle (test or repro)
    AG->>R: Implement small change (<=300 LOC)
    AG->>SH: ./scripts/run_with_log.sh verify_fast -- ./scripts/verify_fast.sh
    SH->>V: check_locked -> check_memory -> check_outputs -> lint_gate -> tests/smoke
    V-->>SH: PASS/FAIL + exit_code
    SH->>LG: Write logs/<tag>_<ts>.log + latest.log + runs.tsv + meta

    alt FAIL
      AG->>LG: Read logs/latest.log / grep errors
      AG->>R: Fix smallest delta
    else PASS
      AG->>MEM: Update memory/STM.md with run_id/log/verify + changes + next slice
      opt Stable knowledge discovered
        AG->>MEM: Write memory/LTM/*.md (kid/tags/updated) + update memory/INDEX.md
      end
    end
  end

  AG-->>U: Report completion with evidence (run_id, log, verify) + files changed
```

---

## What gets installed into your repo

### Common control plane

* `AGENT.md` — read-first entrypoint (search order, DoD, commands)
* `docs/` — standards, logging spec, ADR templates, repo index
* `memory/` — STM + LTM conventions (grep-first)
* `scripts/` — run-with-log, grep logs, verify gates, locked-files check
* `.gitignore` snippet is merged (logs/ etc.)

### Evidence logs

* `logs/<tag>_YYYYMMDD_HHMMSS.log` (one log per run)
* `logs/latest.log` (symlink/copy to newest log)
* `logs/runs.tsv` (index)

---

## Supported agents

Agents are applied via `--agents` (comma-separated) or `all`.

Current templates include:

* `antigravity`
* `trae`
* `cursor`
* `continue`
* `cline`
* `copilot`
* `claude_code`
* `windsurf`
* `aider`
* `iflow-cli`
* `codebuddy`

> Add a new agent:
>
> 1. Create `src/sliceproofkit/kit/agents/<agent_name>/...`
> 2. Add it to `src/sliceproofkit/kit/manifest.yaml`
> 3. Done — the apply tool discovers it automatically

---

## Lint gate: what it checks

`verify_fast` is a layered, fail-fast gate:

1. **Locked files**: prevent accidental edits to repo contracts (`LOCKED_FILES.txt`)
2. **Memory format**: STM/LTM must stay grep-able (headers, required keys)
3. **Outputs format**: ADR/INDEX must include evidence fields, etc.
4. **Lint gate**: stack-aware lint/format/typecheck (and/or your local override)
5. **Tests/smoke**: minimal sanity checks

Your job is to define what “fast enough + strict enough” means for your repo
(via `scripts/verify_fast.local.sh`).

---

## CLI reference

```bash
sliceproofkit --help
sliceproofkit list-agents
sliceproofkit apply --dest <repo_path> --agents all
sliceproofkit apply --dest <repo_path> --agents antigravity,trae,cursor --force
```

---

## Contributing

PRs welcome—especially:

* better stack autodetection for `verify_fast`
* more agent rule templates
* stronger “evidence formatting” gates that stay simple & grep-friendly

---

## License

MIT
