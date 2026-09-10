"""Allowlisted local paths and consistent, bounded saved-project snapshots."""

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path, PurePosixPath
import stat

from librepcb_mcp.errors import ProjectError, require

MAX_FILE_BYTES = 16_000_000
MAX_PROJECT_BYTES = 100_000_000
MAX_ENTRIES = 5000
VCS_DIRS = {".git", ".hg", ".svn"}


def no_links(path: Path) -> None:
    """Reject all symlinks/junctions/reparse points along an existing path."""
    for part in (path, *path.parents):
        if os.path.lexists(part):
            info = part.lstat()
            require(not stat.S_ISLNK(info.st_mode)
                    and not (getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT),
                    "Linked paths and Windows reparse points are unsupported.", "path_not_allowed")


def local_absolute(value: str) -> Path:
    require(isinstance(value, str) and 0 < len(value) <= 1024, "Path must be a nonempty bounded string.", "invalid_argument")
    require(not any(ord(c) < 32 for c in value), "Control characters are not allowed in paths.", "path_not_allowed")
    path = Path(value)
    require(path.is_absolute() and not value.startswith(("\\\\", "//")),
            "An absolute local path is required; network/device paths are unsupported.", "path_not_allowed")
    require(".." not in path.parts, "Parent traversal is not allowed.", "path_not_allowed")
    for part in path.parts[1:]:
        require(":" not in part and not part.endswith((" ", ".")),
                "Alternate streams and ambiguous Windows names are unsupported.", "path_not_allowed")
    no_links(path)
    return path.resolve()


def relative_design_path(value: str) -> str:
    path = PurePosixPath(value)
    require(bool(value) and not path.is_absolute() and ".." not in path.parts
            and "\\" not in value and ":" not in value and "\x00" not in value
            and str(path) == value,
            "Invalid project-internal file reference.", "path_not_allowed")
    return value


def closed_project(directory: Path) -> None:
    no_links(directory)
    require(not os.path.lexists(directory / ".lock"),
            "Close the project in LibrePCB before reading it; a lock file is present.", "project_locked")
    require(not any(os.path.lexists(directory / name) for name in (".autosave", ".backup")),
            "Project recovery data is present. Recover and close it in LibrePCB first.", "recovery_required")


@dataclass(frozen=True)
class Capture:
    files: dict[str, bytes]
    revision: str


def capture(directory: Path) -> Capture:
    """Capture saved files only, never autosaves, links, VCS data or GUI state."""
    closed_project(directory)
    files = {}
    total = 0
    entries = 0
    pending = [directory]
    while pending:
        parent = pending.pop()
        no_links(parent)
        for child in sorted(parent.iterdir()):
            entries += 1
            require(entries <= MAX_ENTRIES, "Project contains too many entries.", "resource_limit")
            if child.name in VCS_DIRS:
                continue
            no_links(child)
            info = child.stat()
            if stat.S_ISDIR(info.st_mode):
                pending.append(child)
                continue
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1,
                    "Only regular, non-hardlinked project files are supported.", "path_not_allowed")
            require(info.st_size <= MAX_FILE_BYTES, "Project file exceeds size limit.", "resource_limit")
            with child.open("rb") as stream:
                data = stream.read(MAX_FILE_BYTES + 1)
            require(len(data) <= MAX_FILE_BYTES, "Project file exceeds size limit.", "resource_limit")
            total += len(data)
            require(total <= MAX_PROJECT_BYTES, "Project exceeds total size limit.", "resource_limit")
            files[child.relative_to(directory).as_posix()] = data
    closed_project(directory)
    fingerprint = hashlib.sha256()
    for name, data in sorted(files.items()):
        fingerprint.update(name.encode("utf-8") + b"\x00" + hashlib.sha256(data).digest())
    return Capture(files, "sha256:" + fingerprint.hexdigest())


def copy_capture(captured: Capture, destination: Path) -> None:
    no_links(destination)
    require(os.name != "nt" or all(len(str(destination / name)) < 260 for name in captured.files),
            "Snapshot paths exceed this Windows setup's limit. Configure a shorter data-root directory.", "path_too_long")
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in captured.files.items():
        path = destination / relative_design_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        no_links(path)
        with path.open("xb") as stream:
            stream.write(data)
