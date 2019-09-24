import tkinter 
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialog

import configparser
import os
import random

import time
import threading

# Constant Init

window = tkinter.Tk()
window.title("Minesweeper")

flagGraphic = "⛳"  # Image that is displayed on Flag
mineGraphic = "⚙"   # Image that is displayed on Mine
# Colour of Numbers indicating mine presence (Values from Minesweeper)
colour = ['#FFFFFF', '#0000FF', '#008200', '#FF0000', '#000084', '#840000', '#008284', '#840084', '#000000']

#Variable Init

rows = 9            # Default rows on first run
columns = 9         # Default columns on first run
mineCount = 10      # Default mines on first run

# Amount of flags set to mine count, assigned to tk.label that displays it
flagCount = mineCount                 
flagsLabel = tkinter.StringVar()
flagsLabel.set(flagCount)

# Time elapsed since first move, assigned to tk.label that displays it
gameTime = 0
gameTimeLabel = tkinter.StringVar()
gameTimeLabel.set(gameTime)

firstMove = True    # Tracks when user takes first move
gameOver = False    # Tracks when a mine is hit or game is won

gameField = []
buttons = []
customGameSizes = []

# Function Declarations
# x = rows, y = columns when looping

def loadConfig():
    global rows, columns, mineCount, customGameSizes

    # Get data from config.ini to be parsed by createMenu()
    config = configparser.ConfigParser()
    config.read("config.ini")
    rows = config.getint("game", "rows")
    columns = config.getint("game", "columns")
    mineCount = config.getint("game", "mineCount")
    amountofsizes = config.getint("sizes", "amount")
    for x in range(0, amountofsizes):
        customGameSizes.append((config.getint("sizes", "row"+str(x)), config.getint("sizes", "columns"+str(x)), config.getint("sizes", "mineCount"+str(x))))

def saveConfig():
    global rows, columns, mineCount

    # Store data into config.ini for later use
    config = configparser.ConfigParser()
    config.add_section("game")
    config.set("game", "rows", str(rows))
    config.set("game", "columns", str(columns))
    config.set("game", "mineCount", str(mineCount))
    config.add_section("sizes")
    config.set("sizes", "amount", str(min(5,len(customGameSizes))))
    for x in range(0,min(5,len(customGameSizes))):
        config.set("sizes", "row"+str(x), str(customGameSizes[x][0]))
        config.set("sizes", "columns"+str(x), str(customGameSizes[x][1]))
        config.set("sizes", "mineCount"+str(x), str(customGameSizes[x][2]))

    with open("config.ini", "w") as file:
        config.write(file)

def createMenu():
    menubar = tkinter.Menu(window)

    # Size Menu
    menusize = tkinter.Menu(window, tearoff=0)
    menusize.add_command(label="Beginner (9x9 with 10 mineCount)", command=lambda: setSize(9, 9, 10))
    menusize.add_command(label="Intermediate (16x16 with 40 mineCount)", command=lambda: setSize(16, 16, 40))
    menusize.add_command(label="Expert (16x30 with 99 mineCount)", command=lambda: setSize(16, 30, 99))
    menusize.add_separator()
    menusize.add_command(label="Custom", command=setCustomSize)
    if len(customGameSizes) > 0:
        menusize.add_separator()
        for x in range(0, len(customGameSizes)):
            menusize.add_command(label=str(customGameSizes[x][0])+"x"+str(customGameSizes[x][1])+" with "+str(customGameSizes[x][2])+" mineCount", command=lambda customGameSizes=customGameSizes: setSize(customGameSizes[x][0], customGameSizes[x][1], customGameSizes[x][2]))
    menubar.add_cascade(label="Options", menu=menusize)

    # Game type Menu
    gameTypes = tkinter.Menu(window, tearoff=0)
    gameTypes.add_command(label="Default")
    gameTypes.add_command(label="Hexes")
    gameTypes.add_command(label="Linemap")
    menubar.add_cascade(label="Game Type", menu=gameTypes)

    # Exit Command (Find a way to stick to the Right side)
    menubar.add_command(label="Exit", command=lambda: window.destroy())
    
    window.config(menu=menubar)

def setCustomSize():
    global customGameSizes

    # Ask user for new dimensions
    rows = dialog.askinteger("Custom size", "Enter amount of rows")
    columns = dialog.askinteger("Custom size", "Enter amount of columns\nMin: 7")
    while columns < 7:
        columns = dialog.askinteger("Custom size", "Enter amount of columns\nMin: 7")
    mineCount = dialog.askinteger("Custom size", "Enter amount of mines\nMax: " + str((rows*columns)-1))
    while mineCount > (rows*columns)-1:
        mineCount = dialog.askinteger("Custom size", "Enter amount of mines\nMax: " + str((rows*columns)-1))
    
    # Add new dimension to config.ini and restart game
    customGameSizes.insert(0, (rows, columns, mineCount))
    customGameSizes = customGameSizes[0:5]
    setSize(rows, columns, mineCount)
    createMenu()

def setSize(r,c,m):
    global rows, columns, mineCount

    # Sets the new parameters for the game
    rows = r
    columns = c
    mineCount = m
    saveConfig()
    gameRestart()

def prepareGame():
    global rows, columns, mineCount, flagCount, gameField
    
    gameField = []
    # Add tiles or "buttons" to the field
    for x in range(0, rows):
        gameField.append([])
        for y in range(0, columns):
            gameField[x].append(0)

    # Generate Mines
    for _ in range(0, mineCount):
        x = random.randint(0, rows-1)
        y = random.randint(0, columns-1)
        # Check if mine position already has a mine, repeat until free
        while gameField[x][y] == -1:
            x = random.randint(0, rows-1)
            y = random.randint(0, columns-1)
        gameField[x][y] = -1

        # Calculate numbers surrounding mines
        if x != 0:
            if y != 0:
                if gameField[x-1][y-1] != -1:
                    gameField[x-1][y-1] = int(gameField[x-1][y-1]) + 1
            if gameField[x-1][y] != -1:
                gameField[x-1][y] = int(gameField[x-1][y]) + 1
            if y != columns-1:
                if gameField[x-1][y+1] != -1:
                    gameField[x-1][y+1] = int(gameField[x-1][y+1]) + 1
        if y != 0:
            if gameField[x][y-1] != -1:
                gameField[x][y-1] = int(gameField[x][y-1]) + 1
        if y != columns-1:
            if gameField[x][y+1] != -1:
                gameField[x][y+1] = int(gameField[x][y+1]) + 1
        if x != rows-1:
            if y != 0:
                if gameField[x+1][y-1] != -1:
                    gameField[x+1][y-1] = int(gameField[x+1][y-1]) + 1
            if gameField[x+1][y] != -1:
                gameField[x+1][y] = int(gameField[x+1][y]) + 1
            if y != columns-1:
                if gameField[x+1][y+1] != -1:
                    gameField[x+1][y+1] = int(gameField[x+1][y+1]) + 1  

    # Update flag values and sleep to prevent user from breaking script
    flagCount = mineCount
    flagsLabel.set(flagCount)
    time.sleep(0.6)

def prepareWindow():
    global rows, columns, buttons

    # Create header window
    tkinter.Label(window, textvariable=flagsLabel).grid(row=0, column=0, columnspan=3, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
    tkinter.Button(window, text="☺", command=gameRestart).grid(row=0, column=3, columnspan=columns-6, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
    tkinter.Label(window, textvariable=gameTimeLabel).grid(row=0, column=columns-3, columnspan=3, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
    
    # Create and bind event to mouse buttons for each button on the game field
    buttons = []
    for x in range(0, rows):
        buttons.append([])
        for y in range(0, columns):
            b = tkinter.Button(window, text=" ", width=2, command=lambda x=x,y=y: revealCell(x,y))
            b.bind("<Button-3>", lambda e, x=x, y=y:flagCell(x, y))
            b.grid(row=x+1, column=y, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
            buttons[x].append(b)

def gameRestart():
    global gameOver, firstMove, gameTimeThread, gameTime

    # Reset game values to default
    gameOver = False
    firstMove = True
    gameTime = 0
    gameTimeLabel.set(gameTime)
    # Destroy all instances of info windows
    for win in window.winfo_children():
        if type(win) != tkinter.Menu:
            win.destroy()
    # Reinitialise thread and run prepare functions
    gameTimeThread = threading.Timer(1.0, gameTimer)
    prepareWindow()
    prepareGame()

def revealCell(x,y):
    global gameField, buttons, rows, columns, colour, gameOver, firstMove, gameTimeThread

    # Prevent interaction if the game is won/lost
    if gameOver:
        return
    # Start timer thread on first user move
    if firstMove:
        firstMove = False
        gameTimeThread.start()

    buttons[x][y]["text"] = str(gameField[x][y])
    if gameField[x][y] == -1:   # if gameField contains a mine
        buttons[x][y]["text"] = mineGraphic
        buttons[x][y].config(background='red', disabledforeground='black')
        gameOver = True
        #tkinter.messagebox.showinfo("Lose Message")
        revealMines(x,y,rows,columns)

    else:   # otherwise gameField contains
        buttons[x][y].config(disabledforeground=colour[gameField[x][y]])
    # If no value is present in cell, check surrounding cells
    if gameField[x][y] == 0:    
        buttons[x][y]["text"] = " "
        cascadeCell(x,y)

    buttons[x][y]['state'] = 'disabled'
    buttons[x][y].config(relief=tkinter.SUNKEN)
    # Check if player has won
    win = True
    for x in range(0, rows):
        for y in range(0, columns):
            if gameField[x][y] != -1 and buttons[x][y]["state"] == "normal":
                win = False
    if win and gameOver == False:
        #tkinter.messagebox.showinfo("Win Message")
        gameOver = True
        revealMines(x,y,rows,columns)

def cascadeCell(x,y):
    global gameField, buttons, colour, rows, columns

    # If already activated
    if buttons[x][y]["state"] == "disabled":
        return
    # if cell has adjacent mine
    if gameField[x][y] != 0:
        buttons[x][y]["text"] = str(gameField[x][y])
    else:   # Cell has no adjacent mines
        buttons[x][y]["text"] = " "
    buttons[x][y].config(disabledforeground=colour[gameField[x][y]])
    buttons[x][y].config(relief=tkinter.SUNKEN)
    buttons[x][y]['state'] = 'disabled'
    # Check each adjacent cell
    if gameField[x][y] == 0:
        if x != 0 and y != 0:
            cascadeCell(x-1,y-1)
        if x != 0:
            cascadeCell(x-1,y)
        if x != 0 and y != columns-1:
            cascadeCell(x-1,y+1)
        if y != 0:
            cascadeCell(x,y-1)
        if y != columns-1:
            cascadeCell(x,y+1)
        if x != rows-1 and y != 0:
            cascadeCell(x+1,y-1)
        if x != rows-1:
            cascadeCell(x+1,y)
        if x != rows-1 and y != columns-1:
            cascadeCell(x+1,y+1)

def flagCell(x,y):
    global buttons, flagCount

    if gameOver:
        return
    # If the cell is already flagged, remove it
    if buttons[x][y]["text"] == flagGraphic:
        updateFlagCount(1)
        buttons[x][y]["text"] = " "
        buttons[x][y]["state"] = "normal"
    # Otherwise flag the cell
    elif buttons[x][y]["text"] == " " and buttons[x][y]["state"] == "normal" and flagCount > 0:
        updateFlagCount(-1)
        buttons[x][y]["text"] = flagGraphic
        buttons[x][y]["state"] = "disabled"

def updateFlagCount(change):
    global flagCount

    flagCount += change
    flagsLabel.set(flagCount)

def revealMines(x,y,rows,columns):
    for x in range(0, rows):
        for y in range(columns):
            # Flagged Correctly
            if gameField[x][y] == -1 and buttons[x][y]["text"] == flagGraphic:
                buttons[x][y].config(background='lime', disabledforeground='black')
            # Flagged Incorrectly
            if gameField[x][y] != -1 and buttons[x][y]["text"] == flagGraphic:
                buttons[x][y].config(background='gray', disabledforeground='black')
            # Unflagged Mine
            if gameField[x][y] == -1 and buttons[x][y]["text"] != flagGraphic:
                buttons[x][y]["text"] = mineGraphic
            buttons[x][y]["state"] = 'disabled'
            
def gameTimer():
    global gameTime, firstMove, gameOver

    while firstMove == 0 and gameOver == 0:
        gameTime += 1
        gameTimeLabel.set(gameTime)
        time.sleep(1)        

if __name__ == "__main__":
    # Check to see if config data already exists to load from
    if os.path.exists("config.ini"):
        loadConfig()
    else:
        saveConfig()

    # Initalise game
    gameTimeThread = threading.Timer(1.0, gameTimer)

    createMenu()
    prepareWindow()
    prepareGame()
    window.mainloop() 
