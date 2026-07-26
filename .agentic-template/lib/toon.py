"""Reader and writer for the TOON subset used by template control files.

Supported:
    key: value            scalar (string, int, true, false, null)
    key: "quoted"         string kept verbatim, colons allowed
    key:                  nested map, indented by two spaces
    key: []  /  key: {}   empty list / empty map
    key: [a, b, c]        inline list of scalars
    key:                  block list, items indented by two spaces
      - scalar
      - key: value        list of maps; continuation keys align under the key
        other: value

Not supported: anchors, multi-line strings, inline maps with content, tabs.

Lenient by design:
    Duplicate keys resolve last-wins; earlier values with the same key are
    silently overwritten.
    Unterminated quotes are treated as literal characters (e.g., "a: b is
    accepted as the string "a: b without raising an error).
    Emitted strings that need quoting are backslash-escaped (backslashes and
    double quotes), so a round trip through dumps() then loads() preserves
    quote and backslash characters exactly.
"""
import re

_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*$")
_INT = re.compile(r"-?\d+$")


class ToonError(ValueError):
    """Raised with a line number whenever input leaves the supported subset."""


def _unescape(text):
    out = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            out.append(text[index + 1])
            index += 2
            continue
        out.append(char)
        index += 1
    return "".join(out)


def _scalar(raw):
    text = raw.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return _unescape(text[1:-1])
    if text == "null":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if _INT.match(text):
        return int(text)
    return text


def _split_key(text):
    """Return (key, rest) when text opens a mapping entry, else None."""
    key, separator, rest = text.partition(":")
    if not separator or not _KEY.match(key.strip()):
        return None
    if rest.startswith("//"):
        return None
    return key.strip(), rest.strip()


def _significant_lines(text):
    lines = []
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        leading = raw[:len(raw) - len(raw.lstrip(" \t"))]
        if "\t" in leading:
            raise ToonError(f"line {number}: tabs are not supported; use spaces only")
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise ToonError(f"line {number}: indent {indent} is not a multiple of two")
        lines.append((indent, stripped, number))
    return lines


def _parse_value(lines, index, indent, key_rest):
    """Resolve the value for a mapping entry. Returns (value, next_index)."""
    if key_rest == "[]":
        return [], index
    if key_rest == "{}":
        return {}, index
    if key_rest.startswith("[") and key_rest.endswith("]"):
        body = key_rest[1:-1].strip()
        return ([_scalar(part) for part in body.split(",")] if body else []), index
    if key_rest:
        return _scalar(key_rest), index
    child = indent + 2
    if index < len(lines) and lines[index][0] == child:
        if lines[index][1].startswith("- "):
            return _parse_list(lines, index, child)
        return _parse_map(lines, index, child)
    if index < len(lines) and lines[index][0] > indent:
        raise ToonError(f"line {lines[index][2]}: unexpected indent")
    return {}, index


def _parse_map(lines, index, indent):
    result = {}
    while index < len(lines):
        line_indent, text, number = lines[index]
        if line_indent < indent or text.startswith("- "):
            break
        if line_indent > indent:
            raise ToonError(f"line {number}: unexpected indent")
        entry = _split_key(text)
        if entry is None:
            raise ToonError(f"line {number}: expected 'key: value'")
        key, rest = entry
        index += 1
        result[key], index = _parse_value(lines, index, indent, rest)
    return result, index


def _parse_list(lines, index, indent):
    result = []
    while index < len(lines):
        line_indent, text, number = lines[index]
        if line_indent < indent or not text.startswith("- "):
            break
        if line_indent > indent:
            raise ToonError(f"line {number}: unexpected indent")
        body = text[2:].strip()
        index += 1
        entry = _split_key(body)
        if entry is None:
            result.append(_scalar(body))
            continue
        key, rest = entry
        item = {}
        item[key], index = _parse_value(lines, index, indent + 2, rest)
        continuation, index = _parse_map(lines, index, indent + 2)
        item.update(continuation)
        result.append(item)
    return result, index


def loads(text):
    """Parse TOON text into Python data. Raises ToonError with a line number."""
    lines = _significant_lines(text)
    value, index = _parse_map(lines, 0, 0)
    if index != len(lines):
        raise ToonError(f"line {lines[index][2]}: unexpected content")
    return value


def _needs_quoting(text):
    """True when emitting text bare would read back as something else."""
    if text == "" or text.strip() != text or ":" in text:
        return True
    if text[0] in "[{\"'":
        return True
    return _scalar(text) != text


def _quote(text):
    """Wrap in double quotes, escaping backslashes and quotes losslessly."""
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return '"' + escaped + '"'


def _emit_scalar(value):
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if _needs_quoting(text):
        return _quote(text)
    return text


def _emit(value, indent, out):
    pad = " " * indent
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, dict) and child:
                out.append(f"{pad}{key}:")
                _emit(child, indent + 2, out)
            elif isinstance(child, dict):
                out.append(f"{pad}{key}: {{}}")
            elif isinstance(child, list) and child:
                out.append(f"{pad}{key}:")
                _emit(child, indent + 2, out)
            elif isinstance(child, list):
                out.append(f"{pad}{key}: []")
            else:
                out.append(f"{pad}{key}: {_emit_scalar(child)}")
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                keys = list(item)
                first = keys[0]
                head = item[first]
                if isinstance(head, (dict, list)) and head:
                    out.append(f"{pad}- {first}:")
                    _emit(head, indent + 4, out)
                else:
                    out.append(f"{pad}- {first}: {_emit_scalar(head)}")
                _emit({key: item[key] for key in keys[1:]}, indent + 2, out)
            else:
                out.append(f"{pad}- {_emit_scalar(item)}")


def dumps(value):
    """Emit TOON text for data that stays inside the supported subset."""
    out = []
    _emit(value, 0, out)
    return "\n".join(out) + "\n"
