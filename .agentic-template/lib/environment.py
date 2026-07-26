"""Runtime detection, capability lookup and contract fingerprinting.

Model identity is captured for diagnostics and override matching only. It never
feeds capability lookup: that is a property of the host runtime.
"""
import hashlib
from dataclasses import dataclass
from pathlib import Path

import router
import toon

CONTRACT_FILES = (
    "AGENTS.md",
    ".agents/skills/CATALOG.toon",
    ".agents/knowledge/TAXONOMY.md",
    ".agents/context/ROUTER.toon",
)

UNREPORTED_MODEL = "unreported"


@dataclass(frozen=True)
class Context(router.Environment):
    contract_fingerprint: str = ""


def _config(root):
    path = Path(root) / ".agents/context/runtimes.toon"
    if not path.exists():
        raise router.RouterError(f"missing runtime config: {path}")
    return toon.loads(path.read_text())


def detect_runtime(root, env_vars):
    """Map host environment variables to a runtime id declared in runtimes.toon."""
    explicit = env_vars.get("AGENTIC_RUNTIME")
    if explicit:
        return explicit
    for rule in _config(root).get("detect") or []:
        if env_vars.get(rule["env"]):
            return rule["runtime"]
    return "unknown"


def capabilities(root, runtime):
    runtimes = _config(root)["runtimes"]
    entry = runtimes.get(runtime) or runtimes["unknown"]
    return list(entry["capabilities"])


def contract_fingerprint(root):
    """Hash the files whose change should invalidate recorded observations."""
    digest = hashlib.sha256()
    for relative in CONTRACT_FILES:
        path = Path(root) / relative
        digest.update(relative.encode())
        digest.update(path.read_bytes() if path.exists() else b"<absent>")
    return digest.hexdigest()[:16]


def build(root, env_vars, model=None, runtime=None):
    """Assemble the Environment the router resolves against."""
    resolved_runtime = runtime or detect_runtime(root, env_vars)
    resolved_model = model or env_vars.get("AGENTIC_MODEL_ID") or UNREPORTED_MODEL
    caps = capabilities(root, resolved_runtime)
    contract = contract_fingerprint(root)
    digest = hashlib.sha256()
    for part in (resolved_model, resolved_runtime, ",".join(sorted(caps)), contract):
        digest.update(part.encode())
        digest.update(b"\x00")
    return Context(
        model_id=resolved_model,
        runtime=resolved_runtime,
        capabilities=caps,
        fingerprint=digest.hexdigest()[:16],
        contract_fingerprint=contract,
    )
