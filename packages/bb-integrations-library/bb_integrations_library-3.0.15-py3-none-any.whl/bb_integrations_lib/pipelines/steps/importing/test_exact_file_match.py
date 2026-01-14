import unittest
import re


def file_exact_match(file_name: str, sub_str: str, sep='_') -> bool:
    if not file_name or not sub_str:
        return False
    if not file_name.startswith(sub_str):
        return False
    remainder = file_name[len(sub_str):]
    if not remainder:
        return True
    if remainder.startswith('.'):
        return True
    if remainder.startswith(sep):
        date_part = remainder[1:]
        date_pattern = r'^(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{8}|\d{4}_\d{2}_\d{2}|' + \
                       r'\d{2}_\d{2}_\d{4}|\d{4}\d{2}\d{2})(\.[a-zA-Z0-9]+)?$'
        return bool(re.match(date_pattern, date_part))

    return False


class TestFileExactMatch(unittest.TestCase):
    def test_examples_from_requirements(self):
        self.assertFalse(file_exact_match("Gross_contractrack.csv", "contractrack"))
        self.assertTrue(file_exact_match("contractrack.csv", "contractrack"))
        self.assertTrue(file_exact_match("contractrack_2025-04-16.csv", "contractrack"))
        self.assertFalse(file_exact_match("Gross_contractrack_2025-04-16.csv", "contractrack"))

    def test_valid_date_formats(self):
        self.assertTrue(file_exact_match("contractrack_20250416.csv", "contractrack"))
        self.assertTrue(file_exact_match("contractrack_2025-04-16.csv", "contractrack"))
        self.assertTrue(file_exact_match("contractrack_2025_04_16.csv", "contractrack"))

    def test_invalid_formats(self):
        # Invalid because there's additional text after the date
        self.assertFalse(file_exact_match("contractrack_2025-04-16_final.csv", "contractrack"))

        # Invalid because there's text instead of a date
        self.assertFalse(file_exact_match("contractrack_version2.csv", "contractrack"))

        # Invalid because substring isn't at the start
        self.assertFalse(file_exact_match("prefix_contractrack_2025-04-16.csv", "contractrack"))

    def test_different_separator(self):
        self.assertTrue(file_exact_match("contractrack-2025-04-16.csv", "contractrack", sep='-'))
        self.assertFalse(file_exact_match("Gross-contractrack-2025-04-16.csv", "contractrack", sep='-'))

    def test_edge_cases(self):
        self.assertTrue(file_exact_match("contractrack", "contractrack"))
        self.assertFalse(file_exact_match("contractrack_", "contractrack"))
        self.assertFalse(file_exact_match("contractrack_notadate.csv", "contractrack"))


if __name__ == "__main__":
    unittest.main()