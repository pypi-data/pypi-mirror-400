import math
import pycessingame 

def setup():
    size(800, 600)
    windowTitle("pycessingame – 2D Features Demo")
    frameRate(60)
    smooth()

def draw():
    background(30)

    # ---------------------------------------------------------
    # 1) Style Stack + Primitive Shapes
    # ---------------------------------------------------------
    pushStyle()
    fill(255, 180, 0)
    stroke(255)
    strokeWeight(3)

    square(40, 40, 80)          # square()
    quad(160, 40, 260, 40, 300, 120, 180, 120)  # quad()

    popStyle()

    # ---------------------------------------------------------
    # 2) arc()
    # ---------------------------------------------------------
    pushStyle()
    noFill()
    stroke(0, 200, 255)
    strokeWeight(4)

    arc(120, 220, 120, 120, 0, math.pi * 1.5)
    popStyle()

    # ---------------------------------------------------------
    # 3) beginShape / vertex / endShape
    # ---------------------------------------------------------
    pushStyle()
    fill(0, 200, 120)
    stroke(255)

    beginShape()
    vertex(260, 180)
    vertex(320, 160)
    vertex(360, 200)
    vertex(340, 260)
    vertex(280, 240)
    endShape(True)   # CLOSE

    popStyle()

    # ---------------------------------------------------------
    # 4) Bezier curve
    # ---------------------------------------------------------
    pushStyle()
    noFill()
    stroke(255, 100, 200)
    strokeWeight(3)

    bezier(
        420, 200,
        500, 120,
        580, 280,
        660, 200
    )

    popStyle()

    # ---------------------------------------------------------
    # 5) Transformations + Matrix Stack
    # ---------------------------------------------------------
    pushMatrix()
    translate(width / 2, height / 2)
    rotate(frameCount * 0.02)
    scale(1.2)

    pushStyle()
    fill(180, 80, 255)
    noStroke()

    beginShape()
    for i in range(6):
        a = i * TAU / 6
        vertex(math.cos(a) * 60, math.sin(a) * 60)
    endShape(True)

    popStyle()
    popMatrix()

    # ---------------------------------------------------------
    # 6) Nested pushMatrix / pushStyle (Stress-Test)
    # ---------------------------------------------------------
    pushMatrix()
    translate(650, 450)

    for i in range(6):
        pushMatrix()
        rotate(i * math.pi / 6)
        translate(0, -60)

        pushStyle()
        fill(255, 80 + i * 25, 80)
        noStroke()
        circle(0, 0, 20)
        popStyle()

        popMatrix()

    popMatrix()

    # ---------------------------------------------------------
    # 7) Image import
    # ---------------------------------------------------------
    image(loadImage("schatzkammer.png"), 10, 300, 80, 80)

    if getPressed(ESC):
        exit()

run()
