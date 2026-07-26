"""Shared test helpers. Puts the template library on the import path."""
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / ".agentic-template" / "lib"
BIN = ROOT / ".agentic-template" / "bin"

if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))


def temp_repo():
    """Copy the repository to a scratch directory. Returns (TemporaryDirectory, Path).

    The caller keeps the TemporaryDirectory alive and calls cleanup() in tearDown.
    """
    tmp = tempfile.TemporaryDirectory(prefix="context-router-test-")
    root = Path(tmp.name) / "repo"
    shutil.copytree(
        ROOT, root, symlinks=True, ignore=shutil.ignore_patterns(".git", ".superpowers")
    )
    return tmp, root
