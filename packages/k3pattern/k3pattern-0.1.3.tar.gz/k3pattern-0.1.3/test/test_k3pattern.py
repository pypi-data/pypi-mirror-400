import os
import unittest

import k3ut
import k3pattern

dd = k3ut.dd

this_base = os.path.dirname(__file__)


class TestK3pattern(unittest.TestCase):
    def test_common_prefix_invalid_arg(self):
        cases = (
            (1, []),
            ("a", 1),
            ("a", True),
            ("a", ("a",)),
            (
                (
                    "a",
                    (),
                ),
                (
                    "a",
                    2,
                ),
            ),
        )

        for a, b in cases:
            dd("wrong type: ", repr(a), " ", repr(b))
            self.assertRaises(TypeError, k3pattern.common_prefix, a, b)

    def test_common_prefix(self):
        cases = (
            (
                "abc",
                "abc",
            ),
            (
                "",
                "",
                "",
            ),
            (
                (),
                (),
                (),
                (),
            ),
            (
                "abc",
                "ab",
                "ab",
            ),
            (
                "ab",
                "abd",
                "ab",
            ),
            (
                "abc",
                "abd",
                "ab",
            ),
            (
                "abc",
                "def",
                "",
            ),
            (
                "abc",
                "",
                "",
            ),
            (
                "",
                "def",
                "",
            ),
            (
                "abc",
                "abd",
                "ag",
                "a",
            ),
            (
                "abc",
                "abd",
                "ag",
                "yz",
                "",
            ),
            (
                (
                    1,
                    2,
                ),
                (
                    1,
                    3,
                ),
                (1,),
            ),
            (
                (
                    1,
                    2,
                ),
                (
                    2,
                    3,
                ),
                (),
            ),
            (
                (
                    1,
                    2,
                    "abc",
                ),
                (
                    1,
                    2,
                    "abd",
                ),
                (
                    1,
                    2,
                    "ab",
                ),
            ),
            (
                (
                    1,
                    2,
                    "abc",
                ),
                (
                    1,
                    2,
                    "xyz",
                ),
                (
                    1,
                    2,
                ),
            ),
            (
                (
                    1,
                    2,
                    (5, 6),
                ),
                (
                    1,
                    2,
                    (5, 7),
                ),
                (
                    1,
                    2,
                    (5,),
                ),
            ),
            (
                (
                    "abc",
                    "45",
                ),
                ("abc", "46", "xyz"),
                (
                    "abc",
                    "4",
                ),
            ),
            (
                ("abc", ("45", "xyz"), 3),
                ("abc", ("45", "xz"), 5),
                ("abc", ("45", "x-"), 5),
                (
                    "abc",
                    ("45", "x"),
                ),
            ),
            (
                ("abc", ("45", "xyz"), 3),
                ("abc", ("45", "xz"), 5),
                (
                    "abc",
                    ("x",),
                ),
                ("abc",),
            ),
            (
                [1, 2, 3],
                [1, 2, 4],
                [1, 2],
            ),
        )

        for args in cases:
            expected = args[-1]
            args = args[:-1]

            dd("input: ", args, "expected: ", expected)
            rst = k3pattern.common_prefix(*args)
            dd("rst: ", rst)

            self.assertEqual(expected, rst)

    def test_common_prefix_no_recursive(self):
        cases = (
            (
                ("abc", ("45", "xyz"), 3),
                ("abc", ("45", "xz"), 5),
                ("abc", ("45", "x-"), 5),
                ("abc",),
            ),
            (
                "abc",
                "abd",
                "ag",
                "a",
            ),
            (
                (1, 2, "abc"),
                (1, 2, "abd"),
                (1, 2),
            ),
        )

        for args in cases:
            expected = args[-1]
            args = args[:-1]

            dd("input: ", args, "expected: ", expected)
            rst = k3pattern.common_prefix(*args, recursive=False)
            dd("rst: ", rst)

            self.assertEqual(expected, rst)
