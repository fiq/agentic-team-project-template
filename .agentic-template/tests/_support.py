"""Shared test helpers. Puts the template library on the import path."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / ".agentic-template" / "lib"
BIN = ROOT / ".agentic-template" / "bin"

if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))
