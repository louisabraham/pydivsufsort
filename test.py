import unittest

from pydivsufsort import WonderString


class TestFindUniqueRepeatSubstrings(unittest.TestCase):
    def test_find_unique_repeat_substrings(self):
        test_cases = [
            {
                "s": "this string is repeated three times in this sentence. string string .".encode(),
                "min_length": 4,
                "min_repeats": 2,
                "expected_result": [b" string ", b"this s"],
            },
            {
                "s": "s st str stri strin string".encode(),
                "min_length": 4,
                "min_repeats": 2,
                "expected_result": [b" str", b"stri", b"trin"],
            },
            {
                "s": "banana".encode(),
                "min_length": 2,
                "min_repeats": 2,
                "expected_result": [b"ana"],
            },
            {
                "s": "".encode(),
                "min_length": 3,
                "min_repeats": 2,
                "expected_result": [],
            },
            {
                "s": "a".encode(),
                "min_length": 1,
                "min_repeats": 1,
                "expected_result": [],
            },
            {
                "s": "aa".encode(),
                "min_length": 1,
                "min_repeats": 2,
                "expected_result": [b"a"],
            },
        ]

        for case in test_cases:
            s = case["s"]
            min_length = case["min_length"]
            min_repeats = case["min_repeats"]
            expected_result = case["expected_result"]

            try:
                s = WonderString(s)
                result = s.most_frequent_substrings(
                    length=min_length, minimum_count=min_repeats
                )
                self.assertEqual(result, expected_result)
            except AssertionError as e:
                error_msg = (
                    f"AssertionError in test case:\n"
                    f"s: {s}\n"
                    f"min_length: {min_length}\n"
                    f"min_repeats: {min_repeats}\n"
                    f"Expected: {expected_result}\n"
                    f"Result: {result}\n"
                )
                raise AssertionError(error_msg) from e


suite = unittest.TestLoader().loadTestsFromTestCase(TestFindUniqueRepeatSubstrings)
runner = unittest.TextTestRunner()
runner.run(suite)
