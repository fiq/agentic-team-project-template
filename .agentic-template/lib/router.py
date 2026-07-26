"""Deterministic context-profile resolution.

resolve() is pure: it takes already-loaded data and returns a Decision. Every
precedence step may only raise the profile along ROUTER.toon's `order` ladder, so
the result never depends on step ordering beyond what the trace records.
"""
from dataclasses import dataclass, field
from datetime import date
from fnmatch import fnmatch
from pathlib import Path

import toon

RISKS = ("low", "normal", "high", "irreversible")
EFFORTS = ("minimal", "standard", "deep")
HIGH_RISKS = ("high", "irreversible")


class RouterError(ValueError):
    """Raised when router inputs or configuration are invalid."""


@dataclass(frozen=True)
class Environment:
    model_id: str
    runtime: str
    capabilities: list
    fingerprint: str


@dataclass(frozen=True)
class Task:
    risk: str
    effort: str
    skill_id: str
    paths: list = field(default_factory=list)


@dataclass
class Decision:
    profile: str
    reasons: list
    trace: list


def load_config(root):
    path = Path(root) / ".agents/context/ROUTER.toon"
    if not path.exists():
        raise RouterError(f"missing router config: {path}")
    return toon.loads(path.read_text())


def load_overrides(root, today=None):
    """Local overrides first, then shared. Expired entries are dropped."""
    root = Path(root)
    entries = []
    for name in ("overrides.local.toon", "overrides.toon"):
        path = root / ".agents/context" / name
        if not path.exists():
            continue
        data = toon.loads(path.read_text())
        for entry in data.get("overrides") or []:
            entries.append(dict(entry, source=str(path.relative_to(root))))
    return [entry for entry in entries if not _expired(entry, today)]


def _expired(entry, today=None):
    expires = entry.get("expires")
    if not expires:
        return False
    return str(expires) < (today or date.today().isoformat())


def _rank(config, profile):
    order = config["order"]
    if profile not in order:
        raise RouterError(f"unknown profile: {profile}")
    return order.index(profile)


def _raise_to(config, current, candidate):
    if candidate is None:
        return current
    if current is None:
        return candidate
    return candidate if _rank(config, candidate) > _rank(config, current) else current


def _matches(entry, env):
    match = entry.get("match") or {}
    model = str(match.get("model", "*"))
    runtime = str(match.get("runtime", "*"))
    return fnmatch(env.model_id or "", model) and fnmatch(env.runtime or "", runtime)


def _validate(config, task):
    if task.risk not in RISKS:
        raise RouterError(f"unknown risk: {task.risk}; expected one of {list(RISKS)}")
    if task.effort not in EFFORTS:
        raise RouterError(f"unknown effort: {task.effort}; expected one of {list(EFFORTS)}")
    for risk in HIGH_RISKS:
        floor = config["risk_floors"].get(risk)
        if _rank(config, floor) < _rank(config, "guarded"):
            raise RouterError(
                f"risk_floors.{risk} is {floor}; {risk} work must floor at guarded"
            )


def resolve(env, task, config, overrides, observation):
    """Return the Decision for this environment, task and recorded state."""
    _validate(config, task)
    reasons = []
    trace = []
    profile = None

    override = next((entry for entry in overrides if _matches(entry, env) and not _expired(entry)), None)
    if override:
        profile = override["profile"]
        trace.append(("force_override", f"hit:{profile}"))
        reasons.append(
            f"force override in {override.get('source', 'overrides')} selected "
            f"{profile} ({override.get('reason', 'no reason recorded')})"
        )
    else:
        trace.append(("force_override", "miss"))
        reasons.append("no force override matched the active model and runtime")

    result = (observation or {}).get("result") or "uncertain"
    if profile is None:
        profile = "lean" if result == "pass" else "standard"
        reasons.append(f"qualification result is {result}, routing to {profile}")
    trace.append(("qualification", result))

    escalated = (observation or {}).get("escalated_profile")
    if escalated:
        raised = _raise_to(config, profile, escalated)
        if raised != profile:
            reasons.append(f"recorded degradation escalated the profile to {escalated}")
        profile = raised
        trace.append(("degradation_floor", escalated))
    else:
        trace.append(("degradation_floor", "none"))

    floor = config["risk_floors"][task.risk]
    raised = _raise_to(config, profile, floor)
    if raised != profile:
        reasons.append(f"task risk {task.risk} floors the profile at {floor}")
    profile = raised
    trace.append(("risk_floor", floor))

    if task.risk in HIGH_RISKS:
        raised = _raise_to(config, profile, "guarded")
        if raised != profile:
            reasons.append(f"{task.risk} work is guarded regardless of other inputs")
        profile = raised
        trace.append(("irreversible_guard", "applied"))
    else:
        trace.append(("irreversible_guard", "not_applicable"))

    return Decision(profile=profile, reasons=reasons, trace=trace)
