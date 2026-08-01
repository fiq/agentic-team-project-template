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


import skills  # resolves via the sys.path insert above


def write_skill(root, relative, layers=(), verification=("fixture-verify",), trigger=None):
    """Create a synthetic layered skill in a scratch repo and catalogue it.

    Returns the catalog id. Every named layer gets a real file with enough
    content to pass the emptiness check in `project context check`.
    """
    directory = Path(root) / ".agents/skills" / relative
    directory.mkdir(parents=True, exist_ok=True)
    name = relative.rsplit("/", 1)[-1]
    skill_id = name.replace("-", "_")
    resolved_trigger = trigger or f"{skill_id}_needed"

    declared = "".join(f"  {layer}: {skills.LAYER_FILES[layer]}\n" for layer in layers)
    listed = "".join(f"  - {command}\n" for command in verification)
    (directory / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "description: Synthetic skill used by the context router test suite.\n"
        f"id: SKILL-{name}\n"
        f"triggers: [{resolved_trigger}]\n"
        "default_task_risk: normal\n"
        + (f"layers:\n{declared}" if declared else "")
        + f"verification:\n{listed}"
        "status: active\n"
        "---\n"
        f"\n# {name}\n\nSummary layer for the synthetic {name} fixture skill.\n"
    )
    for layer in layers:
        (directory / skills.LAYER_FILES[layer]).write_text(
            f"# {name} — {layer}\n\n"
            f"Synthetic {layer} layer content for the context router test suite.\n"
        )

    catalog = Path(root) / ".agents/skills/CATALOG.toon"
    catalog.write_text(
        catalog.read_text()
        + f"\n  {skill_id}:\n"
        f"    path: {relative}/SKILL.md\n"
        f"    trigger: {resolved_trigger}\n"
    )
    return skill_id
