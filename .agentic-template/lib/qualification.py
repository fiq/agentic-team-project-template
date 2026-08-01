"""Deterministic capability qualification against a synthetic fixture repository.

Scoring never interprets. Every expectation is an exact comparison, a substring
test, an exclusion test or a value derived from the fixture at score time, so
the same answers always produce the same result.

The scoring config (QUALIFICATION.toon) holds only pointers into the fixture --
which file, which key, which trigger -- never a stored answer. An expected
value that lived in the scoring config would let an agent pass by reading the
config instead of the fixture; deriving every expectation at score time closes
that shortcut. The one exception is `progressive_disclosure`, whose literal
`value` is an exclusion: knowing it leaks nothing, since the probe only checks
that the value is absent from the answer.
"""
from collections import namedtuple
from pathlib import Path

import environment
import toon

Result = namedtuple("Result", "result probes notes")

CONTRACT = ".agents/context/qualification/QUALIFICATION.toon"

DERIVED_EXPECTATIONS = ("sha256_of_file", "catalog_path_for_trigger", "toon_value")


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


def _derive(fixture, probe, expect, source):
    """Compute a probe's expected value from the fixture at score time."""
    if expect == "sha256_of_file":
        return environment.file_digest(fixture / source)
    if expect == "catalog_path_for_trigger":
        catalog = toon.loads((fixture / ".agents/skills/CATALOG.toon").read_text())
        for entry in catalog["skills"].values():
            if entry.get("trigger") == source:
                return entry["path"]
        raise ValueError(f"fixture catalog has no trigger {source}")
    if expect == "toon_value":
        relative, _, dotted = str(source).partition("#")
        node = toon.loads((fixture / relative).read_text())
        for part in dotted.split("."):
            node = node[part]
        return str(node)
    raise ValueError(f"unknown derivation: {expect}")


def _compare(fixture, probe, answer):
    field = probe["field"]
    expect = probe["expect"]
    given = str(answer.get(field, "")).strip()
    if not given:
        return None
    if expect in DERIVED_EXPECTATIONS:
        return given == _derive(fixture, probe, expect, probe["source"])
    if expect == "exact":
        return given == str(probe["value"])
    if expect == "contains":
        return str(probe["value"]) in given
    if expect == "excludes":
        return str(probe["value"]) not in given
    raise ValueError(f"unknown expectation kind: {expect}")


def _cites_a_file_containing(fixture, answer, field, expected):
    """True when `answer[field]` names a real fixture file that contains `expected`.

    Used for checks that an evidence citation is honest, not merely present: the
    named file must exist AND its content must actually contain the correct
    answer, so a real-but-wrong file or an unsourced claim both fail.

    P2: the cited path must resolve inside the fixture directory (no traversal
    out via ``..`` or absolute paths) and must be a regular file, not a
    directory.
    """
    claimed = str(answer.get(field, "")).strip()
    if not claimed:
        return False
    candidate = (fixture / claimed).resolve()
    fixture_resolved = fixture.resolve()
    try:
        candidate.relative_to(fixture_resolved)
    except ValueError:
        return False
    return candidate.is_file() and expected in candidate.read_text()


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
        verdict = _compare(fixture, probe, answer)
        if verdict is None:
            outcomes[probe["id"]] = "unanswered"
            unanswered.append(probe["id"])
            continue
        if verdict and probe.get("source_must_contain_answer"):
            expected = _derive(fixture, probe, probe["expect"], probe["source"])
            verdict = _cites_a_file_containing(fixture, answer, "source", expected)
            if not verdict:
                notes.append(
                    f"{probe['id']}: cited source does not contain the expected answer"
                )
        if verdict and probe.get("also"):
            extra = probe["also"]
            if extra["expect"] != "file_containing_answer":
                raise ValueError(f"unknown 'also' expectation kind: {extra['expect']}")
            expected = _derive(fixture, probe, probe["expect"], probe["source"])
            verdict = _cites_a_file_containing(fixture, answer, extra["field"], expected)
            if not verdict:
                notes.append(
                    f"{probe['id']}: {extra['field']} does not name a file containing "
                    f"the expected answer"
                )
        outcomes[probe["id"]] = "pass" if verdict else "fail"

    failed = [
        probe["id"]
        for probe in contract["probes"]
        if probe["gating"] and outcomes.get(probe["id"]) == "fail"
    ]
    if failed:
        notes.append("failed gating probes: " + ", ".join(failed))
        if unanswered:
            notes.append("also unanswered: " + ", ".join(unanswered))
        return Result("fail", outcomes, notes)

    if unanswered:
        notes.append("unanswered probes: " + ", ".join(unanswered))
        return Result("uncertain", outcomes, notes)

    advisory = [
        probe["id"]
        for probe in contract["probes"]
        if not probe["gating"] and outcomes[probe["id"]] == "fail"
    ]
    if advisory:
        notes.append("advisory probes failed (not gating): " + ", ".join(advisory))
    return Result("pass", outcomes, notes)
