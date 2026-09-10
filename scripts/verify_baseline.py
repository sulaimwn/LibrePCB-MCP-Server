"""Run Day 1 against the real, pinned LibrePCB binary and CC0 fixture.

Run from the repository: .venv/Scripts/python.exe scripts/verify_baseline.py
This is a development acceptance harness, not a model-facing tool.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import shutil
import struct
import sys
from uuid import uuid4
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from librepcb_mcp.adapters.cli import ProcessRunner


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def manifest(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): digest(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def extract_fixture(archive: Path, destination: Path) -> None:
    """Extract our hash-pinned archive only; reject paths escaping the new copy."""
    with ZipFile(archive) as bundle:
        paths = set()
        if sum(item.file_size for item in bundle.infolist()) > 100_000_000:
            raise ValueError("Fixture exceeds 100 MB extracted limit")
        for item in bundle.infolist():
            target = destination / item.filename
            if not target.resolve().is_relative_to(destination.resolve()):
                raise ValueError("Unsafe archive path")
            if (item.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Archive symlinks are unsupported")
            key = str(target.resolve()).casefold()
            if key in paths:
                raise ValueError("Duplicate archive path")
            paths.add(key)
        destination.mkdir(parents=True, exist_ok=False)
        bundle.extractall(destination)


def main() -> int:
    config = json.loads((ROOT / "toolchain.json").read_text(encoding="utf-8"))
    archive = ROOT / "tests/fixtures/d0-reader.lppz"
    before_archive = digest(archive)
    if before_archive != config["fixture"]["sha256"]:
        raise ValueError("Fixture SHA256 differs from pinned upstream archive")
    executable = ROOT / config["librepcb"]["relative_executable"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "work/runs" / f"baseline-{stamp}-{uuid4().hex[:8]}"
    run_dir.mkdir(parents=True, exist_ok=False)
    runner = ProcessRunner(executable, run_dir / "logs", timeout=60)
    records = []
    checks = []

    def expect(name: str, passed: bool, detail=None):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    def invoke(name: str, *args: str):
        result = runner.run(list(args), cwd=ROOT)
        records.append({"name": name, **result.to_dict()})
        return result

    def completed(result, code=0):
        return result.outcome == "completed" and result.exit_code == code

    version = invoke("version", "--version")
    correct_version = completed(version) and all(
        line in version.stdout_excerpt
        for line in (
            "LibrePCB CLI Version 2.1.1",
            "File Format 2 (stable)",
            "Git Revision 06465bf (2026-06-12)",
        )
    )
    if not correct_version:
        (run_dir / "version-failure.json").write_text(
            json.dumps(version.to_dict(), indent=2), encoding="utf-8"
        )
        raise RuntimeError(f"Missing or unsupported CLI. See {run_dir}")
    expect("pinned_cli_version", correct_version)
    help_result = invoke("open_project_help", "open-project", "--help")
    expect("help_available", completed(help_result))

    design = run_dir / "design"
    extract_fixture(archive, design)
    before = manifest(design)
    project = str(design / "d0-reader.lpp")
    expect("format_2_fixture", (design / ".librepcb-project").read_bytes() == b"2\n")
    loaded = invoke("strict_load", "open-project", "--strict", project)
    expect("strict_load", completed(loaded))

    rules = invoke("erc_drc", "open-project", "--erc", "--drc", project)
    raw_rules = Path(rules.stdout_path).read_text(encoding="utf-8")
    approved = [int(n) for n in re.findall(r"^\s*Approved messages: (\d+)$", raw_rules, re.M)]
    unapproved = [int(n) for n in re.findall(r"^\s*Non-approved messages: (\d+)$", raw_rules, re.M)]
    expect("baseline_erc_drc", completed(rules) and approved == [2, 16] and unapproved == [0, 0],
           {"erc_approved": 2, "drc_approved": 16, "observed_approved": approved,
            "observed_unapproved": unapproved, "note": "Approved findings remain present."})

    exports = run_dir / "exports"
    output = invoke("pdf_gerber_jobs", "open-project", "--run-job", "Schematic PDF",
                    "--run-job", "Gerber/Excellon", "--outdir", str(exports), project)
    pdf = exports / "d0-reader_v2_Schematic.pdf"
    gerbers = sorted((exports / "gerber").glob("*.gbr"))
    drills = sorted((exports / "gerber").glob("*.drl"))
    expect("pdf_export", completed(output) and pdf.is_file() and pdf.read_bytes().startswith(b"%PDF-"))
    expect("manufacturing_exports", completed(output) and len(gerbers) == 9 and len(drills) == 2
           and all(p.stat().st_size > 20 for p in [*gerbers, *drills]),
           {"gerber_count": len(gerbers), "drill_count": len(drills)})

    preview_dir = run_dir / "preview"
    preview = invoke("png_output_job", "open-project", "--jobs", str(ROOT / "resources/preview-jobs.lp"),
                     "--run-job", "Schematic PNG", "--outdir", str(preview_dir), project)
    pngs = sorted(preview_dir.glob("*.png"))
    dimensions = []
    for path in pngs:
        header = path.read_bytes()[:24]
        if header[:8] != b"\x89PNG\r\n\x1a\n" or len(header) < 24:
            dimensions.append([0, 0])
        else:
            dimensions.append(list(struct.unpack(">II", header[16:24])))
    expect("png_preview", completed(preview) and len(pngs) == 2
           and all(100 <= width <= 2500 and 100 <= height <= 2500 for width, height in dimensions),
           {"count": len(pngs), "dimensions": dimensions})

    after = manifest(design)
    expect("all_project_files_unchanged", before == after, {"file_count": len(before)})

    # Re-expose the fixture's two existing approved ERC findings on another copy.
    # This tests the real findings/exit behavior, not newly introduced wiring faults.
    unapproved_design = run_dir / "erc-unapproved"
    shutil.copytree(design, unapproved_design)
    (unapproved_design / "circuit/erc.lp").write_bytes(b"(librepcb_erc\n)\n")
    negative_erc = invoke("unapproved_erc", "open-project", "--erc",
                          str(unapproved_design / "d0-reader.lpp"))
    combined = negative_erc.stdout_excerpt + negative_erc.stderr_excerpt
    expect("unapproved_erc_returns_1", completed(negative_erc, 1)
           and "Non-approved messages: 2" in combined and "[WARNING]" in combined,
           "Existing open-wire approvals removed only in the disposable negative-test copy.")

    malformed_design = run_dir / "malformed"
    shutil.copytree(design, malformed_design)
    (malformed_design / "circuit/circuit.lp").write_bytes(b"(librepcb_circuit\n")
    malformed = invoke("malformed_project", "open-project", "--erc",
                       str(malformed_design / "d0-reader.lpp"))
    expect("malformed_project_returns_1", completed(malformed, 1)
           and "Non-approved messages:" not in malformed.stdout_excerpt
           and bool(malformed.stderr_excerpt.strip()),
           "Same exit code as ERC findings: consumers must not classify by exit code alone.")

    expect("original_archive_unchanged", digest(archive) == before_archive)
    expect("baseline_copy_still_unchanged", manifest(design) == before)
    artifacts = []
    for directory in (exports, preview_dir):
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                artifacts.append({"path": str(path), "bytes": path.stat().st_size,
                                  "sha256": digest(path)})
    report = {
        "timestamp_utc": stamp,
        "kind": "real_librepcb_cli_integration_baseline",
        "passed": all(check["passed"] for check in checks),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "fixture_sha256": before_archive,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(before, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "checks": checks,
        "commands": records,
        "artifacts": artifacts,
        "limits": [
            "No MCP handshake or registered tools yet.",
            "No interactive LibrePCB GUI inspection or design editing tested.",
            "PNG size and report-count expectations are specific to this pinned fixture.",
            "Negative ERC probe exposes existing approvals; it does not create a new design fault.",
        ],
    }
    # Keep evidence portable: paths below <REPO> refer to this project directory.
    report_text = json.dumps(report, indent=2).replace(
        json.dumps(str(ROOT))[1:-1], "<REPO>"
    )
    report_path = run_dir / "report.json"
    report_path.write_text(report_text + "\n", encoding="utf-8")
    (run_dir / "source-manifest.json").write_text(json.dumps(before, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checks": checks, "report": str(report_path)}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
