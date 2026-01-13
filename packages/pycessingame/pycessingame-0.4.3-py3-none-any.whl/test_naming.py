# -----------------------------------------------------------------------------
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or distribute
# this software, either in source code form or as a compiled binary, for any
# purpose, commercial or non-commercial, and by any means.
#
# In jurisdictions that recognize copyright laws, the author or authors of this
# software dedicate any and all copyright interest in the software to the
# public domain. We make this dedication for the benefit of the public at large
# and to the detriment of our heirs and successors. We intend this dedication
# to be an overt act of relinquishment in perpetuity of all present and future
# rights to this software under copyright law.
#
# OPTIONAL ATTRIBUTION:
# Credit to E. Luttmann is appreciated but not required.
#
# For more information, please refer to <https://unlicense.org>
# -----------------------------------------------------------------------------
import unittest
import math
import pycessingame 

class TestConstants(unittest.TestCase):

    def test_alignment_constants(self):
        self.assertEqual(LEFT, "LEFT")
        self.assertEqual(RIGHT, "RIGHT")
        self.assertEqual(CENTER, "CENTER")
        self.assertEqual(CORNER, "CORNER")
        self.assertEqual(RADIUS, "RADIUS")
        self.assertEqual(CORNERS, "CORNERS")

    def test_math_constants(self):
        self.assertAlmostEqual(PI, math.pi)
        self.assertAlmostEqual(TWO_PI, math.pi * 2)
        self.assertAlmostEqual(HALF_PI, math.pi / 2)
        self.assertAlmostEqual(QUARTER_PI, math.pi / 4)

        self.assertAlmostEqual(DEGREES * math.pi, 180, delta=0.0001)
        self.assertAlmostEqual(RADIANS * 180, math.pi, delta=0.0001)

    def test_color_mode_constants(self):
        self.assertEqual(RGB, "RGB")
        self.assertEqual(HSB, "HSB")

    def test_cursor_constants(self):
        for c in [ARROW, CROSS, HAND, MOVE, WAIT]:
            self.assertIsInstance(c, str)

if __name__ == "__main__":
    unittest.main()
