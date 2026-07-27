"""Deterministic capability qualification against a synthetic fixture repository.

Scoring never interprets. Every expectation is an exact comparison, a substring
test, an exclusion test or a digest computed from the fixture at score time, so
the same answers always produce the same result.
"""
from collections import namedtuple
from pathlib import Path

import environment
import toon

Result = namedtuple("Result", "result probes notes")

CONTRACT = ".agents/context/qualification/QUALIFICATION.toon"


def pack(root):
    return toon.loads((Path(root) / CONTRACT).read_text())


def render_pack(pack_data):
    lines = [
        f"QUALIFICATION PACK v{pack_data['version']}",
        "",
        f"fixture       {pack_data['fixture']}",
        "answer schema .agents/context/qualification/answers.schema.toon",
        "score with    .agentic-template/bin/project context qualify --score <answers.toon>",
        "",
        "Answer every probe from the fixture repository only. Scoring is exact.",
        "",
    ]
    for probe in pack_data["probes"]:
        tag = "gating  " if probe["gating"] else "advisory"
        lines.append(f"{tag} {probe['id']}")
        lines.append(f"         {probe['prompt']}")
        lines.append(f"         answer field: {probe['field']}")
        lines.append("")
    return "\n".join(lines)


def _compare(root, fixture, probe, answer, field=None, expect=None, value=None):
    field = field or probe["field"]
    expect = expect or probe["expect"]
    value = value if value is not None else probe["value"]
    given = str(answer.get(field, "")).strip()
    if not given:
        return None
    if expect == "sha256_of_file":
        return given == environment.file_digest(fixture / value)
    if expect == "exact":
        return given == str(value)
    if expect == "contains":
        return str(value) in given
    if expect == "excludes":
        return str(value) not in given
    raise ValueError(f"unknown expectation kind: {expect}")


def score(root, answers):
    """Grade an answers document. Missing or unparseable input is uncertain."""
    contract = pack(root)
    fixture = Path(root) / contract["fixture"]
    body = (answers or {}).get("answers") or {}
    notes = []

    if body.get("qualification_version") != contract["version"]:
        return Result(
            "uncertain",
            {},
            [
                f"answers declare qualification_version "
                f"{body.get('qualification_version')}, contract is {contract['version']}"
            ],
        )

    given = {entry.get("id"): entry for entry in body.get("probes") or []}
    outcomes = {}
    unanswered = []
    for probe in contract["probes"]:
        answer = given.get(probe["id"])
        if answer is None:
            outcomes[probe["id"]] = "unanswered"
            unanswered.append(probe["id"])
            continue
        verdict = _compare(root, fixture, probe, answer)
        if verdict is None:
            outcomes[probe["id"]] = "unanswered"
            unanswered.append(probe["id"])
            continue
        if verdict and probe.get("also"):
            extra = probe["also"]
            verdict = bool(
                _compare(
                    root, fixture, probe, answer, extra["field"], extra["expect"], extra["value"]
                )
            )
        if verdict and probe.get("source_must_exist"):
            source = str(answer.get("source", "")).strip()
            verdict = bool(source) and (fixture / source).exists()
            if not verdict:
                notes.append(f"{probe['id']}: source '{source}' does not resolve in the fixture")
        outcomes[probe["id"]] = "pass" if verdict else "fail"

    if unanswered:
        notes.append("unanswered probes: " + ", ".join(unanswered))
        return Result("uncertain", outcomes, notes)

    failed = [
        probe["id"]
        for probe in contract["probes"]
        if probe["gating"] and outcomes[probe["id"]] == "fail"
    ]
    if failed:
        notes.append("failed gating probes: " + ", ".join(failed))
        return Result("fail", outcomes, notes)
    advisory = [
        probe["id"]
        for probe in contract["probes"]
        if not probe["gating"] and outcomes[probe["id"]] == "fail"
    ]
    if advisory:
        notes.append("advisory probes failed (not gating): " + ", ".join(advisory))
    return Result("pass", outcomes, notes)
