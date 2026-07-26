"""Catalog-first skill resolution and taxonomy layer discovery.

Skill paths always resolve through .agents/skills/CATALOG.toon. Frontmatter in
SKILL.md is the single canonical home for a skill's metadata; the catalog holds
only the index fields needed to find it without opening every file.
"""
from dataclasses import dataclass
from pathlib import Path

import toon

LAYERS = (
    "summary",
    "core",
    "procedure",
    "verification",
    "examples",
    "failure_modes",
    "references",
)

LAYER_FILES = {
    "summary": "SKILL.md",
    "core": "core.md",
    "procedure": "procedure.md",
    "verification": "verification.md",
    "examples": "examples.md",
    "failure_modes": "failure-modes.md",
    "references": "references.md",
}

SKILL_ROOT = ".agents/skills"
CATALOG = f"{SKILL_ROOT}/CATALOG.toon"


class SkillError(ValueError):
    """Raised when a skill cannot be resolved or its metadata is malformed."""


@dataclass(frozen=True)
class Skill:
    id: str
    path: Path
    directory: Path
    meta: dict
    layers: dict


def parse_frontmatter(text):
    """Split YAML frontmatter from the body. The subset matches toon.loads."""
    if not text.startswith("---\n"):
        raise SkillError("missing frontmatter")
    end = text.find("\n---", 4)
    if end < 0:
        raise SkillError("unterminated frontmatter")
    raw = text[4:end]
    try:
        meta = toon.loads(raw)
    except toon.ToonError as error:
        raise SkillError(
            f"frontmatter is not parseable ({error}); use two-space indentation, no "
            f"tabs, and quote any value that starts with '[' or '{{'"
        ) from error
    return meta, text[end + 4 :]


def load_catalog(root):
    path = Path(root) / CATALOG
    if not path.exists():
        raise SkillError(f"missing {CATALOG}")
    return toon.loads(path.read_text())["skills"]


def _layers_for(root, directory, meta):
    """Declared layers, restricted to files that actually exist."""
    declared = dict(meta.get("layers") or {})
    found = {"summary": str((directory / "SKILL.md").relative_to(Path(root)))}
    for layer, filename in declared.items():
        if layer not in LAYERS:
            raise SkillError(f"{directory}: unknown taxonomy layer '{layer}'")
        candidate = directory / filename
        if candidate.exists():
            found[layer] = str(candidate.relative_to(Path(root)))
    return found


def _build(root, skill_id, relative_path):
    path = Path(root) / SKILL_ROOT / relative_path
    if not path.exists():
        raise SkillError(f"{CATALOG} points at missing file: {relative_path}")
    meta, _ = parse_frontmatter(path.read_text())
    directory = path.parent
    return Skill(
        id=skill_id,
        path=path,
        directory=directory,
        meta=meta,
        layers=_layers_for(root, directory, meta),
    )


def resolve(root, skill_id=None, trigger=None):
    """Look up one skill by catalog id or by trigger. Never guesses a path."""
    catalog = load_catalog(root)
    if skill_id:
        normalised = skill_id.replace("-", "_")
        entry = catalog.get(normalised)
        if entry is None:
            raise SkillError(
                f"unknown skill '{skill_id}'; resolve ids through {CATALOG} "
                f"({len(catalog)} entries)"
            )
        return _build(root, normalised, entry["path"])
    if trigger:
        for candidate, entry in catalog.items():
            if entry.get("trigger") == trigger:
                return _build(root, candidate, entry["path"])
        raise SkillError(f"no skill in {CATALOG} declares trigger '{trigger}'")
    raise SkillError("resolve() needs skill_id or trigger")


def all_skills(root):
    """Walk the filesystem. Used by the validator to detect catalog drift."""
    found = []
    catalog = load_catalog(root)
    by_path = {entry["path"]: name for name, entry in catalog.items()}
    base = Path(root) / SKILL_ROOT
    for path in sorted(base.rglob("SKILL.md")):
        relative = str(path.relative_to(base))
        found.append(_build(root, by_path.get(relative, f"uncatalogued:{relative}"), relative))
    return found
