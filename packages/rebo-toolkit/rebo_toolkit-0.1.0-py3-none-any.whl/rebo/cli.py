\
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .commands.init import cmd_init
from .commands.doctor import cmd_doctor
from .commands.md2pdf import cmd_md2pdf
from .commands.jsondiff import cmd_jsondiff
from .commands.index import cmd_index


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rebo",
        description="Repo bootstrap + repo utilities (init/doctor/md2pdf/jsondiff/index).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # init
    s = sub.add_parser("init", help="Bootstrap a new repository from a template profile.")
    s.add_argument("path", help="Target directory for new project")
    s.add_argument("--profile", default="py-lib", choices=["py-lib", "node-lib", "c-lib", "minimal"])
    s.add_argument("--name", help="Project display name (default: directory name)")
    s.add_argument("--author", default="", help="Author name used in templates")
    s.add_argument("--email", default="", help="Email used in templates")
    s.add_argument("--github-user", default="", help="GitHub username for URLs")
    s.add_argument("--license", default="MIT", choices=["MIT"], help="License template")
    s.add_argument("--with-ci", action="store_true", help="Add a basic GitHub Actions workflow")
    s.add_argument("--force", action="store_true", help="Overwrite existing files if they exist (dangerous)")
    s.set_defaults(func=cmd_init)

    # doctor
    s = sub.add_parser("doctor", help="Check repo hygiene; optionally auto-fix missing basics.")
    s.add_argument("path", nargs="?", default=".", help="Repo path (default: .)")
    s.add_argument("--fix", action="store_true", help="Create missing recommended files (placeholders).")
    s.add_argument("--force", action="store_true", help="Overwrite existing files when fixing.")
    s.set_defaults(func=cmd_doctor)

    # md2pdf
    s = sub.add_parser("md2pdf", help="Convert Markdown to PDF (subset, no external tools).")
    s.add_argument("input", help="Input .md file")
    s.add_argument("output", help="Output .pdf file")
    s.set_defaults(func=cmd_md2pdf)

    # jsondiff
    s = sub.add_parser("jsondiff", help="Structural diff for two JSON files.")
    s.add_argument("old", help="Old JSON file")
    s.add_argument("new", help="New JSON file")
    s.add_argument("--format", default="text", choices=["text", "json", "html"])
    s.add_argument("--out", default="", help="Output file (optional; for html/json)")
    s.add_argument("--max-changes", type=int, default=200, help="Max individual changes to list")
    s.set_defaults(func=cmd_jsondiff)

    # index
    s = sub.add_parser("index", help="Generate COMMANDS.md from common build/run entrypoints.")
    s.add_argument("path", nargs="?", default=".", help="Repo path (default: .)")
    s.add_argument("--write", action="store_true", help="Write COMMANDS.md into repo")
    s.add_argument("--update-readme", action="store_true", help="Ensure README links to COMMANDS.md")
    s.set_defaults(func=cmd_index)

    return p


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
