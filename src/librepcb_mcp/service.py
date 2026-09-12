"""Saved-design operations, independent of MCP transport and model APIs."""

from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import threading
import traceback
from uuid import uuid4

from librepcb_mcp import __version__
from librepcb_mcp.adapters.cli import ProcessRunner
from librepcb_mcp.adapters.checks import interpret_check
from librepcb_mcp.adapters.edits import CIRCUIT_FILE, resistance_edit, verify_edit, verify_save_initialization
from librepcb_mcp.adapters.exports import Artifact, JOB_NAMES, collect_artifacts, image_bytes, job_text
from librepcb_mcp.adapters.files import capture, copy_capture, local_absolute, no_links
from librepcb_mcp.adapters.project import ProjectData, inspect_project
from librepcb_mcp.adapters.reports import write_json
from librepcb_mcp.errors import ProjectError, require
from librepcb_mcp.operations import checkpoint, operation_scope, validate_timeout

TOOLS = ["get_status", "open_project", "get_project_summary", "list_components", "list_nets",
         "run_checks", "export_preview", "run_output_job"]
MAX_PAGE_BYTES = 24_000  # MCP carries both text and structured representations.


@dataclass(frozen=True)
class Snapshot:
    project_id: str
    source: Path
    copy: Path
    revision: str
    captured_at: str
    data: ProjectData
    source_revision: str | None = None


class ProjectService:
    def __init__(self, cli: str, project_roots: list[str], data_root: str, *, timeout: float = 30,
                 experimental_edits: bool = False, operation_timeout: float | None = None):
        self.operation_timeout = operation_timeout if operation_timeout is not None else (240 if experimental_edits else 90)
        validate_timeout(self.operation_timeout)
        require(bool(project_roots), "At least one project root is required.", "invalid_argument")
        self.roots = tuple(local_absolute(root) for root in project_roots)
        require(all(root.is_dir() for root in self.roots), "Configured project roots must exist.", "invalid_argument")
        base = local_absolute(data_root)
        base.mkdir(parents=True, exist_ok=True)
        no_links(base)
        self.session_dir = base / ("s-" + uuid4().hex[:12])
        self.session_dir.mkdir()
        self.data_root = base
        self.runner = ProcessRunner(local_absolute(cli), self.session_dir / "logs", timeout=timeout)
        self.lock = threading.RLock()
        self.snapshots: dict[str, Snapshot] = {}
        self.open_attempts = 0
        self.operation_count = 0
        self.artifacts: dict[str, Artifact] = {}
        self.experimental_edits = experimental_edits
        self.tools = [*TOOLS, *(["create_value_edit"] if experimental_edits else [])]
        self.edit_attempts = 0

    def dispatch(self, operation: str, *, _cancel_check=None, **arguments) -> dict:
        with operation_scope(self.operation_timeout, _cancel_check):
            acquired = False
            successful = False
            snapshots_before, artifacts_before = set(), set()
            try:
                # The same budget includes queueing; cancelled queued requests
                # cannot acquire the writer lock later and start an edit.
                while not acquired:
                    checkpoint()
                    acquired = self.lock.acquire(timeout=.05)
                snapshots_before, artifacts_before = set(self.snapshots), set(self.artifacts)
                checkpoint()
                no_links(self.session_dir)
                require(operation in self.tools, "Unknown operation.", "invalid_argument")
                result = getattr(self, operation)(**arguments)
                response = {"ok": True, "message": "Saved-project operation completed.", "data": result}
                require(len(json.dumps(response).encode("utf-8")) <= 64_000,
                        "Result exceeds the supported response size.", "resource_limit")
                checkpoint()
                successful = True
                return response
            except ProjectError as exc:
                return {"ok": False, "error": exc.code, "message": str(exc), "details": exc.details}
            except (OSError, UnicodeError) as exc:
                return {"ok": False, "error": "io_error", "message": "Could not read or store the project snapshot.",
                        "details": {"exception_type": type(exc).__name__}}
            except Exception:
                artifact = self.session_dir / ("error-" + uuid4().hex + ".txt")
                details = {}
                try:
                    no_links(artifact)
                    with artifact.open("x", encoding="utf-8") as stream:
                        stream.write(traceback.format_exc())
                    details["diagnostic_artifact"] = str(artifact)
                except (OSError, ProjectError) as exc:
                    details["diagnostic_write_error"] = type(exc).__name__
                return {"ok": False, "error": "internal_error", "message": "An unexpected error occurred.",
                        "details": details}
            finally:
                if acquired:
                    if not successful:
                        for key in self.snapshots.keys() - snapshots_before:
                            self.snapshots.pop(key)
                        for key in self.artifacts.keys() - artifacts_before:
                            self.artifacts.pop(key)
                    self.lock.release()

    def _cli_version(self) -> dict:
        no_links(self.runner.executable)
        result = self.runner.run(["--version"], cwd=self.session_dir)
        diagnostics = {"stdout_artifact": result.stdout_path, "stderr_artifact": result.stderr_path}
        if result.outcome != "completed":
            raise ProjectError(result.outcome, result.error or "LibrePCB could not start.", diagnostics)
        if result.exit_code != 0:
            raise ProjectError("process_failed", "LibrePCB version detection failed.", diagnostics)
        lines = result.stdout_excerpt.splitlines()
        if "LibrePCB CLI Version 2.1.1" not in lines or "File Format 2 (stable)" not in lines:
            raise ProjectError("unsupported_version", "This server requires LibrePCB 2.1.1 with stable file format 2.", diagnostics)
        return {"version": "2.1.1", "file_format": "2", "version_output": result.stdout_excerpt, **diagnostics}

    def get_status(self) -> dict:
        try:
            cli = self._cli_version()
            problems = []
        except ProjectError as exc:
            cli = None
            problems = [{"code": exc.code, "message": str(exc), "details": exc.details}]
        return {"server_version": __version__, "mcp_sdk_version": version("mcp"), "ready": not problems,
                "librepcb": cli, "tools": self.tools, "problems": problems,
                "saved_state_only": True, "write_tools": self.experimental_edits,
                "experimental_edits": self.experimental_edits, "project_root_count": len(self.roots),
                "output_jobs": ["schematic_pdf", "gerber_excellon"],
                "limits": {"max_page_size": 100, "max_open_attempts_per_session": 32,
                           "max_check_export_operations": 64, "max_edit_attempts": 8, "max_response_bytes": 64000,
                           "operation_timeout_seconds": self.operation_timeout, "cli_timeout_seconds": self.runner.timeout,
                           "max_preview_wire_bytes": 1500000, "max_log_bytes_per_stream": self.runner.max_log_bytes}}

    def _source(self, value: str) -> Path:
        path = local_absolute(value)
        require(any(path.is_relative_to(root) for root in self.roots),
                "Project is outside the configured roots.", "path_not_allowed")
        require(path.suffix.lower() == ".lpp" and path.is_file(),
                "Pass an existing extracted .lpp project file; archives are not supported here.", "invalid_project")
        require(not self.data_root.is_relative_to(path.parent) and not path.is_relative_to(self.data_root),
                "Project and server data directories must not overlap.", "path_not_allowed")
        return path

    def open_project(self, path: str) -> dict:
        source = self._source(path)
        first = capture(source.parent)
        parsed = inspect_project(first, source.name)
        self._cli_version()
        require(self.open_attempts < 32, "Session snapshot limit reached; restart the server.", "resource_limit")
        self.open_attempts += 1
        identifier = uuid4().hex
        destination = self.session_dir / f"p{self.open_attempts:02d}"
        copy_capture(first, destination)
        result = self.runner.run(["open-project", str(destination / source.name)], cwd=self.session_dir)
        if result.outcome != "completed":
            raise ProjectError(result.outcome, result.error or "LibrePCB could not open the snapshot.",
                               {"stdout_artifact": result.stdout_path, "stderr_artifact": result.stderr_path})
        if result.exit_code != 0:
            raise ProjectError("invalid_project", "LibrePCB rejected the saved project snapshot.",
                               {"exit_code": result.exit_code, "stdout_artifact": result.stdout_path,
                                "stderr_artifact": result.stderr_path})
        require(capture(source.parent).revision == first.revision and capture(destination).revision == first.revision,
                "Project changed while opening. Close it and open a fresh snapshot.", "stale_revision")
        snapshot = Snapshot(identifier, source, destination, first.revision,
                            datetime.now(timezone.utc).isoformat(), parsed)
        self.snapshots[identifier] = snapshot
        return self._summary(snapshot)

    def _snapshot(self, project_id: str) -> Snapshot:
        checkpoint()
        require(isinstance(project_id, str) and project_id in self.snapshots,
                "Unknown project handle; open the project in this server session.", "invalid_argument")
        snapshot = self.snapshots[project_id]
        self._source(str(snapshot.source))
        require(capture(snapshot.source.parent).revision == (snapshot.source_revision or snapshot.revision)
                and capture(snapshot.copy).revision == snapshot.revision,
                "Source or snapshot changed. Open the project again for current data.", "stale_revision")
        return snapshot

    @staticmethod
    def _summary(snapshot: Snapshot) -> dict:
        return {"project_id": snapshot.project_id, "revision": snapshot.revision,
                "state": "saved_snapshot", "captured_at": snapshot.captured_at, "lock_present": False,
                "metadata": snapshot.data.metadata, "file_format": "2",
                "boards": snapshot.data.boards, "schematics": snapshot.data.schematics,
                "component_count": len(snapshot.data.components), "net_count": len(snapshot.data.nets),
                "snapshot_project": str(snapshot.copy / snapshot.source.name),
                "is_edit_candidate": snapshot.source_revision is not None,
                "source_revision": snapshot.source_revision or snapshot.revision,
                "inspection_scope": "Circuit components, raw values/attributes, and net signal counts; no geometry or resolved display values."}

    def get_project_summary(self, project_id: str) -> dict:
        return self._summary(self._snapshot(project_id))

    def _page(self, project_id: str, cursor: str | None, limit: int, kind: str) -> dict:
        require(type(limit) is int and 1 <= limit <= 100, "limit must be an integer between 1 and 100.", "invalid_argument")
        snapshot = self._snapshot(project_id)
        offset = 0
        if cursor is not None:
            require(isinstance(cursor, str) and len(cursor) <= 128, "Invalid cursor.", "invalid_argument")
            parts = cursor.split(":")
            require(len(parts) == 3 and parts[:2] == [project_id, kind] and parts[2].isascii()
                    and parts[2].isdigit(), "Cursor belongs to another project or list.", "invalid_argument")
            offset = int(parts[2])
        records = getattr(snapshot.data, kind)
        require(offset <= len(records), "Cursor offset is out of range.", "invalid_argument")
        items = []
        used = 0
        for record in records[offset:offset + limit]:
            size = len(json.dumps(record).encode("utf-8")) + 2
            require(size <= MAX_PAGE_BYTES, "One record exceeds the supported page size.", "resource_limit")
            if used + size > MAX_PAGE_BYTES:
                break
            items.append(record)
            used += size
        end = offset + len(items)
        return {"project_id": project_id, "revision": snapshot.revision, "state": "saved_snapshot",
                "items": items, "total": len(records),
                "next_cursor": f"{project_id}:{kind}:{end}" if end < len(records) else None}

    def list_components(self, project_id: str, cursor: str | None = None, limit: int = 50) -> dict:
        return self._page(project_id, cursor, limit, "components")

    def list_nets(self, project_id: str, cursor: str | None = None, limit: int = 50) -> dict:
        return self._page(project_id, cursor, limit, "nets")

    @staticmethod
    def _board(snapshot: Snapshot, board_id: str | None) -> tuple[int, dict]:
        boards = snapshot.data.boards
        require(bool(boards), "This project has no board.", "invalid_argument")
        if board_id is None:
            require(len(boards) == 1, "Select board_id explicitly for a project with multiple boards.", "invalid_argument")
            return 0, boards[0]
        for index, board in enumerate(boards):
            if board["id"] == board_id:
                return index, board
        raise ProjectError("invalid_argument", "Unknown board_id for this saved project.")

    def _operation_directory(self) -> Path:
        checkpoint()
        require(self.operation_count < 64, "Session check/export limit reached; restart the server.", "resource_limit")
        self.operation_count += 1
        directory = self.session_dir / f"r{self.operation_count:03d}"
        no_links(directory)
        directory.mkdir(exist_ok=False)
        return directory

    @staticmethod
    def _diagnostics(result) -> dict:
        return {"stdout_artifact": result.stdout_path, "stderr_artifact": result.stderr_path,
                "exit_code": result.exit_code, "process_outcome": result.outcome}

    def run_checks(self, project_id: str, checks: str = "both", board_id: str | None = None) -> dict:
        require(checks in {"erc", "drc", "both"}, "checks must be erc, drc or both.", "invalid_argument")
        require(checks != "erc" or board_id is None, "ERC applies to the circuit; omit board_id.", "invalid_argument")
        snapshot = self._snapshot(project_id)
        selected = self._board(snapshot, board_id) if checks != "erc" else None
        directory = self._operation_directory()
        self._cli_version()
        project = snapshot.copy / snapshot.source.name
        reports = []
        for kind in (["erc", "drc"] if checks == "both" else [checks]):
            args = ["open-project", f"--{kind}"]
            board = None
            if kind == "drc":
                index, board = selected
                args.extend(["--board-index", str(index)])
            args.append(str(project))
            result = self.runner.run(args, cwd=self.session_dir)
            report = interpret_check(result, kind, project, board)
            reports.append(report)
            # Also recheck on failures: a concurrent saved change invalidates this result.
            self._snapshot(project_id)
            if report["outcome"] == "indeterminate":
                artifact = directory / "checks.json"
                code = result.outcome if result.outcome != "completed" else "check_failed"
                details = {"checks": reports}
                try:
                    write_json(artifact, reports)
                    details["report_artifact"] = str(artifact)
                except (OSError, ProjectError) as storage_error:
                    details["report_write_error"] = type(storage_error).__name__
                raise ProjectError(code, "A rule check could not be interpreted reliably; no pass is claimed.",
                                   details)
        record = {"project_id": project_id, "revision": snapshot.revision, "state": "saved_snapshot",
                  "outcome": "violations" if any(r["outcome"] == "violations" for r in reports) else "passed",
                  "approved_count": sum(r["approved_count"] for r in reports),
                  "unapproved_count": sum(r["unapproved_count"] for r in reports), "checks": reports,
                  "approval_details_available": False}
        artifact = directory / "checks.json"
        checkpoint()
        write_json(artifact, record)
        record["report_artifact"] = str(artifact)
        return record

    def _export(self, snapshot: Snapshot, kind: str, board_id: str | None = None) -> dict:
        directory = self._operation_directory()
        output = directory / "files"
        output.mkdir(exist_ok=False)
        jobs = directory / "jobs.lp"
        with jobs.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(job_text(kind, board_id))
        self._cli_version()
        project = snapshot.copy / snapshot.source.name
        result = self.runner.run(["open-project", "--jobs", str(jobs), "--run-job", JOB_NAMES[kind],
                                  "--outdir", str(output), str(project)], cwd=self.session_dir)
        self._snapshot(snapshot.project_id)
        diagnostics = self._diagnostics(result)
        if result.outcome != "completed":
            raise ProjectError(result.outcome, "Export did not complete.", diagnostics)
        stdout = Path(result.stdout_path).read_text(encoding="utf-8")
        lines = stdout.splitlines()
        prefix = [f"Open project '{project}'...", f"Run output job '{JOB_NAMES[kind]}'..."]
        if not (result.exit_code == 0 and len(lines) >= 4 and lines[:2] == prefix and lines[-1] == "SUCCESS"
                and all(line.startswith("  => '") and line.endswith("'") for line in lines[2:-1])
                and not Path(result.stderr_path).stat().st_size):
            raise ProjectError("export_failed", "Export reported an error or unfamiliar diagnostics; inspect the raw logs.", diagnostics)
        for line in lines[2:-1]:
            declared = Path(line[6:-1])
            if not declared.is_absolute() or not declared.is_relative_to(output):
                raise ProjectError("invalid_export", "An output artifact was declared outside the export directory.", diagnostics)
        try:
            artifacts = collect_artifacts(output, kind, len(snapshot.data.schematics))
        except ProjectError as exc:
            raise ProjectError(exc.code, str(exc), diagnostics) from exc
        record = {"project_id": snapshot.project_id, "revision": snapshot.revision, "state": "saved_snapshot",
                  "job": kind, "board_id": board_id, "artifacts": [a.public() for a in artifacts],
                  "output_directory": str(output), "diagnostics": diagnostics}
        manifest = directory / "artifacts.json"
        checkpoint()
        write_json(manifest, record)
        record["manifest_artifact"] = str(manifest)
        self.artifacts.update({a.identifier: a for a in artifacts})
        return record

    def export_preview(self, project_id: str, schematic_id: str | None = None) -> dict:
        snapshot = self._snapshot(project_id)
        pages = snapshot.data.schematics
        require(bool(pages), "Project has no schematics.", "invalid_argument")
        selected = next((i for i, page in enumerate(pages) if page["id"] == schematic_id), None) if schematic_id is not None else 0
        require(selected is not None, "Unknown schematic_id for this project.", "invalid_argument")
        record = self._export(snapshot, "schematic_png")
        filename = "schematic.png" if len(pages) == 1 else f"schematic{selected+1}.png"
        image = next(a for a in record["artifacts"] if a["filename"] == filename)
        record.update({"selected_schematic": pages[selected], "image_artifact_id": image["artifact_id"],
                       "image_note": "One selected schematic is attached as an MCP image; all generated pages are listed as artifacts."})
        return record

    def get_preview_image(self, artifact_id: str) -> bytes:
        """Internal transport helper; not a general file-reading MCP tool."""
        with self.lock:
            require(artifact_id in self.artifacts, "Unknown preview artifact.", "invalid_argument")
            return image_bytes(self.artifacts[artifact_id])

    def run_output_job(self, project_id: str, job_name: str, board_id: str | None = None) -> dict:
        require(job_name in {"schematic_pdf", "gerber_excellon"},
                "Supported jobs are schematic_pdf and gerber_excellon.", "invalid_argument")
        snapshot = self._snapshot(project_id)
        if job_name == "gerber_excellon":
            _, board = self._board(snapshot, board_id)
            board_id = board["id"]
        else:
            require(board_id is None and bool(snapshot.data.schematics),
                    "Schematic PDF requires schematics and does not take board_id.", "invalid_argument")
        return self._export(snapshot, job_name, board_id)

    def create_value_edit(self, project_id: str, component_id: str, new_value: str,
                          expected_revision: str) -> dict:
        require(self.experimental_edits, "Experimental editing is not enabled.", "unsupported_edit")
        snapshot = self._snapshot(project_id)
        require(expected_revision == snapshot.revision, "Expected source revision does not match.", "stale_revision")
        require(snapshot.source_revision is None, "Chaining edits on a candidate is not supported.", "unsupported_edit")
        require(len(snapshot.data.boards) == 1, "Experimental value edits require exactly one board.", "unsupported_edit")
        original = capture(snapshot.copy)
        # Reject unsupported values/components before any candidate or CLI save.
        edit = resistance_edit(original, snapshot.source.name, component_id, new_value)
        require(self.edit_attempts < 8, "Session edit limit reached; restart the server.", "resource_limit")
        require(self.operation_count <= 62, "Two check operations are required for an edit; session limit reached.", "resource_limit")
        self.edit_attempts += 1
        directory = self.session_dir / f"e{self.edit_attempts:02d}"
        no_links(directory)
        directory.mkdir(exist_ok=False)
        report_path = directory / "edit.json"
        record = {"outcome": "pending", "source_project_id": project_id, "source_revision": snapshot.revision,
                  "change": edit.change, "cli_roundtrip": [], "operation_directory": str(directory)}
        identifier = None

        def cli_step(folder: Path, flags: list[str]):
            self._snapshot(project_id)
            capture(folder)  # refuse locks/recovery/linked files before invoking LibrePCB
            result = self.runner.run(["open-project", *flags, str(folder / snapshot.source.name)], cwd=self.session_dir)
            record["cli_roundtrip"].append({"flags": flags, **self._diagnostics(result)})
            self._snapshot(project_id)
            if result.outcome != "completed" or result.exit_code != 0 or Path(result.stderr_path).stat().st_size:
                raise ProjectError(result.outcome if result.outcome != "completed" else "validation_failed",
                                   "Candidate save/reopen validation failed.", self._diagnostics(result))
            return capture(folder)

        try:
            # Durable intent before starting native operations. A process crash
            # can leave this and partial copies; it never makes a usable handle.
            write_json(directory / "started.json", record)
            baseline = self.run_checks(project_id)
            record["baseline_checks"] = baseline
            require(baseline["outcome"] == "passed", "Resolve unapproved findings before experimental value editing.", "validation_failed")
            control = directory / "b"
            candidate = directory / "c"
            copy_capture(original, control)
            saved = cli_step(control, ["--save"])
            record["generated_preference_files"] = verify_save_initialization(original, saved, snapshot.source.name)
            # The saved, unedited control is the exact reference for every other
            # byte, including newly initialized preferences and all approvals.
            edit = resistance_edit(saved, snapshot.source.name, component_id, new_value)
            copy_capture(saved, candidate)
            (candidate / CIRCUIT_FILE).write_bytes(edit.content)
            verify_edit(saved, capture(candidate), edit)
            for flags in (["--strict"], ["--save"], ["--strict"]):
                current = cli_step(candidate, flags)
                record["invariants"] = verify_edit(saved, current, edit)
            identifier = uuid4().hex
            candidate_snapshot = Snapshot(identifier, snapshot.source, candidate, current.revision,
                datetime.now(timezone.utc).isoformat(), inspect_project(current, snapshot.source.name), snapshot.revision)
            self.snapshots[identifier] = candidate_snapshot
            checked = self.run_checks(identifier)
            record["candidate_checks"] = checked
            signature = lambda result: [(c["check"], c["approved_count"], c["unapproved_count"], c["findings"])
                                        for c in result["checks"]]
            require(checked["outcome"] == "passed" and signature(checked) == signature(baseline),
                    "Candidate findings differ from the source baseline.", "validation_failed")
            verify_edit(saved, capture(candidate), edit)
            self._snapshot(project_id)
            record["outcome"] = "validated_candidate"
            record["candidate"] = self._summary(candidate_snapshot)
            record["rollback"] = "Original was never modified. Close the candidate and discard its copy to abandon this edit."
            record["experimental"] = True
            record["report_artifact"] = str(report_path)
            checkpoint()
            write_json(report_path, record)
            return record
        except BaseException as exc:
            if identifier is not None:
                self.snapshots.pop(identifier, None)
            code = getattr(exc, "code", "io_error" if isinstance(exc, OSError) else "internal_error")
            record.pop("candidate", None)
            record.pop("report_artifact", None)
            record.update(outcome="failed", error=code, message=str(exc)[:1000])
            details = {**getattr(exc, "details", {}), "operation_directory": str(directory)}
            try:
                failure_path = directory / "failure.json"
                write_json(failure_path, record)
                details["report_artifact"] = str(failure_path)
            except (OSError, ProjectError) as storage_error:
                details["report_write_error"] = type(storage_error).__name__
            if not isinstance(exc, Exception):
                raise
            raise ProjectError(code, str(exc)[:1000], details) from exc
