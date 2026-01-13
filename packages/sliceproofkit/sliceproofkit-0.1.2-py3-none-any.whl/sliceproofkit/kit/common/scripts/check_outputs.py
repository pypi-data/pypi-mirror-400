#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys
from pathlib import Path


REQ_EVID_KEYS = ["run_id=", "log=", "verify="]


def fail(msg: str) -> None:
    print(f"[check_outputs] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"[check_outputs] WARN: {msg}", file=sys.stderr)


def check_docs_index(root: Path) -> None:
    p = root / "docs" / "INDEX.md"
    if not p.exists():
        fail("docs/INDEX.md missing")
    txt = p.read_text(encoding="utf-8", errors="replace").strip()
    if len(txt) < 20:
        fail("docs/INDEX.md too short (fill the repo map)")


def is_template_adr(path: Path) -> bool:
    name = path.name.lower()
    return "template" in name or name.startswith("0001-") or name.startswith("0000-")


def check_adr_evidence(root: Path) -> None:
    adr_dir = root / "docs" / "ADR"
    if not adr_dir.exists():
        return
    md_files = sorted([p for p in adr_dir.glob("*.md") if p.is_file()])
    for p in md_files:
        if is_template_adr(p):
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        if "## Evidence" not in txt:
            fail(f"{p.as_posix()} missing '## Evidence' section")
        # Require at least one evidence key somewhere after Evidence header
        tail = txt.split("## Evidence", 1)[-1]
        if not any(k in tail for k in REQ_EVID_KEYS):
            fail(f"{p.as_posix()} Evidence section missing one of: {', '.join(REQ_EVID_KEYS)}")


def check_agent_entrypoints(root: Path) -> None:
    # These should exist after apply; if not, it's probably a broken apply.
    must = [
        root / "AGENT.md",
        root / "docs" / "STANDARDS.md",
        root / "memory" / "STM.md",
        root / "scripts" / "run_with_log.sh",
    ]
    for p in must:
        if not p.exists():
            fail(f"missing required file: {p.as_posix()}")


def main() -> None:
    root = Path(".")
    check_agent_entrypoints(root)
    check_docs_index(root)
    check_adr_evidence(root)
    print("[check_outputs] OK")


if __name__ == "__main__":
    main()
