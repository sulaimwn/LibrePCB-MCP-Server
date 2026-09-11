"""Full-file invariants and rejection boundaries for the typed resistance patch."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from librepcb_mcp.adapters.edits import CIRCUIT_FILE, resistance_edit, verify_edit
from librepcb_mcp.adapters.files import Capture, capture
from librepcb_mcp.errors import ProjectError

ROOT = Path(__file__).resolve().parents[1]
R17 = "0f0fb70f-d2f9-4a08-83e2-47fae2ffc276"


class ResistanceEditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory(prefix="lp-edit-")
        with ZipFile(ROOT / "tests/fixtures/d0-reader.lppz") as archive:
            archive.extractall(cls.temp.name)
        cls.before = capture(Path(cls.temp.name))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def patch(self, value="2.2", captured=None, component=R17):
        return resistance_edit(captured or self.before, "d0-reader.lpp", component, value)

    def altered(self, old, new):
        original = self.before.files[CIRCUIT_FILE]
        assert old in original
        return Capture({**self.before.files, CIRCUIT_FILE: original.replace(old, new, 1)}, "unit-test")

    def test_exact_scalar_patch_preserves_full_project(self):
        edit = self.patch()
        old = self.before.files[CIRCUIT_FILE]
        start, end = edit.change["character_span"]
        text = old.decode("utf-8")
        self.assertEqual(edit.content, (text[:start] + '"2.2"' + text[end:]).encode())
        after = Capture({**self.before.files, CIRCUIT_FILE: edit.content}, "unit-test")
        self.assertEqual(verify_edit(self.before, after, edit)["changed_files"], [CIRCUIT_FILE])
        self.assertEqual(edit.change["unit"], "kiloohm")
        self.assertEqual(edit.change["value_raw"], "{{RESISTANCE}}")

    def test_semantic_noop_and_untrusted_text_rejected(self):
        for value in ("1.5", "1.500", "", "2k2", "2.2k", "-1", "NaN", "Infinity", "1e3", " 2.2", "2,2", "01", '2\") (net bad)', "1000001", "0.0000001", 2.2, None):
            with self.subTest(value=value), self.assertRaises(ProjectError):
                self.patch(value)

    def test_supported_zero_and_decimal_bounds(self):
        for value in ("0", "0.001", "2.200", "1000000"):
            self.assertEqual(self.patch(value).change["after"], value)

    def test_unicode_and_comments_preserved(self):
        captured = self.altered(b'(librepcb_circuit', '; resistance Ω µ unchanged\n(librepcb_circuit'.encode())
        edit = self.patch(captured=captured)
        self.assertTrue(edit.content.startswith('; resistance Ω µ unchanged\n'.encode()))

    def test_wrong_component_or_value_shape_rejected(self):
        for captured, component in ((self.before, "not-a-component"),
                (self.altered(b'(name "R17") (value "{{RESISTANCE}}")', b'(name "R17") (value "1.5k")'), R17),
                (self.altered(b'(name "R17") (value "{{RESISTANCE}}")', b'(name "U17") (value "{{RESISTANCE}}")'), R17),
                (self.altered(b'(unit kiloohm) (value "1.5")', b'(unit none) (value "1.5")'), R17)):
            with self.subTest(component=component), self.assertRaises(ProjectError):
                self.patch(captured=captured, component=component)

    def test_additional_procurement_attributes_rejected(self):
        captured = self.altered(b'(name "R17") (value "{{RESISTANCE}}")',
            b'(name "R17") (value "{{RESISTANCE}}")\n(attribute "MPN" (type string) (unit none) (value "fixed-part"))')
        with self.assertRaises(ProjectError):
            self.patch(captured=captured)

    def test_different_connectivity_or_any_other_file_rejected(self):
        edit = self.patch()
        for changed in ({**self.before.files, CIRCUIT_FILE: edit.content + b"; unrelated change\n"},
                        {**self.before.files, CIRCUIT_FILE: edit.content, "extra.lp": b"unexpected"},
                        {**self.before.files, CIRCUIT_FILE: edit.content, "circuit/erc.lp": b"hidden approvals"}):
            with self.assertRaises(ProjectError) as raised:
                verify_edit(self.before, Capture(changed, "unit-test"), edit)
            self.assertEqual(raised.exception.code, "validation_failed")


if __name__ == "__main__":
    unittest.main()
