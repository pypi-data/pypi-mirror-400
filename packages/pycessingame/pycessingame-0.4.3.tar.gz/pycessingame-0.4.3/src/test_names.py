import unittest
import sys

# IMPORTANT: this triggers the injection
import pycessingame


class TestInjectedAPI(unittest.TestCase):
    """
    Verifies that pycessingame correctly injects its API
    into the caller's (global) namespace.
    """

    # canonical camelCase names
    API_NAMES = [
        # lifecycle
        "run", "exit",

        # environment
        "size", "frameRate", "windowTitle",
        "smooth", "noSmooth",

        # loop control
        "loop", "noLoop", "redraw",

        # input
        "getPressed",
        "cursor", "noCursor",

        # color & style
        "color", "colorMode",
        "fill", "noFill",
        "stroke", "noStroke",
        "strokeWeight",
        "background", "clear",

        # shapes
        "rect", "ellipse", "circle",
        "line", "point", "triangle",
        "rectMode", "ellipseMode",

        # text
        "text", "textSize", "textAlign", "textFont",

        # math / util
        "map", "random", "randomSeed", "randomGaussian",
        "lerpColor",

        # color components
        "red", "green", "blue", "alpha",
        "hue", "saturation", "brightness",

        # time
        "millis", "second", "minute", "hour",
        "day", "month", "year", "weekday", "timestamp",
    ]

    def camel_to_snake(self, name):
        out = ""
        for c in name:
            if c.isupper():
                out += "_" + c.lower()
            else:
                out += c
        return out.lstrip("_")

    def test_injected_names_exist(self):
        ns = globals()
        missing = []

        for camel in self.API_NAMES:
            snake = self.camel_to_snake(camel)

            if camel not in ns:
                missing.append(f"missing camelCase: {camel}")

            if snake not in ns:
                missing.append(f"missing snake_case: {snake}")

        if missing:
            self.fail(
                "Injected API names missing:\n"
                + "\n".join(missing)
            )

    def test_injected_objects_are_callable_when_expected(self):
        ns = globals()
        non_callable = []

        for camel in self.API_NAMES:
            snake = self.camel_to_snake(camel)

            for name in (camel, snake):
                obj = ns.get(name)
                if obj is not None and not callable(obj):
                    non_callable.append(f"{name} is not callable")

        if non_callable:
            self.fail(
                "Injected API objects not callable:\n"
                + "\n".join(non_callable)
            )


if __name__ == "__main__":
    unittest.main()
