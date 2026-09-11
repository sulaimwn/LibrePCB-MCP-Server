"""Conservative parser for one verified LibrePCB 2.1.1 ERC or board DRC run."""

from pathlib import Path
import json
import re

from librepcb_mcp.adapters.cli import ProcessResult

MAX_FINDINGS = 50
MAX_FINDING_BYTES = 6_000


def interpret_check(result: ProcessResult, kind: str, project: Path, board: dict | None = None) -> dict:
    record = {"check": kind, "board": board, "outcome": "indeterminate",
              "approved_count": None, "unapproved_count": None, "findings": [],
              "findings_truncated": False, "exit_code": result.exit_code,
              "stdout_artifact": result.stdout_path, "stderr_artifact": result.stderr_path,
              "diagnostic_notes": []}
    if result.outcome != "completed":
        record["diagnostic_notes"].append(result.outcome)
        return record
    try:
        stdout = Path(result.stdout_path).read_text(encoding="utf-8")
        stderr = Path(result.stderr_path).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        record["diagnostic_notes"].append("Diagnostics unavailable or not UTF-8.")
        return record
    lines = [line for line in stdout.splitlines() if line.strip()]
    prefix = [f"Open project '{project}'...", f"Run {kind.upper()}..."]
    indent = "  "
    if kind == "drc":
        prefix.append(f"  Board '{board['name']}':")
        indent = "    "
    if len(lines) != len(prefix) + 3 or lines[:len(prefix)] != prefix:
        record["diagnostic_notes"].append("Unexpected or incomplete stdout; no clean-check conclusion is possible.")
        return record
    approved = re.fullmatch(re.escape(indent) + r"Approved messages: ([0-9]{1,9})", lines[-3])
    unapproved = re.fullmatch(re.escape(indent) + r"Non-approved messages: ([0-9]{1,9})", lines[-2])
    if not approved or not unapproved:
        record["diagnostic_notes"].append("Missing or invalid approved/unapproved counts.")
        return record
    record["approved_count"] = int(approved[1])
    record["unapproved_count"] = int(unapproved[1])
    expected_exit = 1 if record["unapproved_count"] else 0
    expected_ending = "Finished with errors!" if expected_exit else "SUCCESS"
    if result.exit_code != expected_exit or lines[-1] != expected_ending:
        record["diagnostic_notes"].append("Exit status or completion marker contradicts the finding counts.")
    finding_count, used = 0, 0
    for line in stderr.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(re.escape(indent + "  ") + r"- \[(HINT|WARNING|ERROR)\] (.+)", line)
        if not match:
            note = "Unrecognized stderr; see raw diagnostics."
            if note not in record["diagnostic_notes"]:
                record["diagnostic_notes"].append(note)
            continue
        finding_count += 1
        message = match[2]
        finding = {"severity": match[1].lower(), "message": message, "approved": False}
        size = len(json.dumps(finding).encode("utf-8"))
        if len(record["findings"]) < MAX_FINDINGS and used + size <= MAX_FINDING_BYTES and len(message) <= 1500:
            record["findings"].append(finding)
            used += size
        else:
            record["findings_truncated"] = True
    if finding_count != record["unapproved_count"]:
        record["diagnostic_notes"].append("Finding detail count differs from the reported count.")
    record["diagnostic_notes"] = list(dict.fromkeys(record["diagnostic_notes"]))
    if not record["diagnostic_notes"]:
        record["outcome"] = "violations" if expected_exit else "passed"
    return record
