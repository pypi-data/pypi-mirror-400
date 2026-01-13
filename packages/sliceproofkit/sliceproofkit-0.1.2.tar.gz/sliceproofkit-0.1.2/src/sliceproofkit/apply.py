from __future__ import annotations

import os
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


@dataclass(frozen=True)
class CopyItem:
    src: str
    dst: str
    mode: str = "copy"  # copy | merge_gitignore
    optional: bool = False


@dataclass(frozen=True)
class Manifest:
    render_extensions: Tuple[str, ...]
    common_copy: Tuple[CopyItem, ...]
    agents: Dict[str, Tuple[CopyItem, ...]]


def load_manifest(kit_root: Path) -> Manifest:
    mf = kit_root / "manifest.yaml"
    data = yaml.safe_load(mf.read_text(encoding="utf-8"))
    exts = tuple(data.get("render_extensions", []))
    common = []
    for item in data.get("common", {}).get("copy", []):
        common.append(CopyItem(**item))
    agents: Dict[str, Tuple[CopyItem, ...]] = {}
    for name, block in (data.get("agents") or {}).items():
        items = []
        for item in block.get("copy", []):
            items.append(CopyItem(**item))
        agents[name] = tuple(items)
    return Manifest(render_extensions=exts, common_copy=tuple(common), agents=agents)


def parse_agents(raw: str) -> List[str]:
    raw = raw.strip()
    if not raw:
        return []
    if raw.lower() == "all":
        return ["all"]
    aliases = {
        "iflow": "iflow-cli",
        "iflowcli": "iflow-cli",
        "code-buddy": "codebuddy",
    }
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    seen = set()
    out: List[str] = []
    for p in parts:
        key = p.lower()
        name = aliases.get(key, p)
        if name not in seen:
            out.append(name)
            seen.add(name)
    return out


def render_text(content: str, variables: Dict[str, str]) -> str:
    # Replace {{VAR}} occurrences
    for k, v in variables.items():
        content = content.replace("{{" + k + "}}", v)
    return content


def should_render(path: Path, exts: Tuple[str, ...]) -> bool:
    return any(path.name.endswith(ext) for ext in exts)


def merge_gitignore(dst_path: Path, snippet: str) -> None:
    existing = ""
    if dst_path.exists():
        existing = dst_path.read_text(encoding="utf-8", errors="replace")
    # Append snippet if it's not already present (by header marker)
    marker = "# ==== agent-kit (generated) ===="
    if marker in existing:
        return
    out = existing.rstrip() + ("\n\n" if existing.strip() else "") + snippet.rstrip() + "\n"
    dst_path.write_text(out, encoding="utf-8")


def copy_file(src: Path, dst: Path, *, render: bool, variables: Dict[str, str], exts: Tuple[str, ...], force: bool) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        return
    if render and should_render(src, exts):
        txt = src.read_text(encoding="utf-8", errors="replace")
        dst.write_text(render_text(txt, variables), encoding="utf-8")
    else:
        shutil.copy2(src, dst)


def copy_any(src: Path, dst: Path, *, variables: Dict[str, str], exts: Tuple[str, ...], force: bool) -> None:
    if src.is_dir():
        # Copy directory tree
        for root, dirs, files in os.walk(src):
            rel = Path(root).relative_to(src)
            for d in dirs:
                (dst / rel / d).mkdir(parents=True, exist_ok=True)
            for f in files:
                s = Path(root) / f
                d = dst / rel / f
                copy_file(s, d, render=True, variables=variables, exts=exts, force=force)
    else:
        copy_file(src, dst, render=True, variables=variables, exts=exts, force=force)


def chmod_scripts(dest_root: Path) -> None:
    scripts = dest_root / "scripts"
    if not scripts.exists():
        return
    for p in scripts.glob("*.sh"):
        try:
            st = p.stat()
            p.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except Exception:
            pass


def apply(kit_root: Path, dest_root: Path, agents: List[str], *, project_name: Optional[str] = None, force: bool = False) -> None:
    manifest = load_manifest(kit_root)

    # Variables for template rendering
    variables: Dict[str, str] = {}
    variables["TODAY"] = __import__("datetime").date.today().isoformat()
    variables["PROJECT_NAME"] = project_name or dest_root.name

    # Ensure dest exists
    dest_root.mkdir(parents=True, exist_ok=True)

    def do_item(item: CopyItem):
        src = kit_root / item.src
        dst = dest_root / item.dst
        if item.optional and not src.exists():
            return
        if item.mode == "merge_gitignore":
            snippet = (kit_root / item.src).read_text(encoding="utf-8", errors="replace")
            merge_gitignore(dst, render_text(snippet, variables))
        else:
            copy_any(src, dst, variables=variables, exts=manifest.render_extensions, force=force)

    # common
    for item in manifest.common_copy:
        do_item(item)

    # agents
    if agents == ["all"]:
        selected = list(manifest.agents.keys())
    else:
        selected = agents
    for name in selected:
        if name not in manifest.agents:
            raise SystemExit(f"Unknown agent: {name}. Available: {', '.join(sorted(manifest.agents.keys()))}")
        for item in manifest.agents[name]:
            do_item(item)

    # Ensure scripts are executable
    chmod_scripts(dest_root)
