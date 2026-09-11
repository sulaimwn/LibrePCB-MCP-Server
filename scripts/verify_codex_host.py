"""Optional deterministic Codex app-server MCP test; no model turn or config edits.

Verified against codex-cli 0.153.4's generated JSON schemas. This starts a separate
host process and an ephemeral thread, then calls MCP directly through that host.
It does not test UI rendering or launch a coding agent.
"""

import argparse
import base64
import hashlib
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
import tomllib
from uuid import uuid4

from verify_baseline import extract_fixture, manifest

ROOT = Path(__file__).resolve().parents[1]


class Host:
    def __init__(self, command, stderr):
        self.process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=stderr, text=True,
                                        encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
        self.messages = queue.Queue()
        self.counter = 0
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        for line in self.process.stdout:
            try:
                self.messages.put(json.loads(line))
            except json.JSONDecodeError:
                self.messages.put({"invalid_stdout": line[:500]})
        self.messages.put({"eof": True})

    def send(self, method, params, identifier=None):
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        if identifier is not None:
            message["id"] = identifier
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def request(self, method, params, timeout=60):
        self.counter += 1
        self.send(method, params, self.counter)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                message = self.messages.get(timeout=min(1, max(.01, deadline - time.monotonic())))
            except queue.Empty:
                continue
            if "eof" in message or "invalid_stdout" in message:
                raise RuntimeError(f"Host transport failed: {message}")
            if "method" in message and "id" in message:
                raise RuntimeError(f"Unexpected host request: {message['method']}; no approval was supplied")
            if message.get("id") == self.counter:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message["result"]
        raise TimeoutError(f"Host request timed out: {method}")

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            # Only this harness-owned process tree; never other desktop sessions.
            subprocess.run(["taskkill.exe", "/PID", str(self.process.pid), "/T", "/F"],
                           capture_output=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
            self.process.wait(timeout=10)
        self.process.stdout.close()
        self.reader.join(timeout=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", required=True, type=Path)
    parser.add_argument("--experimental-edits", action="store_true")
    args = parser.parse_args()
    run_dir = ROOT / "work" / ("cx-" + uuid4().hex[:6])
    run_dir.mkdir(parents=True)
    source = run_dir / "p"
    fixture = ROOT / "tests/fixtures/d0-reader.lppz"
    pin = json.loads((ROOT / "toolchain.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == pin["fixture"]["sha256"]
    extract_fixture(fixture, source)
    before = manifest(source)
    cli_version = subprocess.run([str(args.codex), "--version"], capture_output=True,
                                 text=True, check=True, timeout=15).stdout.strip()
    # Disable other configured servers/plugins only in this process. Read table
    # names locally; never copy config values, credentials, or auth files to logs.
    config_path = Path.home() / ".codex/config.toml"
    configuration = tomllib.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    overrides = ["features.apps=false", "features.plugins=false", "features.remote_plugin=false",
                 "features.shell_snapshot=false"]
    for name in configuration.get("mcp_servers", {}):
        if "." in name:
            raise ValueError("This optional host harness does not support dotted MCP config keys")
        overrides.append(f"mcp_servers.{name}.enabled=false")
    server = {"command": sys.executable, "args": ["-m", "librepcb_mcp.server", "--cli",
              str(ROOT / pin["librepcb"]["relative_executable"]), "--project-root", str(source),
              "--data-root", str(run_dir / "d")], "cwd": str(ROOT),
              "startup_timeout_sec": 30, "tool_timeout_sec": 300 if args.experimental_edits else 120}
    if args.experimental_edits:
        server["args"].append("--enable-experimental-edits")
    for key, value in server.items():
        overrides.append(f"mcp_servers.librepcb_day2.{key}={json.dumps(value)}")
    command = [str(args.codex), "app-server", "--listen", "stdio://"]
    for override in overrides:
        command.extend(["-c", override])
    checks, calls = [], []
    completed = False
    failure = None
    log = (run_dir / "host-stderr.txt").open("w", encoding="utf-8")
    host = Host(command, log)
    try:
        host.request("initialize", {"clientInfo": {"name": "librepcb_day2_test", "version": "0.1"},
                                    "capabilities": {"experimentalApi": True}})
        host.send("initialized", {})
        thread = host.request("thread/start", {"cwd": str(ROOT), "ephemeral": True})
        thread_id = thread["thread"]["id"]
        status = host.request("mcpServerStatus/list", {"threadId": thread_id, "limit": 100}, timeout=90)
        found = next(item for item in status["data"] if item["name"] == "librepcb_day2")
        checks.append({"name": "host_discovers_registered_tools", "passed": len(found["tools"]) == (9 if args.experimental_edits else 8),
                       "tools": list(found["tools"]), "runtime_status": found.get("runtimeStatus")})

        def call(tool, arguments=None):
            result = host.request("mcpServer/tool/call", {"threadId": thread_id,
                                  "server": "librepcb_day2", "tool": tool, "arguments": arguments or {}}, timeout=300 if args.experimental_edits else 120)
            for content in result["content"]:
                if content.get("type") == "image":
                    data = base64.b64decode(content.pop("data"), validate=True)
                    image_path = run_dir / f"host-preview-{len(calls)}.png"
                    image_path.write_bytes(data)
                    content.update({"saved_image": str(image_path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
            calls.append({"tool": tool, "result": result})
            return result["structuredContent"]

        status = call("get_status")
        checks.append({"name": "real_cli_ready", "passed": status["ok"] and status["data"]["ready"]})
        opened = call("open_project", {"path": str(source / "d0-reader.lpp")})
        handle = opened["data"]["project_id"]
        summary = call("get_project_summary", {"project_id": handle})
        checks.append({"name": "host_reads_summary", "passed": summary["ok"] and
                       (summary["data"]["component_count"], summary["data"]["net_count"]) == (97, 48)})
        for tool in ("list_components", "list_nets"):
            page = call(tool, {"project_id": handle, "limit": 3})
            checks.append({"name": tool, "passed": page["ok"] and len(page["data"]["items"]) == 3})
        rules = call("run_checks", {"project_id": handle})
        checks.append({"name": "host_runs_real_checks", "passed": rules["ok"] and rules["data"]["outcome"] == "passed"
                       and rules["data"]["approved_count"] == 18 and rules["data"]["unapproved_count"] == 0})
        preview = call("export_preview", {"project_id": handle})
        images = [c for c in calls[-1]["result"]["content"] if c.get("type") == "image"]
        checks.append({"name": "host_receives_native_png_image", "passed": preview["ok"] and len(images) == 1
                       and images[0]["mimeType"] == "image/png" and images[0]["bytes"] > 1000})
        selected = next(a for a in preview["data"]["artifacts"] if a["artifact_id"] == preview["data"]["image_artifact_id"])
        checks.append({"name": "host_image_matches_export", "passed": images[0]["sha256"] == selected["sha256"]})
        for job, count in (("schematic_pdf", 1), ("gerber_excellon", 11)):
            exported = call("run_output_job", {"project_id": handle, "job_name": job})
            checks.append({"name": "host_export_" + job, "passed": exported["ok"] and len(exported["data"]["artifacts"]) == count})
        if args.experimental_edits:
            edited = call("create_value_edit", {"project_id": handle, "component_id": "0f0fb70f-d2f9-4a08-83e2-47fae2ffc276",
                          "new_value": "2.2", "expected_revision": opened["data"]["revision"]})
            checks.append({"name": "host_creates_validated_resistance_candidate", "passed": edited["ok"]
                           and edited["data"]["outcome"] == "validated_candidate" and edited["data"]["change"]["after"] == "2.2"})
            candidate = edited["data"]["candidate"]
            ethernet = next(s["id"] for s in candidate["schematics"] if s["name"] == "Ethernet")
            candidate_preview = call("export_preview", {"project_id": candidate["project_id"], "schematic_id": ethernet})
            images = [c for c in calls[-1]["result"]["content"] if c.get("type") == "image"]
            checks.append({"name": "host_receives_edited_candidate_image", "passed": candidate_preview["ok"] and len(images) == 1})
            original_summary = call("get_project_summary", {"project_id": handle})
            checks.append({"name": "host_source_handle_remains_unchanged", "passed": original_summary["ok"]
                           and original_summary["data"]["revision"] == opened["data"]["revision"]})
        rejected = call("open_project", {"path": str(ROOT / "outside.lpp")})
        checks.append({"name": "host_receives_structured_error", "passed": not rejected["ok"] and
                       rejected["error"] == "path_not_allowed" and calls[-1]["result"]["isError"]})
        completed = True
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        host.close()
        log.close()
        checks.append({"name": "source_preserved", "passed": manifest(source) == before})
        report = {"kind": "codex_app_server_direct_mcp", "codex_version": cli_version, "experimental_edits": args.experimental_edits,
                  "passed": completed and all(c["passed"] for c in checks), "failure": failure,
                  "checks": checks, "calls": calls,
                  "note": "Actual installed Codex host, ephemeral thread, direct MCP calls. Native PNG bytes saved separately with hashes. No model turn or persistent host config edits."}
        encoded = json.dumps(report, indent=2).replace(json.dumps(str(ROOT))[1:-1], "<REPO>")
        (run_dir / "report.json").write_text(encoded + "\n", encoding="utf-8")
        print(json.dumps({"passed": report["passed"], "checks": len(checks), "failure": failure,
                          "report": str(run_dir / "report.json")}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
