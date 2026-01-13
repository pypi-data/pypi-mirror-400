# pycessingame

![For Education](https://img.shields.io/badge/for-education-blue)
![Made for Thonny](https://img.shields.io/badge/made%20for-Thonny-orange)
![IDEs](https://img.shields.io/badge/IDEs-Thonny%20|%20VS%20Code%20|%20PyCharm-blue)
![Runs everywhere](https://img.shields.io/badge/runs-everywhere%20Python%20runs-success)

## Deutsch

Processing-Style kreatives coden mit Python & Pygame für Ausbildung und Lehre.

PYCESSINGAME bringt den Geist von Processing in die Python-Welt – leichtgewichtig,
direkt und ohne Umwege. Es richtet sich an Lehrende, Entwicklerinnen, 
Künstlerinnen und Designerinnen, die visuelles, interaktives Creative Coding
lieben und dabei die Einfachheit von Processing schätzen.

Mit einer bewusst vertrauten API kannst du sofort loslegen:
setup(), draw(), ellipse(), fill(), stroke(), color(), random() – alles 
fühlt sich an wie Processing, nur eben pures Python.

Warum noch eine Implementierung?
- einfach Python, kein Java, kein transpiling
- gleiche Namen, gleiche Konzepte, gleiches Denken
- Schreibstil nach Geschmack: camelCase oder snake_case
- nur von einem anderen python paket (pygame) abhängig
- gleich los zeichnen und nicht um Fenster, Rendering und Events kümmmern
- einfacher Start und die ganze Python-Welt zur Verfügung
- völlig freie Nutzung

Einfache **Installation**:
`pip install pycessingame`

Entwickelt mit Augenmerk auf Anfängerfreundlichkeit für Ausbildung, Lehrer und kreatives coden.  
Intensiv im Einsatz mit der Thonny Python IDE.

## English

Processing-style creative coding not only for education using Python and Pygame

PYCESSINGAME brings the spirit of Processing to the Python world — lightweight, 
direct, and without detours. It is designed for educators, developers, 
artists, and designers who love visual, interactive creative coding and 
appreciate the simplicity of Processing.

With a deliberately familiar API, you can start right away:
setup(), draw(), ellipse(), fill(), stroke(), color(), random() — everything 
feels like Processing, just pure Python.

Why yet another implementation?
- pure Python — no Java, no transpiling
- same names, same concepts, same way of thinking
- coding style of your choice: camelCase or snake_case
- depends on only one external Python package (pygame)
- start drawing immediately without worrying about windows, rendering, or events
- easy to get started, with the entire Python ecosystem at your disposal 
- completely free to use

Easy **installation**:
`pip install pycessingame`

Designed for education and beginner-friendly creative coding.  
Intensively used with the Thonny Python IDE.

## Beispiel  / Example

```python
import pycessingame

def setup():
    size(640, 480)
    frameRate(60)
    
def draw():
    background(30, 120, 200)
    fill(255, 200, 0)
    noStroke()
    ellipse(width/2, height/2, 150, 150)
    
run()
```

![Screenshot](docs/screenshot.png)

## Benutzung / Usage

### Deutsch

PYCESSINGAME wird genau wie Processing verwendet. Du schreibst ganz normalen Processing-Code – mit nur zwei kleinen Anpassungen:

Ganz oben die Zeile

```import pycessingame```

Ganz am Ende des Programms ein Aufruf von

```run()```


Alles dazwischen ist klassischer Processing-Stil:
setup(), draw(), Zeichenfunktionen, Events, Farben, Zufall, Maus und Tastatur.

Es ist kein spezielles Framework-Wissen nötig – wer Processing kennt, kann
sofort loslegen.

**Migration von bestehendem Processing-Code**

Bestehender Processing-Code (Java / PDE) lässt sich in vielen Fällen nahezu
1:1 nach Python übertragen. Gängige Large Language Models (LLMs) können dabei sehr gut helfen.

Ein einfacher Prompt wie zum Beispiel:

```"Convert the following Processing code into Python assuming the Processing API is completely available."```

reicht in der Praxis oft aus, um bestehenden Processing-Code direkt in
funktionsfähigen Python-Code für PYCESSINGAME zu überführen. 

### English

PYCESSINGAME is used exactly like Processing. You write ordinary Processing-style code — with only two small adjustments:

Add

```import pycessingame```

at the very top of your file.

Call

```run()```

at the very end of your program.

Everything in between follows the familiar Processing workflow:
setup(), draw(), drawing commands, events, colors, randomness, mouse and
keyboard handling.

No special framework knowledge is required — if you know Processing, you can
start immediately.

**Migrating existing Processing sketches**

Existing Processing sketches (Java / PDE) can often be ported almost 1:1
to Python. Modern Large Language Models (LLMs) are especially effective at this task.
In practice, a simple prompt such as:

```"Convert the following Processing code into Python assuming the Processing API is completely available."```

is usually sufficient to transform existing Processing code into working
PYCESSINGAME code.

## Referenzen / references

https://processing.org/

https://openprocessing.org/

https://p5js.org/

https://pypi.org/project/p5/

https://py5coding.org/index.html


## Notizen / Gedächtnisstütze

git tag & push => build & pypi upload:

`git tag v0.0.0`

`git push origin v0.0.0`

Realisiert mit einen git pre-push hook (.git/hooks/pre-push)und pypi Zugangsdaten in ~/.pypirc.