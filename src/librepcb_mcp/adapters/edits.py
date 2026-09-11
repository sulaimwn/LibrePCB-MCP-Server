"""One bounded typed-resistance patch; no general design serializer."""

from dataclasses import dataclass
from decimal import Decimal
import re

from librepcb_mcp.adapters.files import Capture
from librepcb_mcp.adapters.project import allowed, inspect_project, unique
from librepcb_mcp.adapters.sexpr import Atom, parse
from librepcb_mcp.errors import ProjectError, require

CIRCUIT_FILE = "circuit/circuit.lp"
RESISTANCE_UNITS = {"microohm", "milliohm", "ohm", "kiloohm", "megaohm"}


@dataclass(frozen=True)
class ResistanceEdit:
    content: bytes
    change: dict


def resistance_edit(captured: Capture, filename: str, component_id: str,
                    new_value: str) -> ResistanceEdit:
    """Change one numeric attribute in its existing unit, preserving all other bytes.

    The model supplies plain decimal text, not unit suffixes, exponent notation,
    expressions or arbitrary S-expressions. A populated part choice is rejected:
    changing a displayed resistance must not silently retain a selected part.
    """
    require(isinstance(new_value, str) and len(new_value) <= 16
            and bool(re.fullmatch(r"(?:0|[1-9][0-9]{0,8})(?:\.[0-9]{1,6})?", new_value)),
            "new_value must be plain nonnegative decimal text in the existing resistance unit.", "invalid_argument")
    number = Decimal(new_value)
    require(number <= Decimal("1000000"), "Resistance value exceeds the experimental range.", "invalid_argument")
    data = inspect_project(captured, filename)
    matches = [c for c in data.components if c["id"] == component_id]
    require(len(matches) == 1, "Unknown component_id for this saved project.", "invalid_argument")
    component = matches[0]
    require(bool(re.fullmatch(r"R[1-9][0-9]*", component["reference"]))
            and component["signal_count"] == 2 and not component["schematic_only"]
            and component["value_raw"] == "{{RESISTANCE}}",
            "Only two-signal resistors using exactly {{RESISTANCE}} are supported.", "unsupported_edit")
    source = captured.files[CIRCUIT_FILE].decode("utf-8")
    node = unique(parse(source).children("component"))[component_id]
    require(node.field("lock_assembly") == "false", "Assembly-locked components are unsupported for value editing.", "unsupported_edit")
    for device in node.children("device"):
        # Only variant membership is accepted; parts and device attributes may
        # encode the existing resistance in procurement data.
        allowed(device, {"variant"}, leading_id=True)
    require(len(node.children("attribute")) == 1,
            "Only a sole typed RESISTANCE attribute is supported; extra attributes need review.", "unsupported_edit")
    attribute = node.one("attribute")
    require(attribute.atom() == "RESISTANCE" and attribute.field("type") == "resistance"
            and attribute.field("unit") in RESISTANCE_UNITS,
            "A supported typed RESISTANCE attribute is required.", "unsupported_edit")
    allowed(attribute, {"type", "unit", "value"}, leading_id=True)
    old_value = attribute.field("value")
    require(bool(re.fullmatch(r"(?:0|[1-9][0-9]{0,8})(?:\.[0-9]{1,6})?", old_value)),
            "Existing resistance is outside the supported decimal subset.", "unsupported_edit")
    require(Decimal(old_value) != number, "The requested resistance is unchanged.", "invalid_argument")
    atom = attribute.one("value").items[0]
    require(isinstance(atom, Atom) and atom.quoted, "Resistance value must be a quoted scalar.", "unsupported_edit")
    replacement = '"' + new_value + '"'
    edited = (source[:atom.start] + replacement + source[atom.end:]).encode("utf-8")
    return ResistanceEdit(edited, {"component_id": component_id, "reference": component["reference"],
        "file": CIRCUIT_FILE, "field": "RESISTANCE", "type": "resistance",
        "unit": attribute.field("unit"), "before": old_value, "after": new_value,
        "value_raw": component["value_raw"], "character_span": [atom.start, atom.end]})


def verify_edit(before: Capture, after: Capture, edit: ResistanceEdit) -> dict:
    """Exact full-project equality except the intended scalar is stronger than counts.

    This preserves every UUID, reference, signal assignment, wire, trace, library
    byte, job, approval and unknown field. Recheck it after LibrePCB saving too.
    """
    expected = {**before.files, CIRCUIT_FILE: edit.content}
    changed = sorted(name for name in before.files.keys() | after.files.keys()
                     if before.files.get(name) != after.files.get(name))
    if after.files != expected:
        raise ProjectError("validation_failed", "Candidate changed outside the intended resistance scalar.",
                           {"changed_files": changed[:20]})
    return {"exact_expected_files": True, "file_count": len(after.files),
            "changed_files": changed, "identifiers_connectivity_geometry_and_other_bytes_preserved": True}
