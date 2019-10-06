# -*- coding: utf-8 -*-

# # # # # #
# Imports #
# # # # # #
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialog
import tkinter.font as tkFont

import configparser
import os
import random
import sys

import time
import threading

# # # # # # # # #
# Constant Init #
# # # # # # # # #
sysType = 0
cellDisplay = ''

window = tk.Tk()
window.title("Minesweeper")
window.iconbitmap("game.ico")
window.resizable(0,0)
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=12, weight=(tk.font.BOLD))

flagGraphic = "⛳"  # Image that is displayed on Flag
mineGraphic = "⦻"   # Image that is displayed on Mine
resetGraphic = "☺"   # Image that is displayed on Reset Button
# Colour of Numbers indicating mine presence (Values from Minesweeper)
colour = ['#FFFFFF', '#0000FF', '#008200', '#FF0000', '#000084', '#840000', '#008284', '#840084', '#000000']
validNum = ['1','2','3','4','5','6','7','8']

# # # # # # # # #
# Variable Init #
# # # # # # # # #
rows = 9            # Default rows on first run
columns = 9         # Default columns on first run
mineCount = 10      # Default mines on first run

# Amount of flags set to mine count, assigned to tk.label that displays it
flagCount = mineCount                 
flagsLabel = tk.StringVar()
flagsLabel.set(flagGraphic+str(flagCount))

# Time elapsed since first move, assigned to tk.label that displays it
gameTime = 0
gameTimeLabel = tk.StringVar()
gameTimeLabel.set(gameTime)

# Set up reset graphic
resetLabel = tk.StringVar()
resetLabel.set(resetGraphic)

firstMove = True    # Tracks when user takes first move
gameOver = False    # Tracks when a mine is hit or game is won

gameField = []          # Positioning of cells
cell = []            # Tracks each cell
customGameSizes = []    # Stores players custom game stats

# # # # # # # # # # # # #
# Function Declarations #
# x = columns, y = rows #
# # # # # # # # # # # # #

def loadConfig():
    global rows, columns, mineCount, customGameSizes

    # Get data from config.ini to be parsed by createMenu()
    config = configparser.ConfigParser()
    config.read("config.ini")
    rows = config.getint("game", "rows")
    columns = config.getint("game", "columns")
    mineCount = config.getint("game", "mines")
    amountofsizes = config.getint("sizes", "amount")
    for x in range(0, amountofsizes):
        customGameSizes.append((config.getint("sizes", "row"+str(x)), config.getint("sizes", "columns"+str(x)), config.getint("sizes", "mines"+str(x))))

def saveConfig():
    global rows, columns, mineCount

    # Store data into config.ini for later use
    config = configparser.ConfigParser()
    config.add_section("game")
    config.set("game", "rows", str(rows))
    config.set("game", "columns", str(columns))
    config.set("game", "mines", str(mineCount))
    config.add_section("sizes")
    config.set("sizes", "amount", str(min(5,len(customGameSizes))))
    for x in range(0,min(5,len(customGameSizes))):
        config.set("sizes", "row"+str(x), str(customGameSizes[x][0]))
        config.set("sizes", "columns"+str(x), str(customGameSizes[x][1]))
        config.set("sizes", "mines"+str(x), str(customGameSizes[x][2]))

    with open("config.ini", "w") as file:
        config.write(file)

def createMenu():
    menuBar = tk.Menu(window)

    # Size Menu
    sizeMenu = tk.Menu(window, tearoff=0)
    sizeMenu.add_command(label="Beginner (9x9 with 10 mineCount)", command=lambda: setSize(9, 9, 10))
    sizeMenu.add_command(label="Intermediate (16x16 with 40 mineCount)", command=lambda: setSize(16, 16, 40))
    sizeMenu.add_command(label="Expert (16x30 with 99 mineCount)", command=lambda: setSize(16, 30, 99))
    sizeMenu.add_separator()
    sizeMenu.add_command(label="Custom", command=setCustomSize)
    if len(customGameSizes) > 0:
        sizeMenu.add_separator()
        for x in range(0, len(customGameSizes)):
            sizeMenu.add_command(label=str(customGameSizes[x][0])+"x"+str(customGameSizes[x][1])+" with "+str(customGameSizes[x][2])+" mineCount", command=lambda customGameSizes=customGameSizes: setSize(customGameSizes[x][0], customGameSizes[x][1], customGameSizes[x][2]))
    menuBar.add_cascade(label="Options", menu=sizeMenu)

    # Game type Menu
    gameTypes = tk.Menu(window, tearoff=0)
    gameTypes.add_command(label="Default")
    gameTypes.add_command(label="Hexes")
    gameTypes.add_command(label="Linemap")
    menuBar.add_cascade(label="Game Type", menu=gameTypes)

    # Exit Command
    menuBar.add_command(label="Exit", command=lambda: window.destroy())
    
    window.config(menu=menuBar)

def setCustomSize():
    global customGameSizes

    # Ask user for new dimensions
    newRows = dialog.askinteger("Custom size", "Enter amount of rows")
    if isinstance(newRows, int) == False:
        return
    newColumns = dialog.askinteger("Custom size", "Enter amount of columns\nMin: 7")
    if isinstance(newColumns, int):
        while newColumns < 7:
            newColumns = dialog.askinteger("Custom size", "Enter amount of columns\nMin: 7")
    else:
        return
    newMineCount = dialog.askinteger("Custom size", "Enter amount of mines\nMax: " + str((newRows*newColumns)-1))
    if isinstance(newMineCount, int):
        while newMineCount > (newRows*newColumns)-1:
            newMineCount = dialog.askinteger("Custom size", "Enter amount of mines\nMax: " + str((newRows*newColumns)-1))

    # Add new dimension to config.ini and restart game
    customGameSizes.insert(0, (newRows, newColumns, newMineCount))
    customGameSizes = customGameSizes[0:5]
    setSize(newRows, newColumns, newMineCount)
    createMenu()

def setSize(r,c,m):
    global rows, columns, mineCount

    # Sets the new parameters for the game
    rows = r
    columns = c
    mineCount = m
    saveConfig()
    gameRestart()

def prepareGame(xPos,yPos):
    global rows, columns, mineCount, flagCount, gameField
    
    gameField = []
    # Add cells to the field
    for x in range(0, rows):
        gameField.append([])
        for y in range(0, columns):
            gameField[x].append(0)

    # Generate Mines
    for _ in range(0, mineCount):
        x = random.randint(0, rows-1)
        y = random.randint(0, columns-1)
        # Check if mine position already has a mine or is at the same place the user wants to reveal, rerandomise it's location if there's a conflict
        while gameField[x][y] == -1 or (x == xPos and y == yPos):
            x = random.randint(0, rows-1)
            y = random.randint(0, columns-1)
        gameField[x][y] = -1

        # Calculate value of cells that have at least one adjacent mine
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
    try:
        if int(gameField[xPos][yPos]) !=0:
            prepareGame(xPos,yPos)
    except RecursionError:
        print("Recursion Limit Reached, no pocket today!")
        
    # Update flag values
    flagCount = mineCount
    flagsLabel.set(flagGraphic+str(flagCount))

def prepareWindow():
    global rows, columns, cell, sysType

    # Create header window
    tk.Label(window, textvariable=flagsLabel).grid(row=0, column=0, columnspan=3, sticky=tk.N+tk.W+tk.S+tk.E)
    tk.Button(window, textvariable=resetLabel, command=gameRestart).grid(row=0, column=3, columnspan=columns-6, sticky=tk.N+tk.W+tk.S+tk.E)
    tk.Label(window, textvariable=gameTimeLabel).grid(row=0, column=columns-3, columnspan=3, sticky=tk.N+tk.W+tk.S+tk.E)
    
    # Create and bind event to mouse buttones for each cell on the game field
    cell = []
    for x in range(0, rows):
        cell.append([])
        for y in range(0, columns):
            b = tk.Button(window, text=" ", width=3, height = 1, command=lambda x=x,y=y: revealCell(x,y))
            if sysType == 0:
                b.bind("<ButtonRelease-2>", lambda e, x=x, y=y:checkCell(x, y))
                b.bind("<ButtonRelease-3>", lambda e, x=x, y=y:flagCell(x, y))
            if sysType == 1:
                #b.bind("<space>", lambda e, x=x, y=y:checkCell(x, y))
                b.bind("<ButtonRelease-2>", lambda e, x=x, y=y:flagCell(x, y))
            b.grid(row=x+1, column=y, sticky=tk.N+tk.W+tk.S+tk.E)
            cell[x].append(b)
    if gameTimeThread.isAlive(): 
        gameTimeThread.join()

def gameRestart():
    global gameOver, firstMove, gameTimeThread, gameTime

    # Reset game values to default
    gameOver = False
    firstMove = True
    gameTime = 0
    gameTimeLabel.set(gameTime)
    # Destroy all instances of info windows
    for win in window.winfo_children():
        if type(win) != tk.Menu:
            win.destroy()
    # Reinitialise thread and run prepare functions
    gameTimeThread = threading.Timer(1.0, gameTimer)
    prepareWindow()

def revealCell(x,y):
    global gameField, cell, rows, columns, colour, gameOver, firstMove, gameTimeThread, cellDisplay

    # Prevent interaction if the game is won/lost
    if gameOver:
        return
    # Start timer thread on first user move
    if firstMove:
        firstMove = False
        prepareGame(x,y)    # Layout mines (Won't place on first cell)
        gameTimeThread.start()

    cell[x][y]["text"] = str(gameField[x][y])
    if gameField[x][y] == -1:   # if gameField contains a mine
        gameLose(x,y)
    # otherwise gameField contains a non-mine
    else:
        cell[x][y].config(**{ cellDisplay: 'lightgrey', 'disabledforeground': colour[gameField[x][y]] })

    # Then, if no value is present in cell, check surrounding cells
    if gameField[x][y] == 0:    
        cell[x][y]["text"] = " "
        cascadeCell(x,y,False)

    cell[x][y]['state'] = 'disabled'
    cell[x][y].config(relief=tk.SUNKEN)
    # Check if player has won
    checkWin()

def cascadeCell(x,y,check):
    global gameField, cell, colour, rows, columns

    # If already activated
    if cell[x][y]["state"] == "disabled" and check == False:
        return
    
    if gameField[x][y] == -1:   # if gameField contains a mine
        gameLose(x,y)
        return
    # if cell has adjacent mine
    if gameField[x][y] != 0:
        cell[x][y]["text"] = str(gameField[x][y])
    else:   # Cell has no adjacent mines
        cell[x][y]["text"] = " "
    cell[x][y].config(**{ cellDisplay: 'lightgrey', 'disabledforeground': colour[gameField[x][y]] })
    cell[x][y].config(relief=tk.SUNKEN)
    cell[x][y]['state'] = 'disabled'
    # Check each adjacent cell
    if gameField[x][y] == 0 or check:
        if x != 0 and y != 0:
            cascadeCell(x-1,y-1,False)
        if x != 0:
            cascadeCell(x-1,y,False)
        if x != 0 and y != columns-1:
            cascadeCell(x-1,y+1,False)
        if y != 0:
            cascadeCell(x,y-1,False)
        if y != columns-1:
            cascadeCell(x,y+1,False)
        if x != rows-1 and y != 0:
            cascadeCell(x+1,y-1,False)
        if x != rows-1:
            cascadeCell(x+1,y,False)
        if x != rows-1 and y != columns-1:
            cascadeCell(x+1,y+1,False)

def checkCell(x, y):
    global gameField, cell, rows, columns, colour, gameOver, flagGraphic, validNum
    
    flagCheck = 0

    if gameOver:
        return

    if cell[x][y]['text'] in validNum:
        for ix in range (-1, 2):
            for iy in range (-1, 2):
                if x+ix < rows and y+iy < columns:
                    if cell[x+ix][y+iy]['text'] == flagGraphic:
                        flagCheck += 1
        if flagCheck == int(cell[x][y]['text']):
            cascadeCell(x,y,True)

    checkWin()

def flagCell(x,y):
    global cell, flagCount

    if gameOver:
        return
    # If the cell is already flagged, remove it
    if cell[x][y]["text"] == flagGraphic:
        updateFlagCount(1)
        cell[x][y]["text"] = " "
        cell[x][y]["state"] = "normal"
    # Otherwise flag the cell
    elif cell[x][y]["text"] == " " and cell[x][y]["state"] == "normal" and flagCount > 0:
        updateFlagCount(-1)
        cell[x][y]["text"] = flagGraphic
        cell[x][y]["state"] = "disabled"

def updateFlagCount(change):
    global flagCount

    flagCount += change
    flagsLabel.set(flagGraphic+str(flagCount))

def checkWin():
    global gameField, cell, rows, columns, gameOver, flagGraphic

    win = True
    for x in range(0, rows):
        for y in range(0, columns):
            if gameField[x][y] != -1 and (cell[x][y]["state"] == "normal" or cell[x][y]["text"] == flagGraphic):
                win = False
    if win and gameOver == False:
        #tk.messagebox.showinfo("Win Message")
        gameOver = True
        revealMines(x,y,rows,columns)

def gameLose(x,y):
    global cell, rows, columns, gameOver, mineGraphic, cellDisplay

    #cell[x][y]["text"] = mineGraphic
    cell[x][y].config(**{ 'text': mineGraphic, cellDisplay: 'red', 'disabledforeground': 'black' })
    gameOver = True
    #tk.messagebox.showinfo("Lose Message")
    revealMines(x,y,rows,columns)

def revealMines(x,y,rows,columns):
    global cellDisplay

    for x in range(0, rows):
        for y in range(columns):
            # Flagged Correctly
            if gameField[x][y] == -1 and cell[x][y]["text"] == flagGraphic:
                cell[x][y].config(**{ cellDisplay: 'lime', 'disabledforeground': 'black' })
            # Flagged Incorrectly
            if gameField[x][y] != -1 and cell[x][y]["text"] == flagGraphic:
                cell[x][y].config(**{ cellDisplay: 'pink', 'disabledforeground': 'black' })
            # Unflagged Mine
            if gameField[x][y] == -1 and cell[x][y]["text"] != flagGraphic:
                cell[x][y]["text"] = mineGraphic
            cell[x][y]["state"] = 'disabled'
            
def gameTimer():
    global gameTime, firstMove, gameOver

    while firstMove == 0 and gameOver == 0:
        gameTime += 1
        gameTimeLabel.set(gameTime)
        time.sleep(1)        

# # # # # #
# M A I N #
# # # # # #
if __name__ == "__main__":
    #global sysType, cellDisplay

    # Check to see if config data already exists to load from
    if os.path.exists("config.ini"):
        loadConfig()
    else:
        saveConfig()

    if sys.platform in ["win32", "win64"]:
        sysType=0
        cellDisplay = "background"
    if sys.platform == "darwin":
        sysType=1
        cellDisplay = "highlightbackground"

    # Initalise game
    createMenu()
    gameRestart()
    window.mainloop() 
