import pycessingame


# Game of Life
# Converted from Processing (Java mode) to Processing.py (Python mode)

# Size of cells
cellSize = 5

# Probability of alive at start (%)
probabilityOfAliveAtStart = 15

# Timer
interval = 100
lastRecordedTime = 0

# Colors
alive = color(0, 200, 0)
dead = color(0)

# Arrays for cells
cells = []
cellsBuffer = []

# Pause toggle
pause = False


def setup():
    global cells, cellsBuffer

    size(640, 360)
    stroke(48)
    noSmooth()

    cols = width // cellSize
    rows = height // cellSize

    # Initialize arrays
    cells = [[0 for _ in range(rows)] for _ in range(cols)]
    cellsBuffer = [[0 for _ in range(rows)] for _ in range(cols)]

    # Fill initial random state
    for x in range(cols):
        for y in range(rows):
            state = random(100)
            if state > probabilityOfAliveAtStart:
                state = 0
            else:
                state = 1
            cells[x][y] = int(state)

    background(0)


def draw():
    global lastRecordedTime

    cols = width // cellSize
    rows = height // cellSize

    # Draw cells
    for x in range(cols):
        for y in range(rows):
            if cells[x][y] == 1:
                fill(alive)
            else:
                fill(dead)
            rect(x * cellSize, y * cellSize, cellSize, cellSize)

    # Timer tick
    if millis() - lastRecordedTime > interval:
        if not pause:
            iteration()
            lastRecordedTime = millis()

    # Manual editing during pause
    if pause and mousePressed:
        xCell = int(map(mouseX, 0, width, 0, cols))
        yCell = int(map(mouseY, 0, height, 0, rows))
        xCell = constrain(xCell, 0, cols - 1)
        yCell = constrain(yCell, 0, rows - 1)

        # Toggle based on buffer
        if cellsBuffer[xCell][yCell] == 1:
            cells[xCell][yCell] = 0
            fill(dead)
        else:
            cells[xCell][yCell] = 1
            fill(alive)

    elif pause and not mousePressed:
        # Copy to buffer
        for x in range(cols):
            for y in range(rows):
                cellsBuffer[x][y] = cells[x][y]


def iteration():
    cols = width // cellSize
    rows = height // cellSize

    # Copy to buffer
    for x in range(cols):
        for y in range(rows):
            cellsBuffer[x][y] = cells[x][y]

    # Process each cell
    for x in range(cols):
        for y in range(rows):

            neighbours = 0

            # Check all 8 neighbours
            for xx in range(x - 1, x + 2):
                for yy in range(y - 1, y + 2):
                    if (0 <= xx < cols) and (0 <= yy < rows):
                        if not (xx == x and yy == y):
                            if cellsBuffer[xx][yy] == 1:
                                neighbours += 1

            # Apply Conway's rules
            if cellsBuffer[x][y] == 1:  # Alive
                if neighbours < 2 or neighbours > 3:
                    cells[x][y] = 0
            else:  # Dead
                if neighbours == 3:
                    cells[x][y] = 1


def keyPressed():
    global pause, cells

    cols = width // cellSize
    rows = height // cellSize

    if key == 'r' or key == 'R':
        # Reset random state
        for x in range(cols):
            for y in range(rows):
                state = random(100)
                if state > probabilityOfAliveAtStart:
                    state = 0
                else:
                    state = 1
                cells[x][y] = int(state)

    if key == ' ':
        # Toggle pause
        pause = not pause

    if key == 'c' or key == 'C':
        # Clear grid
        for x in range(cols):
            for y in range(rows):
                cells[x][y] = 0

run()