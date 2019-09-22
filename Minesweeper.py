import tkinter 
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialog

import configparser
import os
import random

window = tkinter.Tk()

window.title("Minesweeper")

#prepare default values

rowNum = 9
cols = 9
mines = 10

field = []
buttons = []

colour = ['#FFFFFF', '#0000FF', '#008200', '#FF0000', '#000084', '#840000', '#008284', '#840084', '#000000']

gameover = False
customsizes = []


def createMenu():
    menubar = tkinter.Menu(window)
    menusize = tkinter.Menu(window, tearoff=0)
    menusize.add_command(label="Beginner (9x9 with 10 mines)", command=lambda: setSize(9, 9, 10))
    menusize.add_command(label="Intermediate (16x16 with 40 mines)", command=lambda: setSize(16, 16, 40))
    menusize.add_command(label="Expert (16x30 with 99 mines)", command=lambda: setSize(16, 30, 99))
    menusize.add_separator()
    menusize.add_command(label="Custom", command=setCustomSize)
    if len(customsizes) > 0:
        menusize.add_separator()
        for x in range(0, len(customsizes)):
            menusize.add_command(label=str(customsizes[x][0])+"x"+str(customsizes[x][1])+" with "+str(customsizes[x][2])+" mines", command=lambda customsizes=customsizes: setSize(customsizes[x][0], customsizes[x][1], customsizes[x][2]))
    menubar.add_cascade(label="Options", menu=menusize)
    menubar.add_command(label="Exit", command=lambda: window.destroy())
    window.config(menu=menubar)

def setCustomSize():
    global customsizes
    rows = dialog.askinteger("Custom size", "Enter amount of rowNum")
    columns = dialog.askinteger("Custom size", "Enter amount of columns")
    mines = dialog.askinteger("Custom size", "Enter amount of mines")
    while mines > rows*columns:
        mines = dialog.askinteger("Custom size", "Maximum mines for this dimension is: " + str(rows*columns) + "\nEnter amount of mines")
    customsizes.insert(0, (rows,columns,mines))
    customsizes = customsizes[0:5]
    setSize(rows,columns,mines)
    createMenu()

def setSize(r,c,m):
    global rowNum, cols, mines
    rowNum = r
    cols = c
    mines = m
    saveConfig()
    restartGame()

def saveConfig():
    global rowNum, cols, mines
    #configuration
    config = configparser.ConfigParser()
    config.add_section("game")
    config.set("game", "rowNum", str(rowNum))
    config.set("game", "cols", str(cols))
    config.set("game", "mines", str(mines))
    config.add_section("sizes")
    config.set("sizes", "amount", str(min(5,len(customsizes))))
    for x in range(0,min(5,len(customsizes))):
        config.set("sizes", "row"+str(x), str(customsizes[x][0]))
        config.set("sizes", "cols"+str(x), str(customsizes[x][1]))
        config.set("sizes", "mines"+str(x), str(customsizes[x][2]))

    with open("config.ini", "w") as file:
        config.write(file)

def loadConfig():
    global rowNum, cols, mines, customsizes
    config = configparser.ConfigParser()
    config.read("config.ini")
    rowNum = config.getint("game", "rowNum")
    cols = config.getint("game", "cols")
    mines = config.getint("game", "mines")
    amountofsizes = config.getint("sizes", "amount")
    for x in range(0, amountofsizes):
        customsizes.append((config.getint("sizes", "row"+str(x)), config.getint("sizes", "cols"+str(x)), config.getint("sizes", "mines"+str(x))))

def prepareGame():
    global rowNum, cols, mines, field
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

def prepareWindow():
    global rowNum, cols, buttons
    tkinter.Button(window, text="Restart", command=restartGame).grid(row=0, column=0, columnspan=cols, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
    buttons = []
    for x in range(0, rowNum):
        buttons.append([])
        for y in range(0, cols):
            b = tkinter.Button(window, text=" ", width=2, command=lambda x=x,y=y: clickOn(x,y))
            b.bind("<Button-3>", lambda e, x=x, y=y:flagCell(x, y))
            b.grid(row=x+1, column=y, sticky=tkinter.N+tkinter.W+tkinter.S+tkinter.E)
            buttons[x].append(b)

def restartGame():
    global gameover
    gameover = False
    #destroy all - prevent memory leak
    for x in window.winfo_children():
        if type(x) != tkinter.Menu:
            x.destroy()
    prepareWindow()
    prepareGame()

def clickOn(x,y):
    global field, buttons, colour, gameover, rowNum, cols
    if gameover:
        return
    buttons[x][y]["text"] = str(field[x][y])
    if field[x][y] == -1:
        buttons[x][y]["text"] = "Ο"
        buttons[x][y].config(background='red', disabledforeground='black')
        gameover = True
        #tkinter.messagebox.showinfo("Game Over", "You have lost.")

        for _x in range(0, rowNum):     # Reveal Mines
            for _y in range(cols):
                #buttons[_x][_y]["state"] = "disabled"
                if field[_x][_y] == -1:
                    buttons[_x][_y]["text"] = "⊗"
    else:
        buttons[x][y].config(disabledforeground=colour[field[x][y]])
    if field[x][y] == 0:
        buttons[x][y]["text"] = " "
        #now repeat for all buttons nearby which are 0... kek
        cellCascade(x,y)
    buttons[x][y]['state'] = 'disabled'
    buttons[x][y].config(relief=tkinter.SUNKEN)
    checkWin()

def cellCascade(x,y):
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
            cellCascade(x-1,y-1)
        if x != 0:
            cellCascade(x-1,y)
        if x != 0 and y != cols-1:
            cellCascade(x-1,y+1)
        if y != 0:
            cellCascade(x,y-1)
        if y != cols-1:
            cellCascade(x,y+1)
        if x != rowNum-1 and y != 0:
            cellCascade(x+1,y-1)
        if x != rowNum-1:
            cellCascade(x+1,y)
        if x != rowNum-1 and y != cols-1:
            cellCascade(x+1,y+1)

def flagCell(x,y):
    global buttons
    if gameover:
        return
    if buttons[x][y]["text"] == "⁋":
        buttons[x][y]["text"] = " "
        buttons[x][y]["state"] = "normal"
    elif buttons[x][y]["text"] == " " and buttons[x][y]["state"] == "normal":
        buttons[x][y]["text"] = "⁋"
        buttons[x][y]["state"] = "disabled"

def checkWin():
    global buttons, field, rowNum, cols, gameover
    win = True
    for x in range(0, rowNum):
        for y in range(0, cols):
            if field[x][y] != -1 and buttons[x][y]["state"] == "normal":
                win = False
    if win:
        #tkinter.messagebox.showinfo("Gave Over", "You have won.")
        gameover = True
        revealMines(_x,_y,rowNum,cols)
        
def revealMines(x,y,rowNum,cols):
    for _x in range(0, rowNum):
            for _y in range(cols):
                if field[x][y] == -1:
                    buttons[x][y]["text"] = "⊗"


if os.path.exists("config.ini"):
    loadConfig()
else:
    saveConfig()

createMenu()

prepareWindow()
prepareGame()
window.mainloop()