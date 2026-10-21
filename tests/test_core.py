import unittest

from http_content_range_tools.core import (
    ContentRange,
    InvalidContentRange,
    parse_content_range,
)


class TestParseContentRange(unittest.TestCase):
    def test_complete_bytes_range(self):
        result = parse_content_range("bytes 0-499/1000")
        self.assertEqual(
            result,
            ContentRange(
                start=0, end=499, total=1000,
                unit="bytes", unsatisfied=False,
            ),
        )

    def test_bytes_range_unknown_total(self):
        result = parse_content_range("bytes 0-499/*")
        self.assertEqual(
            result,
            ContentRange(
                start=0, end=499, total=None,
                unit="bytes", unsatisfied=False,
            ),
        )

    def test_unsatisfied_range(self):
        result = parse_content_range("bytes */1000")
        self.assertEqual(
            result,
            ContentRange(
                start=None, end=None, total=1000,
                unit="bytes", unsatisfied=True,
            ),
        )

    def test_single_byte_range(self):
        result = parse_content_range("bytes 5-5/10")
        self.assertEqual(result.start, 5)
        self.assertEqual(result.end, 5)
        self.assertEqual(result.total, 10)
        self.assertFalse(result.unsatisfied)

    def test_trailing_whitespace(self):
        result = parse_content_range("bytes 0-499/1000  ")
        self.assertEqual(result.start, 0)
        self.assertEqual(result.end, 499)

    def test_inner_whitespace(self):
        result = parse_content_range("bytes  0-499/1000")
        self.assertEqual(result.start, 0)
        self.assertEqual(result.end, 499)

    def test_non_bytes_unit_rejected(self):
        with self.assertRaises(InvalidContentRange):
            parse_content_range("items 0-499/1000")

    def test_start_greater_than_end_rejected(self):
        with self.assertRaises(InvalidContentRange):
            parse_content_range("bytes 500-499/1000")

    def test_empty_value_rejected(self):
        with self.assertRaises(InvalidContentRange):
            parse_content_range("")

    def test_garbage_rejected(self):
        with self.assertRaises(InvalidContentRange):
            parse_content_range("not a content range")

    def test_missing_total_rejected(self):
        with self.assertRaises(InvalidContentRange):
            parse_content_range("bytes 0-499")

    def test_non_string_rejected(self):
        with self.assertRaises(InvalidContentRange):
            parse_content_range(123)


if __name__ == "__main__":
    unittest.main()
