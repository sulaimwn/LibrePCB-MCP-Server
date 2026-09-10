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
from librepcb_mcp.adapters.files import capture, copy_capture, local_absolute, no_links
from librepcb_mcp.adapters.project import ProjectData, inspect_project
from librepcb_mcp.errors import ProjectError, require

TOOLS = ["get_status", "open_project", "get_project_summary", "list_components", "list_nets"]
MAX_PAGE_BYTES = 24_000  # MCP carries both text and structured representations.


@dataclass(frozen=True)
class Snapshot:
    project_id: str
    source: Path
    copy: Path
    revision: str
    captured_at: str
    data: ProjectData


class ProjectService:
    def __init__(self, cli: str, project_roots: list[str], data_root: str, *, timeout: float = 30):
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

    def dispatch(self, operation: str, **arguments) -> dict:
        with self.lock:
            try:
                no_links(self.session_dir)
                require(operation in TOOLS, "Unknown operation.", "invalid_argument")
                result = getattr(self, operation)(**arguments)
                response = {"ok": True, "message": "Saved-project operation completed.", "data": result}
                require(len(json.dumps(response).encode("utf-8")) <= 64_000,
                        "Result exceeds the supported response size.", "resource_limit")
                return response
            except ProjectError as exc:
                return {"ok": False, "error": exc.code, "message": str(exc), "details": exc.details}
            except (OSError, UnicodeError) as exc:
                return {"ok": False, "error": "io_error", "message": "Could not read or store the project snapshot.",
                        "details": {"exception_type": type(exc).__name__}}
            except Exception:
                artifact = self.session_dir / ("error-" + uuid4().hex + ".txt")
                artifact.write_text(traceback.format_exc(), encoding="utf-8")
                return {"ok": False, "error": "internal_error", "message": "An unexpected error occurred.",
                        "details": {"diagnostic_artifact": str(artifact)}}

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
                "librepcb": cli, "tools": TOOLS, "problems": problems,
                "saved_state_only": True, "write_tools": False, "project_root_count": len(self.roots),
                "limits": {"max_page_size": 100, "max_open_attempts_per_session": 32, "max_response_bytes": 64000}}

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
        require(isinstance(project_id, str) and project_id in self.snapshots,
                "Unknown project handle; open the project in this server session.", "invalid_argument")
        snapshot = self.snapshots[project_id]
        self._source(str(snapshot.source))
        require(capture(snapshot.source.parent).revision == snapshot.revision
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
