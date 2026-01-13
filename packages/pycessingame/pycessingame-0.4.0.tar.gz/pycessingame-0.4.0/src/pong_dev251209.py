from py_processing_game_09 import *

# Ballposition
x, y = 350, 250
vx, vy = 8, 8
spieler2_y = 500/2-100/2
score1, score2 = 0, 0
pause_ab = 0

def reset():
    global x, y, vy, vx
    global pause_ab
    x, y = 350, 250
    vy = random(2,8)    
    pause_ab = millis()

def setup():
   size(600,500)
   windowTitle("PONG")
   noCursor()
   
def draw():
    global x, y, vy, vx
    global spieler2_y
    global score1, score2
    
    #zeichnen
    background(200)
    fill(0)
    rect(550,min(mouse_y,500-100),25,100)
    rect(25,spieler2_y,25,100)
    textSize(60)
    fill(255)
    textAlign(LEFT)
    text(score1,50,20)
    textAlign(RIGHT)
    text(score2,600-50,20)

    if millis()-pause_ab > 2000:
        # Ball
        fill(255,0,0)
        ellipse(x,y,25,25)
        #animation
        x=x+vx
        y=y+vy

    # Tastenbehandlung
    # Wenn Pfeil Hoch gedrückt wird, dann pos. nach oben verschieben
    if keyPressed:
        if key == 'w':
            spieler2_y = spieler2_y - 20
        if key == 's':
            spieler2_y = spieler2_y + 20
    if spieler2_y < 0:
        spieler2_y = 0
    if spieler2_y > 500-100:
        spieler2_y = 500-100
        
    
    # Abprallen an den Rändern des Fensters
    if y > 488.5:
        vy=-vy
    if x > 588.5:
        # rechts raus
        score2 = score2 + 1
        reset()
        vx=-vx
    if y < 12.5:
        vy=-vy
    if x < 12.5:
        score1 = score1 + 1
        reset()
        vx=-vx
        
    # Abprallen am Schläger von Spieler1
    if x + 12.5 > 550 and y > min(mouse_y, 500-100) and y < min(mouse_y, 500-100) + 100:
        vx = -vx
    # Abprallen am Schläger von Spieler2
    if x - 12.5 < 25+25 and y > spieler2_y and y < spieler2_y + 100:
        vx = -vx
         
run()