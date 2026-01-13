#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
import sys
from pathlib import Path


REQ_STM_KEYS = ["run_id=", "log=", "verify="]

FRONT_MATTER_RE = re.compile(r"(?s)^---\n(.*?)\n---\n")
REQ_LTM_FIELDS = ["kid:", "tags:", "updated:"]


def fail(msg: str) -> None:
    print(f"[check_memory] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def check_stm(path: Path) -> None:
    if not path.exists():
        fail(f"missing {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    for k in REQ_STM_KEYS:
        if k not in text:
            fail(f"{path} missing required key: {k}")


def check_ltm_dir(dir_path: Path) -> None:
    if not dir_path.exists():
        return
    for p in sorted(dir_path.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        m = FRONT_MATTER_RE.match(text)
        if not m:
            fail(f"{p} missing YAML front matter header")
        fm = m.group(1)
        for f in REQ_LTM_FIELDS:
            if f not in fm:
                fail(f"{p} front matter missing field: {f}")


def main() -> None:
    root = Path(".")
    check_stm(root / "memory" / "STM.md")
    check_ltm_dir(root / "memory" / "LTM")
    print("[check_memory] OK")


if __name__ == "__main__":
    main()
