import pycessingame
from csv import *

class HighscoreEintrag:
    def __init__(self, name, punkte):
        self.name = name
        self.punkte = int(punkte)
    
    def __str__(self):
        return self.name + ": " + str(self.punkte) + " Punkte"

highscore = []
aktuell = -1
maximum = -1

def setup():
    size(1000, 700);
    background(0)
    ladeTabelle("punkte.csv")
    zeichneBalken()
    
def draw():
    zeichneBalken()
    
def keyPressed():
    if key == 'a':
        thread(maximumssuche)

def ladeTabelle(dateiname):
    file = open(dateiname)
    csvreader = reader(file)
    next(csvreader)
    global highscore
    highscore = []
    for line in csvreader:
        highscore.append(HighscoreEintrag(line[0], line[1]))

def zeichneBalken():
    background(0)
    fill(255)
    textSize(24)
    text("Punkte", 10, 20);
    textSize(16)
    
    for i, h in enumerate(highscore):
        fill(20,25,165)
        
        # aktuelle Elemente farblich hervorheben
        # ----------------------------------------------------------------------
        # ToDo: Falls i dem aktuell untersuchtem oder der aktuellen Maximal-
        #      position entspricht, muss eine andere Farbe gewählt werden
        # ----------------------------------------------------------------------
        if i == aktuell:
            fill("green")
        elif i == maximum:
            fill("purple")
        if h.punkte>=0:
            rect(140, 45+i*15, h.punkte+1, 13)
        fill(255)
        text(h.name, 10, 45+i*15);
        text(str(h.punkte), 100, 45+i*15);

def maximumssuche():
    global aktuell, maximum
    for i, h in enumerate(highscore):
        aktuell = i
        if maximum < 0 or h.punkte > highscore[maximum].punkte:
            maximum = i
        delay(1000)
    
run()