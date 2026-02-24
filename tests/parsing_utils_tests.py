import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.parsing_utils import (
    build_absolute_url,
    normalize_whitespace,
    parse_area,
    parse_price,
    safe_float,
    safe_int,
)


# ---------------------------------------------------------------------------
# parse_price
# ---------------------------------------------------------------------------

class TestParsePrice(unittest.TestCase):
    def test_brazilian_format_with_cents(self):
        self.assertEqual(parse_price("R$ 450.000,00"), 450000.0)

    def test_brazilian_format_no_cents(self):
        self.assertEqual(parse_price("1.200.000"), 1200000.0)

    def test_us_format_with_cents(self):
        self.assertEqual(parse_price("450,000.00"), 450000.0)

    def test_plain_integer_string(self):
        self.assertEqual(parse_price("350000"), 350000.0)

    def test_with_currency_symbol(self):
        self.assertEqual(parse_price("R$350.000"), 350000.0)

    def test_decimal_comma(self):
        self.assertAlmostEqual(parse_price("450,50"), 450.50)

    def test_decimal_dot(self):
        self.assertAlmostEqual(parse_price("450.50"), 450.50)

    def test_none_returns_none(self):
        self.assertIsNone(parse_price(None))

    def test_empty_string_returns_none(self):
        self.assertIsNone(parse_price(""))

    def test_non_numeric_returns_none(self):
        self.assertIsNone(parse_price("consulte"))

    def test_whitespace_only_returns_none(self):
        self.assertIsNone(parse_price("   "))


# ---------------------------------------------------------------------------
# parse_area
# ---------------------------------------------------------------------------

class TestParseArea(unittest.TestCase):
    def test_with_m2_symbol(self):
        self.assertEqual(parse_area("95 m²"), 95.0)

    def test_with_m2_text(self):
        self.assertEqual(parse_area("95m2"), 95.0)

    def test_with_decimal_comma(self):
        self.assertAlmostEqual(parse_area("95,5 m²"), 95.5)

    def test_with_decimal_dot(self):
        self.assertAlmostEqual(parse_area("95.5 m²"), 95.5)

    def test_thousands_separator(self):
        self.assertEqual(parse_area("1.200 m²"), 1200.0)

    def test_plain_number(self):
        self.assertEqual(parse_area("120"), 120.0)

    def test_none_returns_none(self):
        self.assertIsNone(parse_area(None))

    def test_empty_string_returns_none(self):
        self.assertIsNone(parse_area(""))

    def test_non_numeric_returns_none(self):
        self.assertIsNone(parse_area("sob consulta"))


# ---------------------------------------------------------------------------
# safe_int
# ---------------------------------------------------------------------------

class TestSafeInt(unittest.TestCase):
    def test_plain_string(self):
        self.assertEqual(safe_int("3"), 3)

    def test_string_with_text(self):
        self.assertEqual(safe_int("3 quartos"), 3)

    def test_float_input(self):
        self.assertEqual(safe_int(2.9), 2)

    def test_int_input(self):
        self.assertEqual(safe_int(4), 4)

    def test_none_returns_none(self):
        self.assertIsNone(safe_int(None))

    def test_non_numeric_returns_none(self):
        self.assertIsNone(safe_int("abc"))

    def test_empty_string_returns_none(self):
        self.assertIsNone(safe_int(""))


# ---------------------------------------------------------------------------
# safe_float
# ---------------------------------------------------------------------------

class TestSafeFloat(unittest.TestCase):
    def test_plain_string(self):
        self.assertAlmostEqual(safe_float("3.14"), 3.14)

    def test_int_input(self):
        self.assertEqual(safe_float(3), 3.0)

    def test_float_input(self):
        self.assertAlmostEqual(safe_float(2.5), 2.5)

    def test_none_returns_none(self):
        self.assertIsNone(safe_float(None))

    def test_non_numeric_returns_none(self):
        self.assertIsNone(safe_float("abc"))

    def test_empty_string_returns_none(self):
        self.assertIsNone(safe_float(""))

    def test_string_with_spaces(self):
        self.assertAlmostEqual(safe_float("  9.99  "), 9.99)


# ---------------------------------------------------------------------------
# normalize_whitespace
# ---------------------------------------------------------------------------

class TestNormalizeWhitespace(unittest.TestCase):
    def test_leading_trailing_spaces(self):
        self.assertEqual(normalize_whitespace("  hello  "), "hello")

    def test_internal_multiple_spaces(self):
        self.assertEqual(normalize_whitespace("hello   world"), "hello world")

    def test_tabs_and_newlines(self):
        self.assertEqual(normalize_whitespace("hello\t\nworld"), "hello world")

    def test_none_returns_empty_string(self):
        self.assertEqual(normalize_whitespace(None), "")

    def test_empty_string_returns_empty_string(self):
        self.assertEqual(normalize_whitespace(""), "")

    def test_already_clean_string(self):
        self.assertEqual(normalize_whitespace("hello world"), "hello world")


# ---------------------------------------------------------------------------
# build_absolute_url
# ---------------------------------------------------------------------------

class TestBuildAbsoluteUrl(unittest.TestCase):
    def test_relative_path(self):
        result = build_absolute_url("https://agency.com/listings", "/property/123")
        self.assertEqual(result, "https://agency.com/property/123")

    def test_already_absolute_url(self):
        result = build_absolute_url("https://agency.com", "https://agency.com/property/123")
        self.assertEqual(result, "https://agency.com/property/123")

    def test_relative_path_no_leading_slash(self):
        result = build_absolute_url("https://agency.com/listings/", "property/123")
        self.assertEqual(result, "https://agency.com/listings/property/123")

    def test_preserves_query_string(self):
        result = build_absolute_url("https://agency.com", "/property/123?ref=list")
        self.assertEqual(result, "https://agency.com/property/123?ref=list")

    def test_empty_path_raises(self):
        with self.assertRaises(ValueError):
            build_absolute_url("https://agency.com", "")

    def test_invalid_base_with_relative_path_raises(self):
        with self.assertRaises(ValueError):
            build_absolute_url("not-a-url", "also-not-a-url")


if __name__ == "__main__":
    unittest.main()