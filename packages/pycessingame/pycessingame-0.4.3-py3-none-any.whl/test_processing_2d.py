import unittest
import math
import pycessingame as p

# ------------------------------------------------------------
# Base setup
# ------------------------------------------------------------

class Processing2DTestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # minimal surface, no window interaction
        p.size(100, 100)

    def setUp(self):
        # reset critical state between tests
        if hasattr(p._P, "_matrix"):
            p._P._matrix = [[1,0,0],[0,1,0],[0,0,1]]
            p._P._matrix_stack = []
        if hasattr(p._P, "_shape_vertices"):
            p._P._shape_vertices = []

# ------------------------------------------------------------
# API existence
# ------------------------------------------------------------

class TestApiExists(Processing2DTestBase):

    def test_new_api_methods_exist(self):
        required = [
            "arc", "quad", "square",
            "beginShape", "vertex", "endShape",
            "bezier",
            "translate", "rotate", "scale",
            "pushMatrix", "popMatrix",
            "pushStyle", "popStyle",
        ]
        for name in required:
            with self.subTest(name=name):
                self.assertTrue(
                    hasattr(p, name),
                    f"{name}() missing from API"
                )

# ------------------------------------------------------------
# Transformation stack
# ------------------------------------------------------------

class TestTransformations(Processing2DTestBase):

    def test_push_pop_matrix_restores_identity(self):
        self.assertTrue(hasattr(p._P, "_matrix"))
        m0 = [row[:] for row in p._P._matrix]

        p.pushMatrix()
        p.translate(10, 20)
        p.popMatrix()

        self.assertEqual(m0, p._P._matrix)

    def test_translate(self):
        p.pushMatrix()
        p.translate(5, 7)

        x, y = p._transform_point(p._P._matrix, 1, 1)
        p.popMatrix()

        self.assertEqual((x, y), (6, 8))

    def test_rotate_90deg(self):
        p.pushMatrix()
        p.rotate(math.pi / 2)

        x, y = p._transform_point(p._P._matrix, 1, 0)
        p.popMatrix()

        self.assertAlmostEqual(x, 0, places=5)
        self.assertAlmostEqual(y, 1, places=5)

    def test_scale(self):
        p.pushMatrix()
        p.scale(2, 3)

        x, y = p._transform_point(p._P._matrix, 1, 1)
        p.popMatrix()

        self.assertEqual((x, y), (2, 3))

# ------------------------------------------------------------
# Style stack
# ------------------------------------------------------------

class TestStyleStack(Processing2DTestBase):

    def test_push_pop_style(self):
        old_fill = p._P._fill_color
        old_stroke = p._P._stroke_color

        p.pushStyle()
        p.fill(255, 0, 0)
        p.stroke(0, 255, 0)

        self.assertNotEqual(p._P._fill_color, old_fill)
        self.assertNotEqual(p._P._stroke_color, old_stroke)

        p.popStyle()

        self.assertEqual(p._P._fill_color, old_fill)
        self.assertEqual(p._P._stroke_color, old_stroke)

# ------------------------------------------------------------
# Shapes
# ------------------------------------------------------------

class TestShapes(Processing2DTestBase):

    def test_square_runs(self):
        p.square(10, 10, 20)

    def test_quad_runs(self):
        p.quad(10, 10, 30, 10, 30, 30, 10, 30)

    def test_arc_runs(self):
        p.arc(50, 50, 40, 40, 0, math.pi)

# ------------------------------------------------------------
# beginShape / endShape
# ------------------------------------------------------------

class TestBeginShape(Processing2DTestBase):

    def test_begin_shape_clears_vertices(self):
        p.beginShape()
        p.vertex(0, 0)
        p.endShape()

        p.beginShape()
        self.assertEqual(len(p._P._shape_vertices), 0)

    def test_basic_polygon(self):
        p.beginShape()
        p.vertex(10, 10)
        p.vertex(20, 10)
        p.vertex(20, 20)
        p.endShape()

# ------------------------------------------------------------
# Bezier
# ------------------------------------------------------------

class TestBezier(Processing2DTestBase):

    def test_bezier_runs(self):
        p.bezier(0, 0, 20, 0, 20, 20, 40, 20)

# ------------------------------------------------------------
# Curve (expected failure)
# ------------------------------------------------------------

class TestCurve(Processing2DTestBase):

    def test_curve_not_implemented_yet(self):
        with self.assertRaises((AttributeError, NotImplementedError)):
            p.curve(0, 0, 10, 10, 20, 10, 30, 0)

if __name__ == "__main__":
    unittest.main()

