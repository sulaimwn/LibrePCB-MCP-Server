"""Real STDIO MCP client -> server -> pinned LibrePCB validation, on fresh copies."""

import asyncio
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import shutil
import sys
from uuid import uuid4

from mcp import Client, StdioServerParameters, stdio_client

from verify_baseline import extract_fixture, manifest

ROOT = Path(__file__).resolve().parents[1]


async def verify() -> int:
    # Keep below Windows MAX_PATH even with UUID-named embedded 3D models.
    run_dir = ROOT / "work" / ("d2-" + uuid4().hex[:6])
    run_dir.mkdir(parents=True)
    allowed = run_dir / "p"
    source = allowed / "board space"
    fixture = ROOT / "tests/fixtures/d0-reader.lppz"
    pin = json.loads((ROOT / "toolchain.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == pin["fixture"]["sha256"]
    extract_fixture(fixture, source)
    outside = run_dir / "p-sibling" / "x"
    shutil.copytree(source, outside)
    before = manifest(source)
    checks, calls, negotiations = [], [], []
    completed_all = False

    def expect(name, condition, detail=None):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    def parameters(cli=None):
        return StdioServerParameters(
            command=sys.executable,
            args=["-m", "librepcb_mcp.server", "--cli", str(cli or ROOT / pin["librepcb"]["relative_executable"]),
                  "--project-root", str(allowed), "--data-root", str(run_dir / "d")],
            cwd=ROOT, env={"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"},
        )

    async def call(client, name, arguments=None):
        result = await client.call_tool(name, arguments or {}, read_timeout_seconds=40)
        payload = result.structured_content
        wire = result.model_dump(mode="json", by_alias=True)
        size = len(json.dumps(wire).encode("utf-8"))
        expect("bounded_response_" + str(len(calls)), size <= 64_000, {"tool": name, "bytes": size})
        calls.append({"tool": name, "arguments": arguments or {}, "is_error": result.is_error,
                      "structured_content": payload})
        if isinstance(payload, dict):
            expect("error_flag_" + str(len(calls)), result.is_error == (not payload["ok"]))
        return payload

    log = (run_dir / "server-stderr.txt").open("w", encoding="utf-8")
    try:
        # Explicit legacy mode proves a real initialize/initialized handshake.
        async with Client(stdio_client(parameters(), errlog=log), mode="legacy", read_timeout_seconds=40) as client:
            negotiations.append({"mode": "legacy", "protocol": client.protocol_version,
                                 "server_info": client.server_info.model_dump(mode="json", by_alias=True)})
            expect("initialize_handshake", client.server_info.name == "LibrePCB MCP Server")
            listed = await client.list_tools()
            tools = [tool.name for tool in listed.tools]
            expect("exactly_eight_tools", set(tools) == {"get_status", "open_project", "get_project_summary", "list_components", "list_nets", "run_checks", "export_preview", "run_output_job"}, tools)
            expect("read_only_annotations", all(tool.annotations.read_only_hint for tool in listed.tools if tool.name not in {"export_preview", "run_output_job"}))
            (run_dir / "tool-schemas.json").write_text(listed.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
            status = await call(client, "get_status")
            expect("real_cli_ready", status["ok"] and status["data"]["ready"] and status["data"]["librepcb"]["version"] == "2.1.1")
            opened = await call(client, "open_project", {"path": str(source / "d0-reader.lpp")})
            expect("open_project", opened["ok"], opened if not opened["ok"] else None)
            if not opened["ok"]:
                raise RuntimeError(f"Open failed: {opened}")
            handle = opened["data"]["project_id"]
            summary = await call(client, "get_project_summary", {"project_id": handle})
            expect("summary_counts", (summary["data"]["component_count"], summary["data"]["net_count"]) == (97, 48))
            expect("snapshot_labeled", summary["data"]["state"] == "saved_snapshot")

            async def pages(tool):
                items, cursor = [], None
                for _ in range(100):
                    page = await call(client, tool, {"project_id": handle, "limit": 17, "cursor": cursor})
                    if not page["ok"]:
                        raise RuntimeError(str(page))
                    items.extend(page["data"]["items"])
                    cursor = page["data"]["next_cursor"]
                    if cursor is None:
                        return items
                raise RuntimeError("Pagination failed to terminate")

            components = await pages("list_components")
            nets = await pages("list_nets")
            expect("complete_component_pagination", len(components) == len({x["id"] for x in components}) == 97)
            expect("complete_net_pagination", len(nets) == len({x["id"] for x in nets}) == 48)
            resistor = next(c for c in components if c["reference"] == "R17")
            expect("resistor_template_and_attribute", resistor["value_is_template"] and resistor["value_raw"] == "{{RESISTANCE}}"
                   and resistor["attributes"] == [{"key": "RESISTANCE", "type": "resistance", "unit": "kiloohm", "value": "1.5"}], resistor)
            ground = next(n for n in nets if n["name"] == "GND")
            expect("ground_connectivity_counts", (ground["signal_count"], ground["component_count"]) == (58, 50), ground)

            negative_calls = [
                ("outside_root", "open_project", {"path": str(outside / "d0-reader.lpp")}, "path_not_allowed"),
                ("unknown_handle", "get_project_summary", {"project_id": "bad"}, "invalid_argument"),
                ("page_limit", "list_components", {"project_id": handle, "limit": 101}, "invalid_argument"),
                ("cross_list_cursor", "list_nets", {"project_id": handle, "cursor": f"{handle}:components:17"}, "invalid_argument"),
            ]
            for label, tool, args, code in negative_calls:
                reply = await call(client, tool, args)
                expect(label, not reply["ok"] and reply["error"] == code)

            for marker, code in ((".lock", "project_locked"), (".autosave", "recovery_required"), (".backup", "recovery_required")):
                path = source / marker
                path.write_bytes(b"test-owned sentinel")
                try:
                    result = await call(client, "open_project", {"path": str(source / "d0-reader.lpp")})
                    expect(marker + "_rejected", not result["ok"] and result["error"] == code and path.read_bytes() == b"test-owned sentinel")
                finally:
                    path.unlink()

            circuit = source / "circuit/circuit.lp"
            original = circuit.read_bytes()
            try:
                circuit.write_bytes(original + b"; new saved revision\n")
                result = await call(client, "list_components", {"project_id": handle})
                expect("stale_source_rejected", not result["ok"] and result["error"] == "stale_revision")
            finally:
                circuit.write_bytes(original)

            for name, relative, value, code in (
                ("future", ".librepcb-project", b"3\n", "unsupported_version"),
                ("malformed", "circuit/circuit.lp", b"(librepcb_circuit", "invalid_project"),
            ):
                negative = allowed / name
                shutil.copytree(source, negative)
                (negative / relative).write_bytes(value)
                result = await call(client, "open_project", {"path": str(negative / "d0-reader.lpp")})
                expect(name + "_rejected", not result["ok"] and result["error"] == code)

            snapshot_file = Path(opened["data"]["snapshot_project"])
            snapshot_circuit = snapshot_file.parent / "circuit/circuit.lp"
            snapshot_original = snapshot_circuit.read_bytes()
            try:
                snapshot_circuit.write_bytes(snapshot_original + b"; changed isolated copy\n")
                result = await call(client, "get_project_summary", {"project_id": handle})
                expect("stale_snapshot_rejected", not result["ok"] and result["error"] == "stale_revision")
            finally:
                snapshot_circuit.write_bytes(snapshot_original)

            # Outside our read projection: actual LibrePCB must reject missing
            # board-device data and expose raw CLI diagnostics, not a mock result.
            missing_device = allowed / "no-device"
            shutil.copytree(source, missing_device)
            next((missing_device / "library/dev").glob("*/device.lp")).unlink()
            result = await call(client, "open_project", {"path": str(missing_device / "d0-reader.lpp")})
            expect("real_cli_rejects_missing_device", not result["ok"] and result["error"] == "invalid_project"
                   and result.get("details", {}).get("exit_code") == 1
                   and Path(result["details"]["stderr_artifact"]).is_file())
            expect("source_files_unchanged", manifest(source) == before, {"file_count": len(before)})
            expect("snapshot_files_identical", manifest(snapshot_file.parent) == before)

        # Also prove modern discovery works, independently of the legacy handshake.
        async with Client(stdio_client(parameters(), errlog=log), read_timeout_seconds=40) as modern:
            negotiations.append({"mode": "auto", "protocol": modern.protocol_version})
            status = await call(modern, "get_status")
            expect("modern_client_ready", status["ok"] and status["data"]["ready"])
            stale_handle = await call(modern, "get_project_summary", {"project_id": handle})
            expect("handles_are_session_scoped", not stale_handle["ok"] and stale_handle["error"] == "invalid_argument")

        async with Client(stdio_client(parameters(run_dir / "missing-cli.exe"), errlog=log), mode="legacy", read_timeout_seconds=40) as missing:
            status = await call(missing, "get_status")
            expect("missing_cli_structured", status["ok"] and not status["data"]["ready"]
                   and status["data"]["problems"][0]["code"] == "cli_missing")
        completed_all = True
    finally:
        log.close()
        report = {"kind": "real_stdio_mcp_integration", "mcp_sdk": version("mcp"),
                  "server_package": version("librepcb-mcp-server"), "negotiations": negotiations,
                  "passed": completed_all and bool(checks) and all(c["passed"] for c in checks) and manifest(source) == before, "checks": checks,
                  "calls": calls, "source_preserved": manifest(source) == before,
                  "note": "SDK clients are real MCP subprocess clients; this is not a Codex or Claude UI tool-call test."}
        encoded = json.dumps(report, indent=2).replace(json.dumps(str(ROOT))[1:-1], "<REPO>")
        (run_dir / "report.json").write_text(encoded + "\n", encoding="utf-8")
        print(json.dumps({"passed": report["passed"], "checks": len(checks), "calls": len(calls),
                          "failures": [c for c in checks if not c["passed"]], "report": str(run_dir / "report.json")}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(verify()))
