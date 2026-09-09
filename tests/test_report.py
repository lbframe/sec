"""Run with the Python from a uv venv containing the installed asvs-verify package.

Every CLI check runs both installed entry points from outside the repository.
Fixtures describe synthetic requirements, not actual security assessments.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def requirement(verdict, **fields):
    return {"id": "synthetic-1", "verdict": verdict, **fields}


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        console = Path(sys.executable).with_name("asvs")
        if not console.is_file():
            raise RuntimeError("Install asvs-verify in a uv venv before running these tests")
        cls.entry_points = ((str(console),), (sys.executable, "-m", "asvs_verify"))

    def run_cli(self, entry_point, directory, *args):
        return subprocess.run(
            [*entry_point, *args], cwd=directory, capture_output=True,
            text=True, timeout=30,
        )

    def check_report(self, rows, result, status, problems=(), metrics=()):
        checklist = {
            "standard": "OWASP ASVS", "version": "5.0.0", "target_level": "L1",
            "chapters": "ALL", "target": "Synthetic report test",
            "total_requirements": len(rows),
            "verdict_vocabulary": ["PASS", "FAIL", "N/A", "NEEDS-EVIDENCE"],
            "requirements": rows,
        }
        with tempfile.TemporaryDirectory(prefix="asvs-report-test-") as directory:
            path = Path(directory, "checklist.json")
            original = (json.dumps(checklist, indent=2) + "\n").encode()
            path.write_bytes(original)
            for entry in self.entry_points:
                with self.subTest(entry=entry):
                    completed = self.run_cli(entry, directory, "report", "--checklist", str(path))
                    self.assertEqual(path.read_bytes(), original, "report modified its input")
                    self.assertEqual(completed.returncode, status, completed.stdout + completed.stderr)
                    self.assertEqual(completed.stderr, "")
                    self.assertIn(f"RESULT: {result} @ L1\n", completed.stdout)
                    if problems:
                        self.assertIn(f"!! {len(problems)} integrity problem(s)", completed.stdout)
                        for problem in problems:
                            self.assertIn(f"   - synthetic-1: {problem}\n", completed.stdout)
                    else:
                        self.assertNotIn("integrity problem(s)", completed.stdout)
                    for metric in metrics:
                        self.assertIn(metric, completed.stdout)

    def test_pass_with_evidence(self):
        self.check_report([requirement("PASS", evidence="synthetic.py:1")], "CONFORMANT", 0)

    def test_na_with_justification_needs_no_remediation(self):
        self.check_report(
            [requirement("N/A", evidence=" \tFeature absent from synthetic scope.\n")],
            "CONFORMANT", 0,
        )

    def test_na_requires_nonblank_text_in_evidence(self):
        fields = [
            {}, {"evidence": ""}, {"evidence": " \t\n"}, {"evidence": None},
            {"evidence": 0}, {"evidence": 42}, {"evidence": False}, {"evidence": True},
            {"evidence": []}, {"evidence": ["reason"]},
            {"evidence": {}}, {"evidence": {"reason": "feature absent"}},
            {"notes": "Feature absent"}, {"remediation": "Feature absent"},
        ]
        for values in fields:
            with self.subTest(fields=values):
                self.check_report(
                    [requirement("N/A", **values)], "INCOMPLETE", 1,
                    ["N/A with no justification in evidence"],
                )

    def test_valid_fail(self):
        self.check_report(
            [requirement("FAIL", evidence="synthetic.py:1", remediation="Fix the synthetic gap")],
            "NON-CONFORMANT", 0,
        )

    def test_needs_evidence_is_valid(self):
        self.check_report([requirement("NEEDS-EVIDENCE")], "INCOMPLETE", 0)

    def test_pass_without_evidence(self):
        for fields in ({}, {"evidence": ""}, {"evidence": " \t\n"}):
            with self.subTest(fields=fields):
                self.check_report(
                    [requirement("PASS", **fields)], "INCOMPLETE", 1,
                    ["verdict PASS with no evidence"],
                )

    def test_fail_without_evidence_or_remediation(self):
        cases = [
            ({"remediation": "Fix the gap"}, ["verdict FAIL with no evidence"]),
            ({"evidence": "synthetic.py:1"}, ["FAIL with no remediation"]),
            ({}, ["verdict FAIL with no evidence", "FAIL with no remediation"]),
            ({"evidence": " \t", "remediation": "\n"},
             ["verdict FAIL with no evidence", "FAIL with no remediation"]),
        ]
        for fields, problems in cases:
            with self.subTest(fields=fields):
                self.check_report([requirement("FAIL", **fields)], "INCOMPLETE", 1, problems)

    def test_invalid_or_missing_verdict(self):
        self.check_report(
            [requirement("UNKNOWN")], "INCOMPLETE", 1, ["invalid verdict 'UNKNOWN'"],
        )
        self.check_report(
            [{"id": "synthetic-1"}], "INCOMPLETE", 1, ["invalid verdict 'None'"],
        )

    def test_mixed_fail_and_needs_evidence(self):
        self.check_report([
            requirement("FAIL", evidence="synthetic.py:1", remediation="Fix the gap"),
            {"id": "synthetic-2", "verdict": "NEEDS-EVIDENCE"},
        ], "INCOMPLETE", 0)

    def test_integrity_problem_takes_priority_in_mixed_report(self):
        rows = [requirement("N/A"), {"id": "synthetic-2", "verdict": "NEEDS-EVIDENCE"}]
        self.check_report(rows, "INCOMPLETE", 1, ["N/A with no justification in evidence"])
        rows.append({"id": "synthetic-3", "verdict": "FAIL", "evidence": "synthetic.py:1",
                     "remediation": "Fix the gap"})
        self.check_report(rows, "INCOMPLETE", 1, ["N/A with no justification in evidence"])

    def test_coverage_and_conformance_formulas(self):
        self.check_report([
            requirement("PASS", evidence="synthetic.py:1"),
            {"id": "synthetic-2", "verdict": "N/A", "evidence": "Feature absent"},
            {"id": "synthetic-3", "verdict": "FAIL", "evidence": "synthetic.py:2",
             "remediation": "Fix the gap"},
            {"id": "synthetic-4", "verdict": "NEEDS-EVIDENCE"},
        ], "INCOMPLETE", 0, metrics=[
            "Coverage (verified, not NEEDS-EVIDENCE): 3/4 = 75.0%",
            "Conformance (PASS+N/A of total):         2/4 = 50.0%",
        ])

    def test_invalid_cli_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            for entry in self.entry_points:
                for args in (("report",), ("report", "--invalid"), ("stats", "--level", "L4")):
                    with self.subTest(entry=entry, args=args):
                        completed = self.run_cli(entry, directory, *args)
                        self.assertEqual(completed.returncode, 2)
                        self.assertIn("usage: asvs", completed.stderr)

    def test_unreadable_or_invalid_input_still_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "checklist.json")
            for raw in (None, b"{", b"{}", b'{"requirements": null}'):
                if raw is not None:
                    path.write_bytes(raw)
                for entry in self.entry_points:
                    with self.subTest(entry=entry, raw=raw):
                        completed = self.run_cli(entry, directory, "report", "--checklist", str(path))
                        self.assertNotEqual(completed.returncode, 0)
                        self.assertNotIn("RESULT:", completed.stdout)
                        if raw is None:
                            self.assertFalse(path.exists())
                        else:
                            self.assertEqual(path.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
