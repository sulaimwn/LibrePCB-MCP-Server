"""Actual MCP -> LibrePCB check/export/image acceptance with real design faults."""

import asyncio
import base64
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import shutil
import sys
from uuid import uuid4

from mcp import Client, StdioServerParameters, stdio_client

from day3_fixtures import add_drc_fault, add_erc_fault
from verify_baseline import extract_fixture, manifest

ROOT = Path(__file__).resolve().parents[1]


async def verify():
    run = ROOT / "work" / ("d3-" + uuid4().hex[:6])
    run.mkdir(parents=True)
    source = run / "p" / "board space"
    pin = json.loads((ROOT / "toolchain.json").read_text(encoding="utf-8"))
    fixture = ROOT / "tests/fixtures/d0-reader.lppz"
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == pin["fixture"]["sha256"]
    extract_fixture(fixture, source)
    before = manifest(source)
    faults = {}
    negative_sources = {}
    for name, mutate in (("erc", add_erc_fault), ("drc", add_drc_fault)):
        directory = run / "p" / name
        shutil.copytree(source, directory)
        faults[name] = mutate(directory)
        negative_sources[name] = manifest(directory)
    poison = run / "p" / "poison"
    shutil.copytree(source, poison)
    jobs = poison / "project/jobs.lp"
    text = jobs.read_text(encoding="utf-8")
    text = text.replace('{{PROJECT}}_{{VERSION}}_Schematic.pdf', '../../../must-not-exist.pdf')
    jobs.write_text(text, encoding="utf-8", newline="\n")
    poison_before = manifest(poison)
    checks, calls = [], []
    completed, failure = False, None

    def expect(name, condition, detail=None):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    params = StdioServerParameters(command=sys.executable, args=["-m", "librepcb_mcp.server", "--cli",
             str(ROOT / pin["librepcb"]["relative_executable"]), "--project-root", str(run / "p"),
             "--data-root", str(run / "d")], cwd=ROOT,
             env={"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"})

    async def call(client, tool, arguments=None):
        result = await client.call_tool(tool, arguments or {}, read_timeout_seconds=120)
        wire = result.model_dump(mode="json", by_alias=True)
        payload = result.structured_content
        images = [item for item in wire["content"] if item["type"] == "image"]
        bound = 1_500_000 if images else 64_000
        expect(f"bounded_{len(calls)}", len(json.dumps(wire).encode("utf-8")) <= bound)
        if payload is not None:
            expect(f"error_flag_{len(calls)}", result.is_error == (not payload["ok"]))
        for image in images:
            data = base64.b64decode(image.pop("data"), validate=True)
            filename = f"client-preview-{len(calls)}.png"
            (run / filename).write_bytes(data)
            image.update({"saved_image": filename, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        calls.append({"tool": tool, "arguments": arguments or {}, "is_error": result.is_error,
                      "structured_content": payload, "images": images})
        return payload

    log = (run / "server-stderr.txt").open("w", encoding="utf-8")
    try:
        async with Client(stdio_client(params, errlog=log), mode="legacy", read_timeout_seconds=120) as client:
            expect("real_handshake", client.server_info.name == "LibrePCB MCP Server")
            listing = await client.list_tools()
            (run / "tool-schemas.json").write_text(listing.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
            expect("eight_registered_tools", len(listing.tools) == 8)
            expect("export_annotations", all(not t.annotations.read_only_hint and not t.annotations.destructive_hint
                   for t in listing.tools if t.name in {"export_preview", "run_output_job"}))
            status = await call(client, "get_status")
            expect("cli_ready", status["ok"] and status["data"]["ready"])
            opened = await call(client, "open_project", {"path": str(source / "d0-reader.lpp")})
            if not opened["ok"]:
                raise RuntimeError(str(opened))
            handle = opened["data"]["project_id"]
            snapshot = Path(opened["data"]["snapshot_project"]).parent
            result = await call(client, "run_checks", {"project_id": handle})
            expect("baseline_checks_passed", result["ok"] and result["data"]["outcome"] == "passed", result)
            expect("approved_findings_retained", (result["data"]["approved_count"], result["data"]["unapproved_count"]) == (18, 0))
            expect("separate_erc_drc_counts", [(r["check"], r["approved_count"]) for r in result["data"]["checks"]] == [("erc", 2), ("drc", 16)])

            # Preoccupy the next internal operation path: never overwrite it.
            collision = snapshot.parent / "r002"
            collision.mkdir()
            marker = collision / "owner-data.txt"
            marker.write_bytes(b"preserve existing output")
            collision_result = await call(client, "export_preview", {"project_id": handle})
            expect("output_collision_preserved", not collision_result["ok"] and collision_result["error"] == "io_error"
                   and marker.read_bytes() == b"preserve existing output")

            previews = []
            for page in opened["data"]["schematics"]:
                preview = await call(client, "export_preview", {"project_id": handle, "schematic_id": page["id"]})
                expect("preview_" + page["name"], preview["ok"], preview if not preview["ok"] else None)
                if not preview["ok"]:
                    raise RuntimeError(str(preview))
                images = calls[-1]["images"]
                expect("native_mcp_image_" + page["name"], len(images) == 1 and images[0]["mimeType"] == "image/png")
                selected = next(a for a in preview["data"]["artifacts"] if a["artifact_id"] == preview["data"]["image_artifact_id"])
                expect("image_matches_artifact_" + page["name"], images[0]["sha256"] == selected["sha256"]
                       and preview["data"]["selected_schematic"]["id"] == page["id"])
                previews.append(preview["data"])
            expect("repeated_exports_are_separate", previews[0]["output_directory"] != previews[1]["output_directory"])
            all_artifacts = [a for p in previews for a in p["artifacts"]]
            for job in ("schematic_pdf", "gerber_excellon"):
                exported = await call(client, "run_output_job", {"project_id": handle, "job_name": job})
                expect(job + "_exported", exported["ok"], exported if not exported["ok"] else None)
                if not exported["ok"]:
                    raise RuntimeError(str(exported))
                artifacts = exported["data"]["artifacts"]
                all_artifacts.extend(artifacts)
                expect(job + "_file_count", len(artifacts) == (1 if job == "schematic_pdf" else 11))
            expect("all_export_hashes_match", all(hashlib.sha256(Path(a["path"]).read_bytes()).hexdigest() == a["sha256"] for a in all_artifacts))
            expect("artifacts_under_session", all(Path(a["path"]).is_relative_to(snapshot.parent) for a in all_artifacts))

            for kind in ("erc", "drc"):
                opened_fault = await call(client, "open_project", {"path": str(run / "p" / kind / "d0-reader.lpp")})
                fault_result = await call(client, "run_checks", {"project_id": opened_fault["data"]["project_id"], "checks": kind})
                expected_text = "MCP_DAY3_UNCONNECTED" if kind == "erc" else "Trace width"
                expect("real_" + kind + "_fault_is_not_a_process_failure", fault_result["ok"] and fault_result["data"]["outcome"] == "violations"
                       and fault_result["data"]["unapproved_count"] == 1)
                finding = fault_result["data"]["checks"][0]["findings"][0]
                expect("real_" + kind + "_finding", expected_text in finding["message"] and finding["severity"] == ("warning" if kind == "erc" else "error"), finding)

            poison_open = await call(client, "open_project", {"path": str(poison / "d0-reader.lpp")})
            poison_export = await call(client, "run_output_job", {"project_id": poison_open["data"]["project_id"], "job_name": "schematic_pdf"})
            expect("project_output_jobs_are_not_executed", poison_export["ok"] and
                   [a["filename"] for a in poison_export["data"]["artifacts"]] == ["schematic.pdf"] and
                   not list(run.rglob("must-not-exist.pdf")) and manifest(poison) == poison_before)
            invalid = await call(client, "run_output_job", {"project_id": handle, "job_name": "STEP Model"})
            expect("arbitrary_job_rejected", calls[-1]["is_error"])
            invalid = await call(client, "run_checks", {"project_id": handle, "board_id": "unknown"})
            expect("unknown_board_rejected", not invalid["ok"] and invalid["error"] == "invalid_argument")
            invalid = await call(client, "export_preview", {"project_id": handle, "schematic_id": "unknown"})
            expect("unknown_sheet_rejected", not invalid["ok"] and invalid["error"] == "invalid_argument")

            marker = source / ".lock"
            marker.write_bytes(b"test-owned lock")
            try:
                for tool, extra in (("run_checks", {}), ("export_preview", {}), ("run_output_job", {"job_name": "schematic_pdf"})):
                    blocked = await call(client, tool, {"project_id": handle, **extra})
                    expect("lock_blocks_" + tool, not blocked["ok"] and blocked["error"] == "project_locked")
            finally:
                marker.unlink()
            expect("source_and_snapshot_preserved", manifest(source) == before and manifest(snapshot) == before)
            expect("fault_sources_preserved", all(manifest(run / "p" / kind) == original for kind, original in negative_sources.items()))
            completed = True
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        log.close()
        report = {"kind": "real_day3_mcp_checks_exports_images", "mcp_sdk": version("mcp"),
                  "package": version("librepcb-mcp-server"), "passed": completed and all(c["passed"] for c in checks)
                  and manifest(source) == before, "failure": failure, "faults": faults,
                  "checks": checks, "calls": calls, "source_preserved": manifest(source) == before,
                  "note": "PNG bytes received as native MCP images are saved separately; no model API was called."}
        text = json.dumps(report, indent=2).replace(json.dumps(str(ROOT))[1:-1], "<REPO>")
        (run / "report.json").write_text(text + "\n", encoding="utf-8")
        print(json.dumps({"passed": report["passed"], "checks": len(checks), "calls": len(calls),
                          "failure": failure, "failed_checks": [c for c in checks if not c["passed"]],
                          "report": str(run / "report.json")}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(verify()))
