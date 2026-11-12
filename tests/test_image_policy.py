"""Regression tests for the CMS image vulnerability publication gate."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

POLICY = pathlib.Path(__file__).parents[1] / 'scripts/check-image-vulnerabilities.py'


class ImagePolicyTests(unittest.TestCase):
    def evaluate(self, severity, fixed):
        report = {'Results': [{'Vulnerabilities': [{'VulnerabilityID': 'CVE-test', 'PkgName': 'fixture', 'InstalledVersion': '1', 'Severity': severity, 'FixedVersion': fixed}]}]}
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / 'report.json'
            path.write_text(json.dumps(report))
            return subprocess.run([sys.executable, str(POLICY), str(path)], text=True, capture_output=True)

    def test_fixable_high_and_critical_block(self):
        for severity in ('HIGH', 'CRITICAL'):
            with self.subTest(severity=severity):
                result = self.evaluate(severity, '2')
                self.assertEqual(result.returncode, 1)
                self.assertIn('CVE-test', result.stdout)

    def test_unfixed_high_is_visible_and_not_blanket_suppressed(self):
        result = self.evaluate('HIGH', '')
        self.assertEqual(result.returncode, 0)
        self.assertIn('::warning::', result.stdout)
        self.assertIn('CVE-test', result.stdout)

    def test_lower_severity_retained_in_summary(self):
        result = self.evaluate('MEDIUM', '2')
        self.assertEqual(result.returncode, 0)
        self.assertIn('1 total', result.stdout)
