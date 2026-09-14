"""Prepare a new CC0 sample and client config snippets; never edit host settings."""

import argparse
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import sys
import subprocess
import tomllib
from uuid import uuid4

from verify_baseline import extract_fixture

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experimental-edits", action="store_true", help="Generate a demo config with typed-resistance candidate editing enabled")
    parser.add_argument("--verify", action="store_true", help="Run the sample workflow through the generated config and leave a review packet")
    options = parser.parse_args()
    pin = json.loads((ROOT / "toolchain.json").read_text(encoding="utf-8"))
    try:
        ready = version('librepcb-mcp-server') == pin['tested_environment']['server_package'] and version('mcp') == pin['python_dependencies']['mcp_sdk']
    except PackageNotFoundError:
        ready = False
    if not ready:
        raise SystemExit('Run bootstrap with this interpreter before preparing the sample; required package versions are missing or differ.')
    fixture = ROOT / "tests/fixtures/d0-reader.lppz"
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == pin["fixture"]["sha256"]
    demo = ROOT / "work" / ("demo-" + uuid4().hex[:6])
    source = demo / "p"
    extract_fixture(fixture, source)
    command = str(Path(sys.executable).resolve())
    arguments = ["-m", "librepcb_mcp.server", "--cli",
                 str(ROOT / pin["librepcb"]["relative_executable"]),
                 "--project-root", str(source), "--data-root", str(demo / "d")]
    if options.experimental_edits:
        arguments.append("--enable-experimental-edits")
    codex = "\n".join(["[mcp_servers.librepcb]", f"command = {json.dumps(command)}",
                        f"args = {json.dumps(arguments)}", "startup_timeout_sec = 30",
                        f"tool_timeout_sec = {300 if options.experimental_edits else 120}", ""])
    tomllib.loads(codex)
    (demo / "codex-config.toml").write_text(codex, encoding="utf-8")
    claude = {"mcpServers": {"librepcb": {"command": command, "args": arguments}}}
    (demo / "claude-desktop-config.json").write_text(json.dumps(claude, indent=2) + "\n", encoding="utf-8")
    prompt = (f"Use LibrePCB tools: check status, open {source / 'd0-reader.lpp'}, get its summary, "
              "then inspect its components and nets, run ERC and DRC, and show a schematic preview. "
              "Report approved and unapproved findings separately and raw template values honestly.\n")
    if options.experimental_edits:
        prompt += ("Then create a separate candidate changing R17's RESISTANCE attribute from 1.5 to 2.2 in its existing kiloohm unit, "
                   "using its component ID and current source revision. Show the candidate Ethernet preview and its check results. "
                   "Preserve the original project.\n")
    (demo / "sample-prompt.txt").write_text(prompt, encoding="utf-8")
    print(json.dumps({"demo_directory": str(demo), "project": str(source / "d0-reader.lpp"),
                      "note": "Configuration snippets generated only; host settings were not changed."}, indent=2), flush=True)
    if options.verify:
        result = subprocess.run([command, str(ROOT / 'scripts/verify_demo.py'), '--demo', str(demo)], check=False)
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
