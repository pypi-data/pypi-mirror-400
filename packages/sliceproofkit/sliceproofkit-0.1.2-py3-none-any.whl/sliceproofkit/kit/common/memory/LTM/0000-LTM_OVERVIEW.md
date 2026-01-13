---
kid: LTM-OVERVIEW-0000
tags: [overview, memory, rules]
updated: {{TODAY}}
---

# Long-term Memory (LTM) Overview

LTM is for **stable knowledge** that prevents repeated mistakes and repeated explanations.

## What belongs in LTM
- Architecture boundaries / invariants (what must never change)
- Public API & config contracts (compatibility rules)
- Recurring traps + how to detect them (grep patterns, symptoms)
- Debug playbooks (commands + where to look)
- Performance baselines & non-obvious constraints

## What does NOT belong in LTM
- One-off task progress (goes to `memory/STM.md`)
- Temporary hypotheses without evidence
- Long chatty narratives (write grep-first notes)

## Required format for every LTM note
Each note in `memory/LTM/` MUST start with:

---
kid: LTM-<AREA>-<NNNN>
tags: [tag1, tag2]
updated: YYYY-MM-DD
---

## Naming convention (recommended)
`memory/LTM/LTM-<AREA>-<NNNN>-<slug>.md`

Examples:
- `LTM-ARCH-0001-boundaries.md`
- `LTM-TRAP-0002-silent-fallback.md`
- `LTM-OPS-0003-debug-playbook.md`

## Search recipes
- by id:    `./scripts/kgrep.sh "kid: LTM-"`
- by tag:   `./scripts/kgrep.sh "tags: \\[.*trap.*\\]"`
- by topic: `./scripts/kgrep.sh "event=" --logs`

## LTM areas (suggested)
- ARCH: architecture / boundaries / invariants
- API: public API / config compatibility
- TRAP: recurring gotchas / regressions
- OPS: debug playbooks / operational knowledge
- PERF: performance baselines / profiling
