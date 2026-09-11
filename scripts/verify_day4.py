"""Real MCP resistance candidate, invariants, checks, images, exports and rollback."""

import asyncio
import base64
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
import shutil
import sys
from uuid import uuid4

from mcp import Client, StdioServerParameters, stdio_client
from librepcb_mcp.adapters.files import capture, no_links
from day3_fixtures import add_erc_fault
from verify_baseline import extract_fixture, manifest

ROOT = Path(__file__).resolve().parents[1]
R17 = "0f0fb70f-d2f9-4a08-83e2-47fae2ffc276"


async def verify():
    run = ROOT / "work" / ("d4-" + uuid4().hex[:6])
    run.mkdir(parents=True)
    source = run / "p" / "source"
    pin = json.loads((ROOT / "toolchain.json").read_text(encoding="utf-8"))
    fixture = ROOT / "tests/fixtures/d0-reader.lppz"
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == pin["fixture"]["sha256"]
    extract_fixture(fixture, source)
    before = manifest(source)
    fault = run / "p" / "fault"
    shutil.copytree(source, fault)
    add_erc_fault(fault)
    fault_before = manifest(fault)
    checks, calls = [], []
    completed, failure = False, None
    candidate = None
    saved_manifest = None

    def expect(name, condition, detail=None):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(name)

    def parameters(enabled=True):
        return StdioServerParameters(command=sys.executable, args=["-m", "librepcb_mcp.server", "--cli",
            str(ROOT / pin["librepcb"]["relative_executable"]), "--project-root", str(run / "p"),
            "--data-root", str(run / "d"), *(["--enable-experimental-edits"] if enabled else [])],
            cwd=ROOT, env={"PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"})

    async def call(client, name, arguments=None):
        result = await client.call_tool(name, arguments or {}, read_timeout_seconds=300)
        wire = result.model_dump(mode="json", by_alias=True)
        images = [item for item in wire["content"] if item["type"] == "image"]
        expect("bounded_" + str(len(calls)), len(json.dumps(wire).encode()) <= (1_500_000 if images else 64_000))
        payload = result.structured_content
        if payload is not None:
            expect("error_flag_" + str(len(calls)), result.is_error == (not payload["ok"]))
        for image in images:
            data = base64.b64decode(image.pop("data"), validate=True)
            name_on_disk = f"client-preview-{len(calls)}.png"
            (run / name_on_disk).write_bytes(data)
            image.update(saved_image=name_on_disk, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        calls.append({"tool": name, "arguments": arguments or {}, "is_error": result.is_error,
                      "structured_content": payload, "images": images})
        return payload

    async def items(client, tool, handle):
        result, cursor = [], None
        while True:
            page = await call(client, tool, {"project_id": handle, "limit": 100, "cursor": cursor})
            expect(tool + "_page", page["ok"])
            result.extend(page["data"]["items"])
            cursor = page["data"]["next_cursor"]
            if cursor is None:
                return result

    def manufacturing_content(data):
        # Wall-clock time also changes the generated file checksum. Only these
        # two metadata comments are normalized; all geometry/attributes remain.
        data = re.sub(rb"(?m)^(?:G04|;) #@! TF\.CreationDate,[^\r\n]+", b"CREATION_DATE", data)
        return re.sub(rb"(?m)^G04 #@! TF\.MD5,[0-9a-f]{32}\*", b"FILE_CHECKSUM", data)

    log = (run / "server-stderr.txt").open("w", encoding="utf-8")
    try:
        async with Client(stdio_client(parameters(), errlog=log), mode="legacy", read_timeout_seconds=300) as client:
            listing = await client.list_tools()
            (run / "tool-schemas.json").write_text(listing.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
            expect("nine_opt_in_tools", len(listing.tools) == 9 and any(t.name == "create_value_edit" for t in listing.tools))
            tool = next(t for t in listing.tools if t.name == "create_value_edit")
            expect("candidate_annotation", not tool.annotations.read_only_hint and not tool.annotations.destructive_hint)
            status = await call(client, "get_status")
            expect("editing_explicitly_enabled", status["ok"] and status["data"]["experimental_edits"] and status["data"]["write_tools"])
            opened = await call(client, "open_project", {"path": str(source / "d0-reader.lpp")})
            expect("source_opened", opened["ok"])
            summary = opened["data"]
            handle, revision = summary["project_id"], summary["revision"]
            snapshot = Path(summary["snapshot_project"]).parent
            baseline_snapshot = manifest(snapshot)
            ethernet = next(s["id"] for s in summary["schematics"] if s["name"] == "Ethernet")
            before_components = await items(client, "list_components", handle)
            before_nets = await items(client, "list_nets", handle)
            before_preview = await call(client, "export_preview", {"project_id": handle, "schematic_id": ethernet})
            before_manufacturing = await call(client, "run_output_job", {"project_id": handle, "job_name": "gerber_excellon"})
            arguments = {"project_id": handle, "component_id": R17, "new_value": "2.2", "expected_revision": revision}
            for changed, error in (({"expected_revision": "stale"}, "stale_revision"),
                    ({"new_value": "1.500"}, "invalid_argument"), ({"new_value": '2\") (net injected)'}, "invalid_argument"),
                    ({"component_id": "missing"}, "invalid_argument")):
                rejected = await call(client, "create_value_edit", {**arguments, **changed})
                expect("rejected_" + next(iter(changed)) + "_" + str(len(calls)), not rejected["ok"] and rejected["error"] == error)
            expect("rejected_values_create_no_candidates", not list(snapshot.parent.glob("e*")))
            marker = source / ".lock"
            marker.write_bytes(b"test-owned lock")
            try:
                locked = await call(client, "create_value_edit", arguments)
                expect("locked_edit_rejected", not locked["ok"] and locked["error"] == "project_locked")
                expect("lock_not_removed", marker.read_bytes() == b"test-owned lock")
            finally:
                marker.unlink()
            collision = snapshot.parent / "e01"
            collision.mkdir()
            (collision / "owner.txt").write_bytes(b"preserve")
            collided = await call(client, "create_value_edit", arguments)
            expect("candidate_collision_preserved", not collided["ok"] and (collision / "owner.txt").read_bytes() == b"preserve")
            edited = await call(client, "create_value_edit", arguments)
            expect("validated_candidate_created", edited["ok"], edited)
            result = edited["data"]
            candidate_summary = result["candidate"]
            candidate = Path(candidate_summary["snapshot_project"]).parent
            candidate_handle = candidate_summary["project_id"]
            expect("separate_candidate_handle_revision", candidate_handle != handle and candidate_summary["revision"] != revision
                   and candidate_summary["source_revision"] == revision and candidate_summary["is_edit_candidate"])
            expect("typed_resistance_change", result["change"]["before"] == "1.5" and result["change"]["after"] == "2.2"
                   and result["change"]["unit"] == "kiloohm" and result["change"]["value_raw"] == "{{RESISTANCE}}")
            expect("actual_save_reopen_and_exact_invariants", result["invariants"]["exact_expected_files"]
                   and result["invariants"]["changed_files"] == ["circuit/circuit.lp"] and len(result["cli_roundtrip"]) == 4)
            expect("baseline_and_candidate_checks_match", all(result[key]["approved_count"] == 18
                   and result[key]["unapproved_count"] == 0 for key in ("baseline_checks", "candidate_checks")))
            after_components = await items(client, "list_components", candidate_handle)
            expected_components = json.loads(json.dumps(before_components))
            next(c for c in expected_components if c["id"] == R17)["attributes"][0]["value"] = "2.2"
            expect("only_intended_component_attribute_changed", after_components == expected_components)
            expect("all_nets_unchanged", await items(client, "list_nets", candidate_handle) == before_nets)
            current_checks = await call(client, "run_checks", {"project_id": candidate_handle})
            expect("candidate_checks_reusable", current_checks["ok"] and current_checks["data"]["outcome"] == "passed")
            after_preview = await call(client, "export_preview", {"project_id": candidate_handle, "schematic_id": ethernet})
            expect("candidate_native_image", after_preview["ok"] and len(calls[-1]["images"]) == 1)
            hashes = lambda value: {a["filename"]: a["sha256"] for a in value["data"]["artifacts"]}
            original_images, changed_images = hashes(before_preview), hashes(after_preview)
            expect("only_ethernet_schematic_image_changes", original_images["schematic1.png"] == changed_images["schematic1.png"]
                   and original_images["schematic2.png"] != changed_images["schematic2.png"])
            pdf = await call(client, "run_output_job", {"project_id": candidate_handle, "job_name": "schematic_pdf"})
            expect("candidate_pdf_export", pdf["ok"] and len(pdf["data"]["artifacts"]) == 1)
            after_manufacturing = await call(client, "run_output_job", {"project_id": candidate_handle, "job_name": "gerber_excellon"})
            files = lambda value: {a["filename"]: manufacturing_content(Path(a["path"]).read_bytes()) for a in value["data"]["artifacts"]}
            expect("manufacturing_unchanged_except_creation_date_and_checksum", files(before_manufacturing) == files(after_manufacturing))
            chained = await call(client, "create_value_edit", {**arguments, "project_id": candidate_handle,
                                    "expected_revision": candidate_summary["revision"], "new_value": "3.3"})
            expect("candidate_chaining_rejected", not chained["ok"] and chained["error"] == "unsupported_edit")
            saved_manifest = manifest(candidate)
            candidate_marker = candidate / ".lock"
            candidate_marker.write_bytes(b"test-owned candidate lock")
            try:
                blocked = await call(client, "export_preview", {"project_id": candidate_handle})
                expect("candidate_lock_respected", not blocked["ok"] and blocked["error"] == "project_locked")
            finally:
                candidate_marker.unlink()
            source_file = source / "project/metadata.lp"
            old = source_file.read_bytes()
            source_file.write_bytes(old + b"; changed source\n")
            try:
                stale = await call(client, "create_value_edit", arguments)
                expect("changed_source_rejected", not stale["ok"] and stale["error"] == "stale_revision")
                stale_candidate = await call(client, "get_project_summary", {"project_id": candidate_handle})
                expect("candidate_tracks_original_source_revision", not stale_candidate["ok"] and stale_candidate["error"] == "stale_revision")
            finally:
                source_file.write_bytes(old)
            opened_fault = await call(client, "open_project", {"path": str(fault / "d0-reader.lpp")})
            fault_edit = await call(client, "create_value_edit", {**arguments, "project_id": opened_fault["data"]["project_id"],
                                    "expected_revision": opened_fault["data"]["revision"]})
            expect("real_unapproved_erc_blocks_edit", not fault_edit["ok"] and fault_edit["error"] == "validation_failed")
            expect("failed_edit_has_report", Path(fault_edit["details"]["report_artifact"]).is_file())
            expect("source_snapshot_fault_and_candidate_preserved", manifest(source) == before and manifest(snapshot) == baseline_snapshot
                   and manifest(fault) == fault_before and manifest(candidate) == saved_manifest)

        # Rollback is abandoning the isolated candidate, after the owning MCP
        # process exits. Check exact absolute containment and closed saved files
        # before deleting only this known test-owned candidate directory.
        no_links(candidate)
        expect("rollback_target_is_owned_candidate", candidate.resolve().is_relative_to(run.resolve() / "d")
               and candidate.name == "c" and candidate.parent.name.startswith("e") and manifest(candidate) == saved_manifest)
        capture(candidate)
        shutil.rmtree(candidate)
        expect("rollback_preserves_original", not candidate.exists() and manifest(source) == before)
        async with Client(stdio_client(parameters(False), errlog=log), mode="legacy", read_timeout_seconds=120) as client:
            listing = await client.list_tools()
            expect("default_server_keeps_eight_tools", len(listing.tools) == 8 and all(t.name != "create_value_edit" for t in listing.tools))
            reopened = await call(client, "open_project", {"path": str(source / "d0-reader.lpp")})
            restored = await items(client, "list_components", reopened["data"]["project_id"])
            expect("original_reopens_after_rollback_at_1_5_kiloohm", restored == before_components)
        completed = True
    except Exception as exc:
        def describe(error):
            return [describe(child) for child in error.exceptions] if isinstance(error, BaseExceptionGroup) else f"{type(error).__name__}: {error}"
        failure = describe(exc)
    finally:
        log.close()
        report = {"kind": "real_day4_mcp_candidate_edit_and_rollback", "package": version("librepcb-mcp-server"),
                  "mcp_sdk": version("mcp"), "passed": completed and all(c["passed"] for c in checks), "failure": failure,
                  "source_preserved": manifest(source) == before, "checks": checks, "calls": calls,
                  "rollback_completed": any(c["name"] == "original_reopens_after_rollback_at_1_5_kiloohm" and c["passed"] for c in checks),
                  "note": "Real SDK/CLI acceptance; GUI save/reopen is separately recorded. Native PNG bytes saved beside this report."}
        text = json.dumps(report, indent=2).replace(json.dumps(str(ROOT))[1:-1], "<REPO>")
        (run / "report.json").write_text(text + "\n", encoding="utf-8")
        print(json.dumps({"passed": report["passed"], "checks": len(checks), "calls": len(calls),
                          "failure": failure, "report": str(run / "report.json")}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(verify()))
