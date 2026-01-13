import os
import unittest
import math

# Headless pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pycessingame  # <- NUR dieses Import


class TestTextAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        size(100, 100)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        background(0)
        fill(255)
        noStroke()
        textSize(20)
        textAlign(LEFT, BASELINE)

    # -------------------------------------------------
    # Helper: robuste Pixelprüfung
    # -------------------------------------------------
    def pixels_have_color_around(self, x, y, radius=3):
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < _P.surface.get_width() and 0 <= ny < _P.surface.get_height():
                    if _P.surface.get_at((nx, ny)).r > 0:
                        return True
        return False


    # -------------------------------------------------
    # textSize / textFont
    # -------------------------------------------------

    def test_text_size_sets_font(self):
        textSize(30)
        self.assertEqual(_P._font_size, 30)

    def test_text_size_increases_text_width(self):
        textSize(10)
        w1 = textWidth("X")

        textSize(30)
        w2 = textWidth("X")

        self.assertGreater(w2, w1)

    def test_text_font_default(self):
        textFont(None)
        font = _P._get_font()
        self.assertIsNotNone(font)

    # -------------------------------------------------
    # textLeading
    # -------------------------------------------------

    def test_text_leading(self):
        textLeading(40)
        self.assertEqual(_P._text_leading, 40)

    # -------------------------------------------------
    # textAlign
    # -------------------------------------------------

    def test_text_align_horizontal(self):
        textAlign(CENTER)
        self.assertEqual(_P._text_align_x, "CENTER")

    def test_text_align_vertical(self):
        textAlign(LEFT, TOP)
        self.assertEqual(_P._text_align_y, "TOP")

    def test_text_align_invalid(self):
        with self.assertRaises(ValueError):
            textAlign("INVALID")

    # -------------------------------------------------
    # textWidth
    # -------------------------------------------------

    def test_text_width_positive(self):
        w = textWidth("Hello")
        self.assertGreater(w, 0)

    def test_text_width_empty(self):
        w = textWidth("")
        self.assertEqual(w, 0)

    # -------------------------------------------------
    # textAscent / textDescent
    # -------------------------------------------------

    def test_text_ascent_positive(self):
        a = textAscent()
        self.assertGreater(a, 0)

    def test_text_descent_non_negative(self):
        d = textDescent()
        self.assertGreaterEqual(d, 0)

    # -------------------------------------------------
    # text() basic drawing
    # -------------------------------------------------

    def test_text_draw_no_exception(self):
        try:
            text("Hello", 10, 30)
        except Exception as e:
            self.fail(f"text() raised exception: {e}")

    def test_text_draw_changes_pixels(self):
        text("X", 10, 30)
        self.assertTrue(self.pixels_have_color_around(10, 30))

    # -------------------------------------------------
    # alignment effect
    # -------------------------------------------------

    def test_text_center_alignment(self):
        textAlign(CENTER)
        text("X", 50, 50)
        self.assertTrue(self.pixels_have_color_around(50, 50))

    # -------------------------------------------------
    # transformation: translate
    # -------------------------------------------------

    def test_text_translate(self):
        pushMatrix()
        translate(30, 30)
        text("X", 0, 20)
        popMatrix()
        self.assertTrue(self.pixels_have_color_around(30, 50))


    # -------------------------------------------------
    # transformation: scale
    # -------------------------------------------------

    def test_text_scale(self):
        pushMatrix()
        translate(20, 40)
        scale(2)
        text("X", 0, 0)
        popMatrix()
        count = 0
        for x in range(20, 60):
            for y in range(40, 80):
                if self.pixels_have_color_around(x, y, radius=1):
                    count += 1
        self.assertGreater(count, 5)


if __name__ == "__main__":
    unittest.main()
