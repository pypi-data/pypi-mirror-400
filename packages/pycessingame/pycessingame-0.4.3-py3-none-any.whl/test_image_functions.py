# test_image_api.py
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import unittest
import tempfile
import pygame
import pycessingame

class TestImageAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))  # nötig auch mit dummy
        size(100, 100)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def tearDown(self):
        # globalen Zustand zurücksetzen
        noTint()
        imageMode(CORNER)
        blendMode(BLEND)

    def test_load_image_valid(self):
        surf = pygame.Surface((10, 10))
        surf.fill((255, 0, 0))

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            filename = f.name

        pygame.image.save(surf, filename)

        img = loadImage(filename)

        self.assertIsNotNone(img)
        self.assertEqual(img.width, 10)
        self.assertEqual(img.height, 10)

        os.remove(filename)

    def test_load_image_invalid(self):
        img = loadImage("does_not_exist.png")
        self.assertIsNone(img)

    def test_image_mode(self):
        imageMode(CENTER)
        self.assertEqual(pycessingame._P._image_mode, "CENTER")

        imageMode(CORNER)
        self.assertEqual(pycessingame._P._image_mode, "CORNER")

        with self.assertRaises(ValueError):
            imageMode("INVALID")

    def test_tint_and_notint(self):
        tint(255, 0, 0, 128)
        self.assertEqual(pycessingame._P._tint, (255, 0, 0, 128))

        noTint()
        self.assertIsNone(pycessingame._P._tint)

    def test_image_draw(self):
        surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        surf.fill((0, 255, 0, 255))
        img = PImage(surf)

        # darf keine Exception werfen
        image(img, 10, 10)
        image(img, 10, 10, 20, 20)

    def test_image_tint_applied(self):
        surf = pygame.Surface((1, 1), pygame.SRCALPHA)
        surf.fill((100, 100, 100, 255))
        img = PImage(surf)

        tint(255, 0, 0)
        image(img, 0, 0)

        px = pycessingame._P.surface.get_at((0, 0))

        self.assertGreater(px.r, px.g)
        self.assertGreater(px.r, px.b)

    def test_blend_mode(self):
        blendMode(ADD)
        self.assertEqual(pycessingame._P._blend_mode, "ADD")

if __name__ == "__main__":
    unittest.main()

