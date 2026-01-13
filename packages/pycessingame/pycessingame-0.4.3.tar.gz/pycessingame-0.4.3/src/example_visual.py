import pycessingame
import math

# ============================================================
# SETUP
# ============================================================
def setup():
    size(600, 500)
    frameRate(60)
    c = color(255, 180, 0)
    fill(c)
    stroke(0)
    strokeWeight(1)

# ============================================================
# DRAW – kombiniert + ARITHMETIC TEST PANEL wiederhergestellt
# ============================================================

def draw():
    background(30, 30, 40)

    # ========================================================
    # MOUSE CIRCLE + CROSSHAIR
    # ========================================================
    noStroke()
    c = color(255, 180, 0)
    fill(c)
    circle(mouseX, mouseY, 40)

    stroke(255)
    strokeWeight(1)
    line(mouseX - 10, mouseY, mouseX + 10, mouseY)
    line(mouseX, mouseY - 10, mouseX, mouseY + 10)

    # ========================================================
    # PANEL 1 – Proxy Debug (camel/snake tests)
    # ========================================================
    fill(255)
    noStroke()
    rect(10, 10, 280, 120)
    fill(0)

    text_data = [
        f"mouseX={mouseX}, mouse_x={mouse_x}",
        f"mousePressed={mousePressed}, mouse_pressed={mouse_pressed}",
        f"keyPressed={keyPressed}, key_pressed={key_pressed}",
        f"frameCount={frameCount}, frame_count={frame_count}",
        f"mouseX+10={mouseX+10}, mouse_x+20={mouse_x+20}",
        f"mouseX>300? {mouseX>300}, mouse_x<200? {mouse_x<200}",
    ]

    y = 25
    for line_text in text_data:
        text(line_text, 20, y)
        y += 15

    # ========================================================
    # ARITHMETIC & DUNDER PANEL (wiederhergestellt)
    # ========================================================
    fill(255)
    rect(10, 150, 580, 200)
    fill(0)

    dunder_tests = [
        f"Add: mouseX + 5 = {mouseX + 5}",
        f"Sub: mouseX - 5 = {mouseX - 5}",
        f"Mul: mouseX * 2 = {mouseX * 2}",
        f"Div: mouseX / 2 = {mouseX / 2:.2f}",
        f"FloorDiv: mouseX // 3 = {mouseX // 3}",
        f"Mod: mouseX % 7 = {mouseX % 7}",
        f"Pow: mouseX ** 0.5 = {mouseX ** 0.5:.2f}",
        f"Neg: -mouseX = {-mouseX}",
        f"Abs: abs(mouseX-250) = {abs(mouseX - 250)}",
        f"Round: round(mouseX / 3) = {round(mouseX / 3)}",
        f"Compare: mouseX < 200 ? {mouseX < 200}",
        f"Compare: mouseX >= 300 ? {mouseX >= 300}",
        f"Bool: bool(mouseX) = {bool(mouseX)}",
        f"Eq: mouseX == mouse_x ? {mouseX == mouse_x}",
    ]

    y = 165
    for line_text in dunder_tests:
        text(line_text, 20, y)
        y += 12

    # ========================================================
    # VISUAL CIRCLES
    # ========================================================
    if mouseX > 300:
        fill(255,0,0)
    else:
        fill(0,255,0)
    circle(500, 350, 30)

    if mouse_x < 200:
        fill(0,0,255)
    else:
        fill(255,255,0)
    circle(550, 350, 30)

    # Snake-case arithmetic
    stroke(255)
    mouse_x_plus = mouse_x + 10
    line(0, mouse_x_plus, 600, mouse_x_plus)

# ============================================================
# MOUSE CALLBACKS
# =============r==============================================
def mousePressed():
    print(f"Mouse pressed at ({mouseX},{mouseY}) button={mouseButton}")

def mouseReleased():
    print(f"Mouse released at ({mouseX},{mouseY})")

def mouseDragged():
    print(f"Mouse dragged at ({mouseX},{mouseY})")

def mouseClicked():
    print(f"Mouse clicked at ({mouseX},{mouseY})")

def mouseWheel(count):
    print(f"Mouse wheel: delta={count}, at ({mouseX},{mouseY})")

# ============================================================
# KEY CALLBACKS
# ============================================================
def keyPressed():
    print(f"Key pressed: {key} ({keyCode})")

def keyReleased():
    print(f"Key released: {key} ({keyCode})")


# ============================================================
# RUN PROGRAM
# ============================================================
run()
