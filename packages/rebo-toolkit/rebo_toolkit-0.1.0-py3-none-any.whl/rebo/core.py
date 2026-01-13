\
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union
import os
import sys


class ReboError(RuntimeError):
    pass


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def ensure_empty_or_new(dir_path: Path) -> None:
    """
    Ensure directory doesn't exist or is empty (to avoid clobbering user data).
    """
    if dir_path.exists():
        if any(dir_path.iterdir()):
            raise ReboError(f"Target directory '{dir_path}' is not empty.")
    else:
        dir_path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str, overwrite: bool = False) -> bool:
    """
    Returns True if written, False if skipped.
    """
    if path.exists() and not overwrite:
        return False
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return True


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except Exception:
        return str(path)


def detect_repo_type(root: Path) -> str:
    """
    Best-effort detection for doctor/index.
    """
    if (root / "pyproject.toml").exists():
        return "python"
    if (root / "package.json").exists():
        return "node"
    if (root / "CMakeLists.txt").exists() or (root / "Makefile").exists():
        return "c"
    return "generic"


@dataclass
class CheckResult:
    key: str
    ok: bool
    message: str
    fix_hint: str = ""
