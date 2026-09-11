"""Server-owned output jobs and verified local artifacts; no project job execution."""

from dataclasses import dataclass
import hashlib
from importlib.resources import files
from pathlib import Path
import re
import stat
import struct
from uuid import uuid4

from librepcb_mcp.adapters.files import no_links, relative_design_path
from librepcb_mcp.errors import require

MAX_IMAGE_BYTES = 1_000_000
MAX_EXPORT_BYTES = 32_000_000
JOB_NAMES = {"schematic_png": "Schematic PNG", "schematic_pdf": "Schematic PDF",
             "gerber_excellon": "Gerber Excellon"}


def job_text(kind: str, board_id: str | None = None) -> str:
    require(kind in JOB_NAMES, "Unsupported server-owned output job.", "invalid_argument")
    if kind == "gerber_excellon":
        require(bool(board_id) and bool(re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", board_id)),
                "A validated board UUID is required.", "invalid_argument")
        return files("librepcb_mcp").joinpath("resources", "gerber.lp").read_text(encoding="utf-8").replace("__BOARD_UUID__", board_id)
    text = files("librepcb_mcp").joinpath("resources", "preview.lp").read_text(encoding="utf-8")
    if kind == "schematic_pdf":
        text = text.replace('"Schematic PNG"', '"Schematic PDF"').replace('"schematic.png"', '"schematic.pdf"')
    return text


@dataclass(frozen=True)
class Artifact:
    identifier: str
    path: Path
    sha256: str
    size: int
    mime_type: str
    width: int | None = None
    height: int | None = None

    def public(self) -> dict:
        result = {"artifact_id": self.identifier, "path": str(self.path), "filename": self.path.name,
                  "mime_type": self.mime_type, "bytes": self.size, "sha256": self.sha256}
        if self.width is not None:
            result.update({"width": self.width, "height": self.height})
        return result


def collect_artifacts(directory: Path, kind: str, schematic_count: int) -> list[Artifact]:
    no_links(directory)
    candidates = []
    entries = list(directory.iterdir())
    # LibrePCB records generated files in this control file. Verify its paths
    # and exact job UUID, then expose only the actual deliverables as artifacts.
    control = directory / ".librepcb-output"
    no_links(control)
    require(control.is_file() and control.stat().st_nlink == 1 and control.stat().st_size <= 16_384,
            "Missing or invalid LibrePCB output manifest.", "invalid_export")
    job_id = "dee1ac11-916a-4da8-8fa7-171e11c37b71" if kind == "gerber_excellon" else "0fd9e43e-7e38-4c9a-8d36-5198c6c23982"
    declared = set()
    for line in control.read_text(encoding="utf-8").splitlines():
        parts = line.split(" | ")
        require(len(parts) == 2 and parts[1] == job_id, "Unexpected output manifest entry.", "invalid_export")
        name = relative_design_path(parts[0])
        require(name not in declared, "Duplicate output manifest path.", "invalid_export")
        declared.add(name)
    entries = [entry for entry in entries if entry.name != ".librepcb-output"]
    if kind == "gerber_excellon":
        require([entry.name for entry in entries] == ["gerber"], "Unexpected export directory layout.", "invalid_export")
        no_links(directory / "gerber")
        entries = list((directory / "gerber").iterdir())
    require(0 < len(entries) <= 64, "Missing or excessive export artifacts.", "invalid_export")
    total = 0
    for path in sorted(entries):
        no_links(path)
        info = path.stat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "Export is not an ordinary file.", "invalid_export")
        total += info.st_size
        require(0 < info.st_size <= MAX_EXPORT_BYTES and total <= MAX_EXPORT_BYTES,
                "Export exceeds the supported artifact size.", "resource_limit")
        data = path.read_bytes()
        require(len(data) == info.st_size, "Export changed while reading.", "invalid_export")
        width = height = None
        if kind == "schematic_png":
            require(bool(re.fullmatch(r"schematic[0-9]*\.png", path.name))
                    and len(data) >= 33 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR",
                    "Invalid PNG export.", "invalid_export")
            width, height = struct.unpack(">II", data[16:24])
            require(0 < width <= 2500 and 0 < height <= 2500 and len(data) <= MAX_IMAGE_BYTES,
                    "Preview exceeds the supported image size.", "resource_limit")
            mime = "image/png"
        elif kind == "schematic_pdf":
            require(path.name == "schematic.pdf" and data.startswith(b"%PDF-") and b"%%EOF" in data[-1024:],
                    "Invalid PDF export.", "invalid_export")
            mime = "application/pdf"
        else:
            require(bool(re.fullmatch(r"board_(?:OUTLINES|COPPER-(?:TOP|BOTTOM|IN[0-9]+)|SOLDERMASK-(?:TOP|BOTTOM)|"
                                     r"SILKSCREEN-(?:TOP|BOTTOM)|SOLDERPASTE-(?:TOP|BOTTOM))\.gbr", path.name))
                    or bool(re.fullmatch(r"board_DRILLS-(?:PTH|NPTH|PLATED-[0-9]+-[0-9]+)\.drl", path.name)),
                    "Unexpected manufacturing export name.", "invalid_export")
            is_drill = path.suffix == ".drl"
            require(b"M48" in data[:1024] if is_drill else b"%FS" in data[:8192],
                    "Invalid manufacturing file header.", "invalid_export")
            mime = "application/octet-stream"
        candidates.append(Artifact(uuid4().hex, path, hashlib.sha256(data).hexdigest(), len(data), mime, width, height))
    names = {item.path.name for item in candidates}
    require(declared == {item.path.relative_to(directory).as_posix() for item in candidates},
            "Output manifest does not match generated artifacts.", "invalid_export")
    if kind == "schematic_png":
        expected = {"schematic.png"} if schematic_count == 1 else {f"schematic{i+1}.png" for i in range(schematic_count)}
        require(names == expected, "Preview page count/names differ from the saved project.", "invalid_export")
    elif kind == "schematic_pdf":
        require(names == {"schematic.pdf"}, "Unexpected PDF artifacts.", "invalid_export")
    else:
        require({"board_OUTLINES.gbr", "board_COPPER-TOP.gbr", "board_COPPER-BOTTOM.gbr"} <= names
                and any(name.endswith(".drl") for name in names), "Incomplete manufacturing export.", "invalid_export")
    return candidates


def image_bytes(artifact: Artifact) -> bytes:
    no_links(artifact.path)
    require(artifact.mime_type == "image/png" and artifact.path.stat().st_size <= MAX_IMAGE_BYTES,
            "Artifact is not a supported preview image.", "invalid_export")
    data = artifact.path.read_bytes()
    require(len(data) == artifact.size and hashlib.sha256(data).hexdigest() == artifact.sha256,
            "Preview artifact changed after export.", "stale_revision")
    return data
