import tkinter 
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialog

import configparser
import os
import random

import time
import threading

window = tkinter.Tk()

window.title("Minesweeper")

#Constants Init

flagGraphic = "⛳"  # Image that is displayed on Flag
mineGraphic = "⚙"   # Image that is displayed on Mine
# Colour of Numbers indicating mine presence (Values from Minesweeper)
colour = ['#FFFFFF', '#0000FF', '#008200', '#FF0000', '#000084', '#840000', '#008284', '#840084', '#000000']

#Variables Init

rowNum = 9      # Default rows on first run
cols = 9        # Default cols on first run
mines = 10      # Default mines on first run

# Amount of flags set to mine count, assigned to tk.label that displays it
flagCount = mines                 
flagsLabel = tkinter.StringVar()
flagsLabel.set(flagCount)

# Time elapsed since first move, assigned to tk.label that displays it
gameTime = 0
gameTimeLabel = tkinter.StringVar()
gameTimeLabel.set(gameTime)

firstMove = True    # Tracks when user takes first move
gameOver = False    # Tracks when a mine is hit or game is won

field = []
buttons = []
customGameSizes = []

#Functions Declarations

def createMenu():
    menubar = tkinter.Menu(window)
    menusize = tkinter.Menu(window, tearoff=0)
    menusize.add_command(label="Beginner (9x9 with 10 mines)", command=lambda: setSize(9, 9, 10))
    menusize.add_command(label="Intermediate (16x16 with 40 mines)", command=lambda: setSize(16, 16, 40))
    menusize.add_command(label="Expert (16x30 with 99 mines)", command=lambda: setSize(16, 30, 99))
    menusize.add_separator()
    menusize.add_command(label="Custom", command=setCustomSize)
    if len(customGameSizes) > 0:
        menusize.add_separator()
        for x in range(0, len(customGameSizes)):
            menusize.add_command(label=str(customGameSizes[x][0])+"x"+str(customGameSizes[x][1])+" with "+str(customGameSizes[x][2])+" mines", command=lambda customGameSizes=customGameSizes: setSize(customGameSizes[x][0], customGameSizes[x][1], customGameSizes[x][2]))
    menubar.add_cascade(label="Options", menu=menusize)
    menubar.add_command(label="Exit", command=lambda: window.destroy())
    window.config(menu=menubar)

def setCustomSize():
    global customGameSizes
    rows = dialog.askinteger("Custom size", "Enter amount of rowNum")
    columns = dialog.askinteger("Custom size", "Enter amount of columns")
    mines = dialog.askinteger("Custom size", "Enter amount of mines")
    while mines > rows*columns:
        mines = dialog.askinteger("Custom size", "Maximum mines for this dimension is: " + str(rows*columns) + "\nEnter amount of mines")
    customGameSizes.insert(0, (rows,columns,mines))
    customGameSizes = customGameSizes[0:5]
    setSize(rows,columns,mines)
    createMenu()

def setSize(r,c,m):
    global rowNum, cols, mines
    rowNum = r
    cols = c
    mines = m
    saveConfig()
    gameRestart()

def saveConfig():
    global rowNum, cols, mines
    #configuration
    config = configparser.ConfigParser()
    config.add_section("game")
    config.set("game", "rowNum", str(rowNum))
    config.set("game", "cols", str(cols))
    config.set("game", "mines", str(mines))
    config.add_section("sizes")
    config.set("sizes", "amount", str(min(5,len(customGameSizes))))
    for x in range(0,min(5,len(customGameSizes))):
        config.set("sizes", "row"+str(x), str(customGameSizes[x][0]))
        config.set("sizes", "cols"+str(x), str(customGameSizes[x][1]))
        config.set("sizes", "mines"+str(x), str(customGameSizes[x][2]))

    with open("config.ini", "w") as file:
        config.write(file)

def loadConfig():
    global rowNum, cols, mines, customGameSizes
    config = configparser.ConfigParser()
    config.read("config.ini")
    rowNum = config.getint("game", "rowNum")
    cols = config.getint("game", "cols")
    mines = config.getint("game", "mines")
    amountofsizes = config.getint("sizes", "amount")
    for x in range(0, amountofsizes):
        customGameSizes.append((config.getint("sizes", "row"+str(x)), config.getint("sizes", "cols"+str(x)), config.getint("sizes", "mines"+str(x))))

def prepareGame():
    global rowNum, cols, mines, field, flagCount
    field = []
    for x in range(0, rowNum):
        field.append([])
        for y in range(0, cols):
            #add button and init value for game
            field[x].append(0)
    #generate mines
    for _ in range(0, mines):
        x = random.randint(0, rowNum-1)
        y = random.randint(0, cols-1)
        #prevent spawning mine on top of each other
        while field[x][y] == -1:
            x = random.randint(0, rowNum-1)
            y = random.randint(0, cols-1)
        field[x][y] = -1
        if x != 0:
            if y != 0:
                if field[x-1][y-1] != -1:
                    field[x-1][y-1] = int(field[x-1][y-1]) + 1
            if field[x-1][y] != -1:
                field[x-1][y] = int(field[x-1][y]) + 1
            if y != cols-1:
                if field[x-1][y+1] != -1:
                    field[x-1][y+1] = int(field[x-1][y+1]) + 1
        if y != 0:
            if field[x][y-1] != -1:
                field[x][y-1] = int(field[x][y-1]) + 1
        if y != cols-1:
            if field[x][y+1] != -1:
                field[x][y+1] = int(field[x][y+1]) + 1
        if x != rowNum-1:
            if y != 0:
                if field[x+1][y-1] != -1:
                    field[x+1][y-1] = int(field[x+1][y-1]) + 1
            if field[x+1][y] != -1:
                field[x+1][y] = int(field[x+1][y]) + 1
            if y != cols-1:
                if field[x+1][y+1] != -1:
                    field[x+1][y+1] = int(field[x+1][y+1]) + 1  
    flagCount = mines
    flagsLabel.set(flagCount)

def prepareWindow():
    global rowNum, cols, buttons
    tkinter.Label(window, textvariable=flagsLabel).grid(row=0, column=0, columnspan=3, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
    tkinter.Button(window, text="☺", command=gameRestart).grid(row=0, column=3, columnspan=cols-6, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
    tkinter.Label(window, textvariable=gameTimeLabel).grid(row=0, column=cols-3, columnspan=3, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
    buttons = []
    for x in range(0, rowNum):
        buttons.append([])
        for y in range(0, cols):
            b = tkinter.Button(window, text=" ", width=2, command=lambda x=x,y=y: revealCell(x,y))
            b.bind("<Button-3>", lambda e, x=x, y=y:flagCell(x, y))
            b.grid(row=x+1, column=y, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
            buttons[x].append(b)

def gameRestart():
    global gameOver, firstMove, gameTimeThread, gameTime
    gameOver = False
    firstMove = True
    gameTime = 0
    gameTimeLabel.set(gameTime)
    #destroy all - prevent memory leak
    for x in window.winfo_children():
        if type(x) != tkinter.Menu:
            x.destroy()
    gameTimeThread = threading.Timer(1.0, gameTimer)
    prepareWindow()
    prepareGame()

def revealCell(x,y):
    global field, buttons, colour, gameOver, firstMove, rowNum, cols, gameTimeThread
    if gameOver:
        return
    if firstMove:
        firstMove = False
        gameTimeThread.start()
    buttons[x][y]["text"] = str(field[x][y])
    if field[x][y] == -1:
        buttons[x][y]["text"] = mineGraphic
        buttons[x][y].config(background='red', disabledforeground='black')
        gameOver = True
        #tkinter.messagebox.showinfo("Lose Message")
        revealMines(x,y,rowNum,cols)

    else:
        buttons[x][y].config(disabledforeground=colour[field[x][y]])
    if field[x][y] == 0:
        buttons[x][y]["text"] = " "
        #now repeat for all buttons nearby which are 0... kek
        cascadeCell(x,y)
    buttons[x][y]['state'] = 'disabled'
    buttons[x][y].config(relief=tkinter.SUNKEN)
    checkWin()

def cascadeCell(x,y):
    global field, buttons, colour, rowNum, cols
    if buttons[x][y]["state"] == "disabled":
        return
    if field[x][y] != 0:
        buttons[x][y]["text"] = str(field[x][y])
    else:
        buttons[x][y]["text"] = " "
    buttons[x][y].config(disabledforeground=colour[field[x][y]])
    buttons[x][y].config(relief=tkinter.SUNKEN)
    buttons[x][y]['state'] = 'disabled'
    if field[x][y] == 0:
        if x != 0 and y != 0:
            cascadeCell(x-1,y-1)
        if x != 0:
            cascadeCell(x-1,y)
        if x != 0 and y != cols-1:
            cascadeCell(x-1,y+1)
        if y != 0:
            cascadeCell(x,y-1)
        if y != cols-1:
            cascadeCell(x,y+1)
        if x != rowNum-1 and y != 0:
            cascadeCell(x+1,y-1)
        if x != rowNum-1:
            cascadeCell(x+1,y)
        if x != rowNum-1 and y != cols-1:
            cascadeCell(x+1,y+1)

def flagCell(x,y):
    global buttons, flagCount
    if gameOver:
        return
    if buttons[x][y]["text"] == flagGraphic:
        updateFlagCount(1)
        buttons[x][y]["text"] = " "
        buttons[x][y]["state"] = "normal"
    elif buttons[x][y]["text"] == " " and buttons[x][y]["state"] == "normal" and flagCount > 0:
        updateFlagCount(-1)
        buttons[x][y]["text"] = flagGraphic
        buttons[x][y]["state"] = "disabled"

def updateFlagCount(change):
    global flagCount
    flagCount += change
    flagsLabel.set(flagCount)

def checkWin():
    global buttons, field, rowNum, cols, gameOver
    win = True
    for x in range(0, rowNum):
        for y in range(0, cols):
            if field[x][y] != -1 and buttons[x][y]["state"] == "normal":
                win = False
    if win:
        #tkinter.messagebox.showinfo("Win Message")
        gameOver = True
        revealMines(x,y,rowNum,cols)
        
def revealMines(x,y,rowNum,cols):
    for x in range(0, rowNum):
        for y in range(cols):
            # Flagged Correctly
            if field[x][y] == -1 and buttons[x][y]["text"] == flagGraphic:
                buttons[x][y].config(background='lime', disabledforeground='black')
            # Flagged Incorrectly
            if field[x][y] != -1 and buttons[x][y]["text"] == flagGraphic:
                buttons[x][y].config(background='gray', disabledforeground='black')
            # Unflagged Mine
            if field[x][y] == -1 and buttons[x][y]["text"] != flagGraphic:
                buttons[x][y]["text"] = mineGraphic
            
def gameTimer():
    global gameTime, firstMove, gameOver
    while True:
        gameTime += 1
        gameTimeLabel.set(gameTime)
        time.sleep(1)
        if firstMove or gameOver:
            break           

if __name__ == "__main__":
    if os.path.exists("config.ini"):
        loadConfig()
    else:
        saveConfig()

    gameTimeThread = threading.Timer(1.0, gameTimer)

    createMenu()
    prepareWindow()
    prepareGame()
    window.mainloop() 
