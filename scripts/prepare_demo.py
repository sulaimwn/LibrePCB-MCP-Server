"""Prepare a new CC0 sample and client config snippets; never edit host settings."""

import hashlib
import json
from pathlib import Path
import sys
import tomllib
from uuid import uuid4

from verify_baseline import extract_fixture

ROOT = Path(__file__).resolve().parents[1]


def main():
    pin = json.loads((ROOT / "toolchain.json").read_text(encoding="utf-8"))
    fixture = ROOT / "tests/fixtures/d0-reader.lppz"
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == pin["fixture"]["sha256"]
    demo = ROOT / "work" / ("demo-" + uuid4().hex[:6])
    source = demo / "p"
    extract_fixture(fixture, source)
    command = str(Path(sys.executable).resolve())
    arguments = ["-m", "librepcb_mcp.server", "--cli",
                 str(ROOT / pin["librepcb"]["relative_executable"]),
                 "--project-root", str(source), "--data-root", str(demo / "d")]
    codex = "\n".join(["[mcp_servers.librepcb]", f"command = {json.dumps(command)}",
                        f"args = {json.dumps(arguments)}", "startup_timeout_sec = 30",
                        "tool_timeout_sec = 45", ""])
    tomllib.loads(codex)
    (demo / "codex-config.toml").write_text(codex, encoding="utf-8")
    claude = {"mcpServers": {"librepcb": {"command": command, "args": arguments}}}
    (demo / "claude-desktop-config.json").write_text(json.dumps(claude, indent=2) + "\n", encoding="utf-8")
    prompt = (f"Use LibrePCB tools: check status, open {source / 'd0-reader.lpp'}, get its summary, "
              "then inspect its components and nets. Report raw template values honestly.\n")
    (demo / "sample-prompt.txt").write_text(prompt, encoding="utf-8")
    print(json.dumps({"demo_directory": str(demo), "project": str(source / "d0-reader.lpp"),
                      "note": "Configuration snippets generated only; host settings were not changed."}, indent=2))


if __name__ == "__main__":
    main()
