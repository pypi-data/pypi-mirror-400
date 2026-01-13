import pycessingame


# Radial Gradient
# Converted from Processing to Python

dim = 0


def setup():
    global dim

    size(640, 360)
    dim = width / 2
    background(0)
    colorMode(HSB, 360, 100, 100)
    noStroke()
    ellipseMode(RADIUS)
    frameRate(1)


def draw():
    background(0)
    x = 0
    while x <= width:
        drawGradient(x, height / 2)
        x += dim


def drawGradient(x, y):
    radius = dim / 2
    h = random(0, 360)

    r = radius
    while r > 0:
        fill(h, 90, 90)
        ellipse(x, y, r, r)
        h = (h + 1) % 360
        r -= 1

run()