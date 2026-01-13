from math import pi
import pycessingame

def setup():
    size(800, 600)
    background(50)
    smooth()
    frameRate(1)  # langsam, um alles sehen zu können

def draw():
    background(50)

    fill(255, 100, 100)
    stroke(255)
    strokeWeight(2)

    f = createFont("arial", 55)
    textFont("arial")
    textAlign(LEFT)
    text("LEFT aligned", 50, 50)

    textAlign(CENTER)
    text("CENTER aligned", width/2, 100)

    textAlign(RIGHT)
    text("RIGHT aligned", width-50, 150)

    # Verschiedene Größen
    textFont(f,16)
    textAlign(LEFT)
    fill(100, 255, 100)
    text("Size 16", 50, 200)

    textFont(f, 24)
    fill(100, 100, 255)
    text("Size 24", 50, 230)

    textFont(f, 48)
    fill(255, 255, 0)
    text("Size 48", 50, 280)

    textFont(f, 48)
    fill(255, 255, 0)
    textSize()
    text("Multi\nLine", 250, 280)

    # Zeilenabstand
    textFont(f, 32)
    textLeading(32)
    fill(200, 200, 255)
    text("Line1\nLine2\nLine3", 50, 350)

    # Rotation + Scale
    pushMatrix()
    translate(width-200, 400)
    rotate(-pi/8)
    scale(1.5)
    fill(255, 150, 150)
    textAlign(CENTER)
    text("Rotated & Scaled", 0, 0)
    popMatrix()

    # Stop after first draw
    noLoop()

run()
