"""Recorded evidence about how a model-runtime pair actually behaves here.

Observations are scoped to a fingerprint over model, runtime, tools and the
contract files. Any material change to those invalidates the record rather than
silently carrying a stale capability claim forward.

Escalation is fast: one degradation after the retry budget is spent raises the
profile a step. Reduction is cautious: it needs a run of successes and a
currently passing qualification.
"""
from collections import namedtuple
from datetime import date
from pathlib import Path

import environment
import toon

Lookup = namedtuple("Lookup", "observation status stale_reason")
Outcome = namedtuple("Outcome", "action reload_source escalated_profile message")

STORE = ".agents/context/observations"


def path_for(root, env):
    return Path(root) / STORE / f"{env.fingerprint}.toon"


def _all(root):
    for path in sorted((Path(root) / STORE).glob("*.toon")):
        yield path, toon.loads(path.read_text())["observation"]


def _changed_contract_files(root, recorded):
    """Name the contract files whose hash no longer matches the recording."""
    changed = []
    stored_by_path = {
        entry["path"]: entry["digest"] for entry in recorded.get("contract_files") or []
    }
    for relative in environment.CONTRACT_FILES:
        stored = stored_by_path.get(relative)
        current = environment.file_digest(Path(root) / relative)
        if stored and stored != current:
            changed.append(relative)
    return changed


def lookup(root, env):
    """Find the observation for this exact environment, or explain its absence."""
    path = path_for(root, env)
    if path.exists():
        return Lookup(toon.loads(path.read_text())["observation"], "current", None)
    for _, recorded in _all(root):
        if recorded.get("model_id") == env.model_id and recorded.get("runtime") == env.runtime:
            changed = _changed_contract_files(root, recorded)
            reason = (
                "changed since the observation: " + ", ".join(changed)
                if changed
                else "environment fingerprint changed"
            )
            return Lookup(None, "invalidated", reason)
    return Lookup(None, "absent", None)


def _blank(root, env, today):
    return {
        "fingerprint": env.fingerprint,
        "model_id": env.model_id,
        "runtime": env.runtime,
        "tools": list(env.capabilities),
        "contract_fingerprint": env.contract_fingerprint,
        "contract_files": [
            {"path": relative, "digest": environment.file_digest(Path(root) / relative)}
            for relative in environment.CONTRACT_FILES
        ],
        "qualification_version": 0,
        "result": "uncertain",
        "probe_results": {},
        "recorded": today,
        "degradations": 0,
        "retry_available": True,
        "escalated_profile": None,
        "successes_since_degradation": 0,
        "events": [],
    }


def _load_or_blank(root, env, today):
    path = path_for(root, env)
    if path.exists():
        return toon.loads(path.read_text())["observation"]
    return _blank(root, env, today)


def _save(root, record):
    path = Path(root) / STORE / f"{record['fingerprint']}.toon"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(toon.dumps({"observation": record}))


def record_qualification(root, env, result, probes, today=None):
    """Store a qualification result. Escalation state is left untouched."""
    today = today or date.today().isoformat()
    record = _load_or_blank(root, env, today)
    record["result"] = result
    record["probe_results"] = dict(probes)
    record["recorded"] = today
    _save(root, record)
    return record


def recovery_source(root, symptom):
    data = toon.loads((Path(root) / ".agents/context/RECOVERY.toon").read_text())
    symptoms = data["symptoms"]
    return symptoms.get(symptom) or symptoms["unknown"]


def _next_profile(config, current):
    order = config["order"]
    index = min(order.index(current) + 1, len(order) - 1)
    return order[index]


def record_event(root, env, event, symptom, config, current_profile, today=None):
    """Apply one degradation or success to the escalation ladder."""
    today = today or date.today().isoformat()
    record = _load_or_blank(root, env, today)
    record["events"].append({"date": today, "event": event, "symptom": symptom or "none"})

    if event == "degraded":
        source = recovery_source(root, symptom or "unknown")
        record["successes_since_degradation"] = 0
        if record["retry_available"]:
            record["retry_available"] = False
            _save(root, record)
            return Outcome(
                "recover_and_retry",
                source,
                record["escalated_profile"],
                f"reload {source}, then retry once before increasing context",
            )
        record["degradations"] += 1
        record["retry_available"] = True
        base = record["escalated_profile"] or current_profile
        record["escalated_profile"] = _next_profile(config, base)
        _save(root, record)
        return Outcome(
            "escalate",
            source,
            record["escalated_profile"],
            f"recovery and retry did not restore correctness; escalated to "
            f"{record['escalated_profile']}",
        )

    if event != "success":
        raise ValueError(f"unknown event: {event}; expected 'degraded' or 'success'")

    record["successes_since_degradation"] += 1
    record["retry_available"] = True
    needed = config["degradation"]["reduce_after_successes"]
    can_reduce = (
        record["escalated_profile"]
        and record["result"] == "pass"
        and record["successes_since_degradation"] >= needed
    )
    if can_reduce:
        record["escalated_profile"] = None
        record["successes_since_degradation"] = 0
        _save(root, record)
        return Outcome("reduced", None, None, f"{needed} clean runs; escalation removed")
    _save(root, record)
    return Outcome(
        "recorded",
        None,
        record["escalated_profile"],
        f"{record['successes_since_degradation']} of {needed} clean runs toward reduction",
    )
