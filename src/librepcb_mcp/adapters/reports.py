"""Exclusive diagnostic writes; never replace an existing report or follow links."""

import json
from pathlib import Path

from librepcb_mcp.adapters.files import no_links


def write_json(path: Path, record) -> None:
    no_links(path)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, indent=2, ensure_ascii=True)
        stream.write("\n")
