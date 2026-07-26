"""Assemble the context plan a resolved profile implies.

The profile chooses which taxonomy layers are preloaded and which are deferred.
It never chooses the required verification, the recovery map or the acceptance
criteria: those are identical under every profile by construction.
"""
from fnmatch import fnmatch
from pathlib import Path

import environment
import router
import toon


def _risk_rules(root):
    return toon.loads((Path(root) / ".agents/context/risk-rules.toon").read_text())


def classify_risk(root, paths, explicit=None):
    """Return (risk, source). The highest risk across touched paths wins."""
    if explicit:
        if explicit not in router.RISKS:
            raise router.RouterError(
                f"unknown risk: {explicit}; expected one of {list(router.RISKS)}"
            )
        return explicit, "flag"
    config = _risk_rules(root)
    if not paths:
        return config["default"], "default"
    best = None
    matched = []
    for path in paths:
        for rule in config["rules"]:
            if any(fnmatch(path, pattern) for pattern in rule["paths"]):
                if best is None or router.RISKS.index(rule["risk"]) > router.RISKS.index(best):
                    best = rule["risk"]
                matched.append(rule["id"])
                break
    if not matched:
        return config["default"], "default"
    ordered = sorted(set(matched))
    return best, "risk-rules:" + ",".join(ordered)


def _entry(root, relative, layer, skill_id=None):
    item = {
        "source": relative,
        "layer": layer,
        "sha": environment.file_digest(Path(root) / relative),
    }
    if skill_id:
        item["skill"] = skill_id
    return item


def _always_preload(root, config, profile):
    sources = config["always_preload_sources"]
    seen = set()
    entries = []
    for name in config["profiles"][profile]["always_preload"]:
        relative = sources.get(name)
        if not relative or relative in seen:
            continue
        seen.add(relative)
        entries.append(_entry(root, relative, name))
    return entries


def _recovery(root):
    data = toon.loads((Path(root) / ".agents/context/RECOVERY.toon").read_text())
    return [
        {"symptom": symptom, "reload": source}
        for symptom, source in data["symptoms"].items()
        if symptom != "unknown"
    ]


def _pending_recovery(root, observation):
    """True while the bounded retry after a degradation has not been spent."""
    if not observation or observation.get("retry_available", True):
        return None
    events = observation.get("events") or []
    symptom = events[-1]["symptom"] if events else "unknown"
    data = toon.loads((Path(root) / ".agents/context/RECOVERY.toon").read_text())
    return {
        "symptom": symptom,
        "reload": data["symptoms"].get(symptom) or data["symptoms"]["unknown"],
        "then": "retry once before increasing context",
    }


def build(root, env, task, config, decision, skill, lookup):
    """Render the full routing decision and its context sets as data."""
    profile = decision.profile
    settings = config["profiles"][profile]
    preload = _always_preload(root, config, profile)
    defer = []
    verification = []
    if skill:
        for layer in settings["preload_layers"]:
            if layer in skill.layers:
                preload.append(_entry(root, skill.layers[layer], layer, skill.id))
        for layer, relative in skill.layers.items():
            if layer not in settings["preload_layers"]:
                defer.append(
                    {
                        "source": relative,
                        "layer": layer,
                        "skill": skill.id,
                        "load_when": "needed for this step, or after a degradation event",
                    }
                )
        verification = list(skill.meta.get("verification") or [])

    document = {
        "version": 1,
        "decision": {
            "profile": profile,
            "reasons": list(decision.reasons),
            "precedence_applied": [f"{step}:{outcome}" for step, outcome in decision.trace],
        },
        "environment": {
            "model_id": env.model_id,
            "model_id_use": "diagnostics_and_override_matching_only",
            "runtime": env.runtime,
            "runtime_capabilities": list(env.capabilities),
            "fingerprint": env.fingerprint,
            "contract_fingerprint": env.contract_fingerprint,
            "observation_status": lookup.status,
            "observation_note": lookup.stale_reason or "none",
        },
        "task": {
            "risk": task.risk,
            "effort": task.effort,
            "skill": skill.id if skill else "none",
        },
        "preload": preload,
        "defer": defer,
        "verification": {"required": verification},
        "recovery": _recovery(root),
        "effort_directives": dict(config["effort"][task.effort]),
        "independent_review": settings["independent_review"],
    }
    pending = _pending_recovery(root, lookup.observation)
    if pending:
        document["recover_first"] = pending
    return {"context_plan": document}


def render_toon(document):
    return toon.dumps(document)


def render_text(document):
    body = document["context_plan"]
    lines = [f"PROFILE  {body['decision']['profile']}", ""]
    lines.append("WHY")
    for reason in body["decision"]["reasons"]:
        lines.append(f"  - {reason}")
    lines.append("")
    lines.append("PRECEDENCE")
    for step in body["decision"]["precedence_applied"]:
        lines.append(f"  {step}")
    lines.append("")
    environment_block = body["environment"]
    lines.append("ENVIRONMENT")
    lines.append(f"  model      {environment_block['model_id']}  (diagnostics only)")
    lines.append(f"  runtime    {environment_block['runtime']}")
    lines.append(f"  capability {', '.join(environment_block['runtime_capabilities'])}")
    lines.append(
        f"  observed   {environment_block['observation_status']}"
        f" ({environment_block['observation_note']})"
    )
    lines.append("")
    lines.append(
        f"TASK  risk={body['task']['risk']}  effort={body['task']['effort']}"
        f"  skill={body['task']['skill']}"
    )
    lines.append("")
    lines.append("PRELOAD")
    for entry in body["preload"]:
        lines.append(f"  [{entry['layer']:<14}] {entry['source']}  {entry['sha']}")
    lines.append("")
    lines.append("LOAD ON DEMAND")
    for entry in body["defer"] or []:
        lines.append(f"  [{entry['layer']:<14}] {entry['source']}")
    if not body["defer"]:
        lines.append("  (none)")
    lines.append("")
    lines.append("REQUIRED VERIFICATION (identical in every profile)")
    for command in body["verification"]["required"] or ["(skill declares none)"]:
        lines.append(f"  {command}")
    lines.append("")
    if "recover_first" in body:
        recover = body["recover_first"]
        lines.append("RECOVER FIRST")
        lines.append(f"  symptom {recover['symptom']}")
        lines.append(f"  reload  {recover['reload']}")
        lines.append(f"  then    {recover['then']}")
        lines.append("")
    lines.append("RECOVERY SOURCES")
    for entry in body["recovery"]:
        lines.append(f"  {entry['symptom']:<30} {entry['reload']}")
    lines.append("")
    directives = body["effort_directives"]
    lines.append(
        f"EFFORT  evidence_depth={directives['evidence_depth']}"
        f"  alternatives={directives['alternatives']}"
        f"  review={directives['review_intensity']}"
    )
    lines.append(f"INDEPENDENT REVIEW  {body['independent_review']}")
    return "\n".join(lines)
