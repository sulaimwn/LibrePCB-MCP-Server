"""Parser, file boundaries and saved-state invariants on the real fixture.

CLI integration is exercised separately by scripts/verify_mcp.py.
"""

from pathlib import Path
import os
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from librepcb_mcp.adapters.files import capture, copy_capture, local_absolute, no_links
from librepcb_mcp.adapters.project import inspect_project
from librepcb_mcp.adapters.sexpr import parse
from librepcb_mcp.errors import ProjectError

ROOT = Path(__file__).resolve().parents[1]


class ParserTests(unittest.TestCase):
    def test_comments_escapes_unicode_and_original_spans(self):
        source = '; comment\n(root (name "résistor; (x) \\"quote\\" \\n\\t\\\\") (unknown future_2))\n'
        root = parse(source)
        self.assertEqual(root.field("name"), 'résistor; (x) "quote" \n\t\\')
        self.assertEqual(root.one("unknown").atom(), "future_2")
        self.assertEqual(source[root.start:root.end], source[10:-1])

    def test_invalid_grammar_is_rejected(self):
        for value in ('', '(root', '(root "open)', '(root "\\q")', '(root) (other)',
                      '( root)', '()', '(root invalid+token)', '(root)\x00', 'just_a_token'):
            with self.subTest(value=value), self.assertRaises(ProjectError):
                parse(value)

    def test_complexity_limits(self):
        with self.assertRaises(ProjectError) as raised:
            parse('(a ' * 66 + ')' * 66)
        self.assertEqual(raised.exception.code, "resource_limit")
        with self.assertRaises(ProjectError):
            parse('(a x y z)', max_nodes=3)

    def test_duplicate_single_fields_fail(self):
        with self.assertRaises(ProjectError):
            parse('(root (name "one") (name "two"))').field("name")


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="librepcb-day2-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.design = self.root / "allowed" / "design with spaces"
        with ZipFile(ROOT / "tests/fixtures/d0-reader.lppz") as archive:
            archive.extractall(self.design)

    def test_real_fixture_counts_attributes_and_signal_relationships(self):
        result = inspect_project(capture(self.design), "d0-reader.lpp")
        self.assertEqual((len(result.components), len(result.nets)), (97, 48))
        self.assertEqual([page["name"] for page in result.schematics], ["Main", "Ethernet"])
        self.assertEqual(len(result.boards), 1)
        resistor = next(c for c in result.components if c["reference"] == "R17")
        self.assertEqual(resistor["value_raw"], "{{RESISTANCE}}")
        self.assertTrue(resistor["value_is_template"])
        self.assertIn({"key": "RESISTANCE", "type": "resistance", "unit": "kiloohm", "value": "1.5"}, resistor["attributes"])
        ground = next(n for n in result.nets if n["name"] == "GND")
        self.assertEqual((ground["signal_count"], ground["component_count"]), (58, 50))
        self.assertEqual(sum(c["connected_signal_count"] for c in result.components),
                         sum(n["signal_count"] for n in result.nets))

    def test_snapshot_bytes_and_revision_preserved(self):
        before = capture(self.design)
        copy = self.root / "copy"
        copy_capture(before, copy)
        self.assertEqual(capture(copy), before)
        self.assertEqual(capture(self.design), before)
        with (copy / "circuit/circuit.lp").open("ab") as stream:
            stream.write(b"; saved change\n")
        self.assertNotEqual(capture(copy).revision, before.revision)
        self.assertEqual(capture(self.design), before)

    def test_locks_and_recovery_are_preserved_and_rejected(self):
        for marker, code in ((".lock", "project_locked"), (".autosave", "recovery_required"), (".backup", "recovery_required")):
            with self.subTest(marker=marker):
                path = self.design / marker
                path.write_bytes(b"owned-by-other-process")
                try:
                    with self.assertRaises(ProjectError) as raised:
                        capture(self.design)
                    self.assertEqual(raised.exception.code, code)
                    self.assertEqual(path.read_bytes(), b"owned-by-other-process")
                finally:
                    path.unlink()  # Only this test's sentinel, never a user's lock.

    def test_unsupported_format_and_missing_references(self):
        marker = self.design / ".librepcb-project"
        marker.write_bytes(b"3\n")
        with self.assertRaises(ProjectError) as raised:
            inspect_project(capture(self.design), "d0-reader.lpp")
        self.assertEqual(raised.exception.code, "unsupported_version")
        marker.write_bytes(b"2\n")
        library = self.design / "library/cmp/ef80cd5e-2689-47ee-8888-31d04fc99174/component.lp"
        library.unlink()
        with self.assertRaises(ProjectError):
            inspect_project(capture(self.design), "d0-reader.lpp")

    def test_internal_path_traversal_rejected(self):
        (self.design / "schematics/schematics.lp").write_text(
            '(librepcb_schematics (schematic "../outside.lp"))', encoding="utf-8")
        with self.assertRaises(ProjectError) as raised:
            inspect_project(capture(self.design), "d0-reader.lpp")
        self.assertEqual(raised.exception.code, "path_not_allowed")

    def test_dangling_net_reference_rejected(self):
        file = self.design / "circuit/circuit.lp"
        text = file.read_text(encoding="utf-8")
        text = text.replace('(net 3a4b85da-e763-4c91-8568-31b18ac3bfb4))',
                            '(net 00000000-0000-0000-0000-000000000000))', 1)
        file.write_text(text, encoding="utf-8")
        with self.assertRaises(ProjectError) as raised:
            inspect_project(capture(self.design), "d0-reader.lpp")
        self.assertIn("missing net", str(raised.exception))

    def test_hardlink_rejected(self):
        target = self.root / "outside.txt"
        target.write_bytes(b"private outside data")
        os.link(target, self.design / "linked.txt")
        with self.assertRaises(ProjectError) as raised:
            capture(self.design)
        self.assertEqual(raised.exception.code, "path_not_allowed")

    @unittest.skipUnless(os.name == "nt", "Windows junction integration")
    def test_windows_junction_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        link = self.design / "junction"
        quoted = lambda value: "'" + str(value).replace("'", "''") + "'"
        command = f"New-Item -ItemType Junction -Path {quoted(link)} -Target {quoted(outside)} | Out-Null"
        subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                       check=True, capture_output=True, timeout=10,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            with self.assertRaises(ProjectError):
                capture(self.design)
            with self.assertRaises(ProjectError):
                no_links(link)
        finally:
            os.rmdir(link)  # Removes the test junction itself, not its target.

    def test_unsafe_external_path_forms(self):
        for path in ("relative.lpp", r"\\server\share\board.lpp", r"C:\board.lpp:secret",
                     str(self.design / ".." / "escape.lpp")):
            with self.subTest(path=path), self.assertRaises(ProjectError):
                local_absolute(path)


if __name__ == "__main__":
    unittest.main()
