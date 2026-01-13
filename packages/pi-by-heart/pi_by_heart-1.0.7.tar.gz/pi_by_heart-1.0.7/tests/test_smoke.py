import unittest
from contextlib import redirect_stdout
from io import StringIO

import pi


class TestSmoke(unittest.TestCase):
    def test_calculate_pi_length_and_prefix(self):
        digits = 10
        value = pi._calculate_pi(digits)
        self.assertTrue(value.startswith("3."))
        self.assertGreaterEqual(len(value), digits + 2)

    def test_check_outputs_summary_for_correct_input(self):
        user_input = "3.1415"
        buffer = StringIO()
        with redirect_stdout(buffer):
            pi.check(user_input)
        output = buffer.getvalue()

        expected_line = "You got 5 out of 5 right!"
        self.assertIn("Enter the digits you know:", output)
        self.assertIn(expected_line, output)
        self.assertIn("Score:", output)

    def test_check_outputs_corrections_for_incorrect_input(self):
        user_input = "3.1416"
        buffer = StringIO()
        with redirect_stdout(buffer):
            pi.check(user_input)
        output = buffer.getvalue()

        self.assertIn("You got 4 out of 5 right!", output)
        self.assertIn("5", output)
        self.assertIn("6", output)
        self.assertIn("Score:", output)


if __name__ == "__main__":
    unittest.main()
