import unittest
import builtins
import pycessingame as p
import pygame

# -------------------------------------------------------------------------
# Farbtests
# -------------------------------------------------------------------------

class TestColorFunction(unittest.TestCase):

    def setUp(self):
        p.colorMode(RGB)

    # ---------- color() ----------
    def test_color_gray(self):
        self.assertEqual(p.color(128), (128, 128, 128, 255))

    def test_color_gray_alpha(self):
        self.assertEqual(p.color(128, 64), (128, 128, 128, 64))

    def test_color_rgb(self):
        self.assertEqual(p.color(10, 20, 30), (10, 20, 30, 255))

    def test_color_rgba(self):
        self.assertEqual(p.color(10, 20, 30, 40), (10, 20, 30, 40))

    def test_color_tuple(self):
        self.assertEqual(p.color((1, 2, 3)), (1, 2, 3, 255))

    def test_color_nested_tuple(self):
        self.assertEqual(p.color(((10, 20, 30))), (10, 20, 30, 255))

    def test_color_float_rgb(self):
        p.colorMode(RGB, 1.0)
        self.assertEqual(p.color(1.0, 0.5, 0.0), (255, 127, 0, 255))

    def test_color_float_alpha(self):
        p.colorMode(RGB, 1.0)
        self.assertEqual(p.color(0.5, 0.5), (127, 127, 127, 127))


class TestColorModeHSB(unittest.TestCase):

    def setUp(self):
        p.colorMode(HSB, 360, 100, 100, 255)

    def test_hsb_red(self):
        c = p.color(0, 100, 100)
        self.assertEqual(c[:3], (255, 0, 0))

    def test_hsb_green(self):
        c = p.color(120, 100, 100)
        self.assertEqual(c[:3], (0, 255, 0))

    def test_hsb_blue(self):
        c = p.color(240, 100, 100)
        self.assertEqual(c[:3], (0, 0, 255))

    def test_hsb_alpha(self):
        c = p.color(0, 100, 100, 128)
        self.assertEqual(p.alpha(c), 128)


class TestColorComponents(unittest.TestCase):

    def setUp(self):
        p.colorMode(RGB)

    def test_rgb_components(self):
        c = p.color(10, 20, 30, 40)
        self.assertEqual(p.red(c), 10)
        self.assertEqual(p.green(c), 20)
        self.assertEqual(p.blue(c), 30)
        self.assertEqual(p.alpha(c), 40)

    def test_rgb_components_without_alpha(self):
        c = p.color(1, 2, 3)
        self.assertEqual(p.alpha(c), 255)


class TestHSBComponents(unittest.TestCase):

    def test_hsb_components_red(self):
        c = p.color(255, 0, 0)
        self.assertAlmostEqual(p.hue(c), 0, delta=2)
        self.assertEqual(p.saturation(c), 255)
        self.assertEqual(p.brightness(c), 255)

    def test_hsb_components_green(self):
        c = p.color(0, 255, 0)
        self.assertAlmostEqual(p.hue(c), 85, delta=2)   # 120° scaled to 255
        self.assertEqual(p.saturation(c), 255)
        self.assertEqual(p.brightness(c), 255)

    def test_hsb_components_gray(self):
        c = p.color(128)
        self.assertEqual(p.saturation(c), 0)
        self.assertEqual(p.brightness(c), 128)

    def test_hsb_components_black(self):
        c = p.color(0)
        self.assertEqual(p.brightness(c), 0)
        self.assertEqual(p.saturation(c), 0)


class TestColorModeIsolation(unittest.TestCase):

    def test_color_mode_does_not_affect_components(self):
        p.colorMode(HSB, 360, 100, 100)
        c = p.color(120, 100, 100)  # green
        p.colorMode(RGB)
        self.assertEqual(p.red(c), 0)
        self.assertEqual(p.green(c), 255)
        self.assertEqual(p.blue(c), 0)


class TestLerpColorRGB(unittest.TestCase):

    def setUp(self):
        p.colorMode(RGB)

    def test_lerp_rgb_half(self):
        c1 = p.color(0, 0, 0)
        c2 = p.color(255, 255, 255)
        self.assertEqual(
            p.lerpColor(c1, c2, 0.5),
            (127, 127, 127, 255)
        )

    def test_lerp_rgb_zero(self):
        c1 = p.color(10, 20, 30)
        c2 = p.color(200, 210, 220)
        self.assertEqual(p.lerpColor(c1, c2, 0.0), c1)

    def test_lerp_rgb_one(self):
        c1 = p.color(10, 20, 30)
        c2 = p.color(200, 210, 220)
        self.assertEqual(p.lerpColor(c1, c2, 1.0), c2)

    def test_lerp_rgb_alpha(self):
        c1 = p.color(0, 0, 0, 0)
        c2 = p.color(0, 0, 0, 255)
        self.assertEqual(
            p.lerpColor(c1, c2, 0.5),
            (0, 0, 0, 127)
        )

    def test_lerp_rgb_extrapolation(self):
        c1 = p.color(0, 0, 0)
        c2 = p.color(100, 100, 100)
        self.assertEqual(
            p.lerpColor(c1, c2, 1.5),
            (150, 150, 150, 255)
        )

# -------------------------------------------------------------------------
# Regressions- und API-Tests
# -------------------------------------------------------------------------

class TestPycessingameRegressions(unittest.TestCase):

    # map() – Processing-Signatur kaputt
    def test_map_processing_signature_raises(self):
        with self.assertRaises(NameError):            
            p.map(5, 0, 10, 0, 100)

    # map(): Python-builtin wurde überschrieben
    def test_map_builtin_shadowed(self):
        result = p.map(lambda x: x * 2, [1, 2, 3])
        self.assertIsInstance(result, builtins.map)

    # background() – falsche Übergabe an color()
    def test_background_argument_forwarding(self):
        try:
            p.background(10, 20, 30)
        except Exception as e:
            self.fail(f"background() raised {type(e).__name__}: {e}")

    def test_millis_before_run_is_zero(self):
        p._P._last_time_global = None
        self.assertEqual(p.millis(), 0)

    # HSB-Farbbereich inkonsistent
    def test_color_hsb_processing_ranges(self):
        p.colorMode(HSB, 360, 100, 100, 100)
        col = p.color(120, 100, 100)
        r, g, b, a = col
        self.assertTrue(g > r and g > b)

    def test_colormode_hsb_single_max(self):
        p.colorMode(HSB, 100)
        self.assertEqual(p._P._color_max, [100, 100, 100, 100])

    def test_colormode_rgb_defaults(self):
        p.colorMode(RGB)
        self.assertEqual(p._P._color_max, [255,255,255,255])

    def test_colormode_hsb_defaults(self):
        p.colorMode(HSB)
        self.assertEqual(p._P._color_max, [360,100,100,100])

    def test_colormode_rgb_three_args_sets_alpha_default(self):
        p.colorMode(RGB, 10, 20, 30)
        self.assertEqual(p._P._color_max, [10,20,30,255])

    def test_hue_wrapping(self):
        p.colorMode(HSB, 360,100,100)
        c1 = p.color(350, 100, 100)
        c2 = p.color(10, 100, 100)
        mid = p.lerpColor(c1, c2, 0.5)
        self.assertTrue(0 <= p.hue(mid) <= 360)
        self.assertAlmostEqual(p.hue(mid), 0, delta=1)

    def test_lerpcolor_hsb_mode_ignored(self):
        p.colorMode(HSB, 360, 100, 100)
        c1 = p.color(0, 100, 100)
        c2 = p.color(120, 100, 100)
        mid = p.lerpColor(c1, c2, 0.5)
        r, g, b, _ = mid
        self.assertTrue(r > 200 and g > 200)

    def test_line_smooth_strokeweight_ignored(self):
        p.strokeWeight(10)
        p.smooth()
        self.assertEqual(p._P._stroke_weight, 10)
        self.assertTrue(p._P._smooth)

    def test_fill_hsb_mode(self):
        p.colorMode('HSB', 360, 100, 100, 1)
        p.fill(180, 50, 100, 0.5)
        r, g, b, a = p._P._fill_color
        self.assertTrue(0 <= r <= 255)
        self.assertTrue(0 <= g <= 255)
        self.assertTrue(0 <= b <= 255)
        self.assertAlmostEqual(a, int(0.5 * 255), delta=1)

    def test_stroke_hsb_mode(self):
        p.colorMode('HSB', 360, 100, 100, 1)
        p.stroke(90, 50, 50, 1)
        r, g, b, a = p._P._stroke_color
        self.assertTrue(0 <= r <= 255)
        self.assertTrue(0 <= g <= 255)
        self.assertTrue(0 <= b <= 255)
        self.assertEqual(a, 255)

    def test_fill_stroke_behavior(self):
        colorMode(RGB)
        fill(10,20,30)
        stroke(100)
        self.assertTrue(p._P._use_fill)
        self.assertTrue(p._P._use_stroke)
        self.assertEqual(p._P._fill_color[:3], (10,20,30))
        self.assertEqual(p._P._stroke_color[:3], (100,100,100))
        p.noFill()
        p.noStroke()
        self.assertFalse(p._P._use_fill)
        self.assertFalse(p._P._use_stroke)

# -------------------------------------------------------------------------
# Shape- und Modus-Tests
# -------------------------------------------------------------------------

class TestShapeModes(unittest.TestCase):

    def setUp(self):
        p._P.surface = pygame.Surface((200,200))
        p._P._use_fill = True
        p._P._use_stroke = True
        p._P._fill_color = (255,0,0,255)
        p._P._stroke_color = (0,255,0,255)
        p._P._stroke_weight = 1

    def test_rect_modes(self):
        for mode in ['CORNER','CORNERS','CENTER','RADIUS']:
            p.rectMode(mode)
            p.rect(10,20,30,40)

    def test_ellipse_modes(self):
        for mode in ['CORNER','CORNERS','CENTER','RADIUS']:
            p.ellipseMode(mode)
            p.ellipse(50,60,70,80)


if __name__ == "__main__":
    unittest.main()
