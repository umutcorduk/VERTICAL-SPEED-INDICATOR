import unittest

from vsi import build_status_message, clamp_value, parse_fpm_input


class InputHelperTests(unittest.TestCase):
    def test_parse_accepts_numeric_text(self):
        self.assertEqual(parse_fpm_input("1500"), 1500.0)

    def test_parse_strips_whitespace(self):
        self.assertEqual(parse_fpm_input("  -500  "), -500.0)

    def test_parse_rejects_invalid_text(self):
        with self.assertRaises(ValueError):
            parse_fpm_input("abc")

    def test_clamp_limits_large_values(self):
        self.assertEqual(clamp_value(7100), 6000)
        self.assertEqual(clamp_value(-7100), -6000)

    def test_status_message_formats_clamped_value(self):
        self.assertEqual(
            build_status_message(6500),
            "Hedef dikey hız 6000 FPM olarak ayarlandı.",
        )


if __name__ == "__main__":
    unittest.main()
