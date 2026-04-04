"""Tests for diff_parser module."""
import unittest
from reviewer.diff_parser import get_changed_sql_files


class TestDiffParser(unittest.TestCase):
    """Test SQL file extraction from PR diffs."""

    def test_import(self):
        """Verify the module imports correctly."""
        from reviewer.diff_parser import get_changed_sql_files, get_full_file_content
        self.assertIsNotNone(get_changed_sql_files)
        self.assertIsNotNone(get_full_file_content)


class TestSQLAnalyzer(unittest.TestCase):
    """Test SQL analyzer module."""

    def test_import(self):
        from reviewer.sql_analyzer import analyze_sql, filter_by_severity
        self.assertIsNotNone(analyze_sql)
        self.assertIsNotNone(filter_by_severity)

    def test_filter_by_severity(self):
        from reviewer.sql_analyzer import filter_by_severity

        findings = [
            {"severity": "info", "message": "info msg"},
            {"severity": "warning", "message": "warning msg"},
            {"severity": "error", "message": "error msg"},
        ]

        # Filter to warnings and above
        result = filter_by_severity(findings, "warning")
        self.assertEqual(len(result), 2)

        # Filter to errors only
        result = filter_by_severity(findings, "error")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["severity"], "error")

        # Filter to all
        result = filter_by_severity(findings, "info")
        self.assertEqual(len(result), 3)


class TestGitHubClient(unittest.TestCase):
    """Test GitHub client module."""

    def test_import(self):
        from reviewer.github_client import post_review, post_comment
        self.assertIsNotNone(post_review)
        self.assertIsNotNone(post_comment)


if __name__ == "__main__":
    unittest.main()
