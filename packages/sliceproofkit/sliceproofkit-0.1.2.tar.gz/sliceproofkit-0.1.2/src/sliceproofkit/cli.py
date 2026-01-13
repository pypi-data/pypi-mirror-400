from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from . import __version__
from .apply import apply, load_manifest, parse_agents


def _kit_root_from_pkg() -> Path:
    # Prefer packaged kit
    from importlib import resources
    # resources.files is available in py3.9+
    return Path(resources.files("sliceproofkit.kit"))


def cmd_list_agents(args: argparse.Namespace) -> int:
    kit_root = Path(args.kit).resolve() if args.kit else _kit_root_from_pkg()
    mf = load_manifest(kit_root)
    for a in sorted(mf.agents.keys()):
        print(a)
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    kit_root = Path(args.kit).resolve() if args.kit else _kit_root_from_pkg()
    dest = Path(args.dest).resolve()
    agents = parse_agents(args.agents)
    if not agents:
        raise SystemExit("--agents is required (use 'all' or comma-separated list)")
    apply(kit_root, dest, agents, project_name=args.project_name, force=args.force)
    print(f"[sliceproofkit] applied to {dest} agents={args.agents}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sliceproofkit", description="Apply slice+proof agent templates into a repo.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list-agents", help="List available agent templates")
    p_list.add_argument("--kit", default=None, help="Use an external kit directory instead of the packaged kit")
    p_list.set_defaults(func=cmd_list_agents)

    p_apply = sub.add_parser("apply", help="Apply templates into a destination repo")
    p_apply.add_argument("--dest", required=True, help="Destination repo path")
    p_apply.add_argument("--agents", required=True, help="all | comma-separated list, e.g. antigravity,trae,cursor")
    p_apply.add_argument("--kit", default=None, help="Use an external kit directory instead of the packaged kit")
    p_apply.add_argument("--project-name", default=None, help="Override {{PROJECT_NAME}} template variable")
    p_apply.add_argument("--force", action="store_true", help="Overwrite existing files")
    p_apply.set_defaults(func=cmd_apply)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
