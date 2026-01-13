# memory/INDEX.md — Long-term Memory Index (LTM)

LTM is for stable facts/traps/playbooks. Keep it **grep-first**.

## LTM note format (required)
Each note lives in `memory/LTM/` and MUST start with:

---
kid: LTM-<AREA>-<NNNN>
tags: [tag1, tag2]
updated: {{TODAY}}
---

## Naming convention (recommended)
`memory/LTM/LTM-<AREA>-<NNNN>-<slug>.md`
Examples:
- `LTM-ARCH-0001-boundaries.md`
- `LTM-OPS-0003-debug-playbook.md`

## How to search
- by id:    `./scripts/kgrep.sh "kid: LTM-"`
- by tag:   `./scripts/kgrep.sh "tags: \\[.*trap.*\\]"`
- by topic: `./scripts/kgrep.sh "ray data" --code`

## Index (edit this)
### ARCH (architecture / boundaries)
- `memory/LTM/0000-LTM_OVERVIEW.md`

### TRAP (recurring gotchas)
- (add)

### OPS (debug / runbooks)
- (add)

_Last updated: {{TODAY}}_
