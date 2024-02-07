import unittest
from src.utils import best_fit


class TestBestFit(unittest.TestCase):
    def test_best_fit(self):
        test_cases = [
            {
                "area_shape": (900, 900),
                "section_shape": (900, 900),
                "n": 9,
                "expected_output": ((300, 300), (3, 3))
            },
            {
                "area_shape": (10, 2),
                "section_shape": (200, 100),
                "n": 10,
                "expected_output": ((2, 1), (5, 2))
            }
        ]

        for test_case in test_cases:
            output = best_fit.best_fit(test_case["area_shape"], test_case["section_shape"], test_case["n"])
            print(output)

            self.assertEqual(output, test_case["expected_output"])