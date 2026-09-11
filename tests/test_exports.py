"""Artifact/path/tampering invariants; real rendering is in verify_day3.py."""

import base64
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from librepcb_mcp.adapters.exports import collect_artifacts, image_bytes, job_text
from librepcb_mcp.adapters.sexpr import parse
from librepcb_mcp.errors import ProjectError

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a6WQAAAAASUVORK5CYII=")
JOB_ID = "0fd9e43e-7e38-4c9a-8d36-5198c6c23982"


class ExportArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "schematic.png").write_bytes(PNG)
        (self.root / ".librepcb-output").write_text(f"schematic.png | {JOB_ID}\n", encoding="utf-8")

    def test_control_manifest_is_verified_but_not_a_deliverable(self):
        artifacts = collect_artifacts(self.root, "schematic_png", 1)
        self.assertEqual([a.path.name for a in artifacts], ["schematic.png"])
        self.assertEqual(image_bytes(artifacts[0]), PNG)

    def test_tampered_preview_is_rejected(self):
        artifact = collect_artifacts(self.root, "schematic_png", 1)[0]
        artifact.path.write_bytes(PNG[:-1] + b"x")
        with self.assertRaises(ProjectError) as raised:
            image_bytes(artifact)
        self.assertEqual(raised.exception.code, "stale_revision")

    def test_manifest_traversal_and_wrong_job_are_rejected(self):
        for line in (f"../outside.png | {JOB_ID}\n", "schematic.png | untrusted-job\n"):
            with self.subTest(line=line):
                (self.root / ".librepcb-output").write_text(line, encoding="utf-8")
                with self.assertRaises(ProjectError):
                    collect_artifacts(self.root, "schematic_png", 1)

    def test_unexpected_extra_artifact_is_rejected(self):
        (self.root / "extra.txt").write_text("unexpected", encoding="utf-8")
        with self.assertRaises(ProjectError):
            collect_artifacts(self.root, "schematic_png", 1)

    def test_page_count_must_match_the_project(self):
        with self.assertRaises(ProjectError):
            collect_artifacts(self.root, "schematic_png", 2)

    def test_only_known_job_templates_and_board_ids_are_allowed(self):
        for kind in ("schematic_png", "schematic_pdf", "gerber_excellon"):
            root = parse(job_text(kind, JOB_ID))
            self.assertEqual(len(root.children("job")), 1)
            self.assertNotIn("{{PROJECT}}", root.one("job").field("output"))
        for kind, board in (("arbitrary-job", None), ("gerber_excellon", 'bad) (output "C:/outside")')):
            with self.assertRaises(ProjectError):
                job_text(kind, board)
