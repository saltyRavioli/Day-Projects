import pygame
import random
import sys
from pygame.locals import *

# 5x10 grid
# control a 1x2 rectangle that swaps its two rectangles on command
# create lines

class Tile(): # 0 means empty tile
    def __init__(self, one, two):
        self.corner1 = one
        self.corner2 = two

pygame.init()
screen = pygame.display.set_mode((325, 450))
bg_colour = [0, 0, 0]
grid_colour = [255, 255, 255]
top_left = [100, 100]

grid = []
for i in range(0, 10):
    grid.append([])
    for j in range(0, 5):
        grid[i].append(Tile(0,0))

player = [8, 2]
tick = 0
spawnFrequency = 7000
on = True

def drawPlayer():
    # translucent:
    # thanks stack overflow
    # https://stackoverflow.com/questions/6339057/draw-transparent-rectangles-and-polygons-in-pygame
    # s = pygame.Surface((25,50))                                                     # the size of your rect
    # s.set_alpha(50)                                                                 # alpha level
    # s.fill((150, 150, 150))                                                         # this fills the entire surface
    # screen.blit(s, (top_left[1] + player[1]*25, top_left[0] + player[0]*25))        # top-left coordinates
    
    # (screen, [RGB], (top left x, top left y, width, height), border width)
    pygame.draw.rect(screen, [255, 0, 0], (top_left[1] + 25*player[1], top_left[0] + 25*player[0], 25, 50), 3) 

def drawLine(i, j, corner):
    # corner labels:
    #   1 3
    #   2 4
    start_point = [top_left[1]+25*j, top_left[1]+25*i] # start point for corner = 1
    if (corner == 2):
        start_point[1]+=25
    elif (corner == 3):
        start_point[0]+=25
    elif (corner == 4):
        start_point[0]+=25
        start_point[1]+=25
    pygame.draw.line(screen, grid_colour, start_point, (top_left[1]+25*j+12, top_left[1]+25*i+12))

def drawGrid():
    for i in range(10):
        j=0
        # (screen, [RGB], (top left x, top left y, width, height), border width)
        # wait hold on why is x and y flipped
        pygame.draw.rect(screen, bg_colour, (top_left[1] + 25*j, top_left[0] + 25*i, 25, 25), 0) 
        pygame.draw.rect(screen, grid_colour, (top_left[1] + 25*j, top_left[0] + 25*i, 25, 25), 1) 
        if (grid[i][j].corner1 != 0): # non-empty tile
            drawLine(i, j, grid[i][j].corner1)
            drawLine(i, j, grid[i][j].corner2)
    for i in range(10):
        for j in range(5):
            # (screen, [RGB], (top left x, top left y, width, height), border width)
            # wait hold on why is x and y flipped
            pygame.draw.rect(screen, bg_colour, (top_left[1] + 25*j, top_left[0] + 25*i, 25, 25), 0) 
            pygame.draw.rect(screen, grid_colour, (top_left[1] + 25*j, top_left[0] + 25*i, 25, 25), 1) 
            if (grid[i][j].corner1 != 0): # non-empty tile
                drawLine(i, j, grid[i][j].corner1)
                drawLine(i, j, grid[i][j].corner2)

def controls():
    # TODO: holding a button down moves cursor
        # don't wanna do rn bc there needs to be "cooldown" or else the cursor would move too fast
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if ((event.key == K_DOWN or event.key == K_s) and player[0] < 8):
                player[0]+=1
            if ((event.key == K_UP or event.key == K_w) and player[0] > 0):
                player[0]-=1
            if ((event.key == K_RIGHT or event.key == K_d) and player[1] < 4):
                player[1]+=1
            if ((event.key == K_LEFT or event.key == K_a) and player[1] > 0):
                player[1]-=1
            if (event.key == K_SPACE): # swap cursor tiles
                temp = grid[player[0]][player[1]]
                grid[player[0]][player[1]] = grid[player[0]+1][player[1]]
                grid[player[0]+1][player[1]] = temp
                checkForClear() # i will no longer check every frame, instead only when game state changes
                    # surely this will lead to less jank
                    # definitely
                    # there's no way this can backfire

        # Check for QUIT event
        elif event.type == QUIT:
            on = False # for some reason this does nothing, so ill just force close here
            pygame.quit()
            sys.exit()



def spawning():
    if (tick%spawnFrequency != 0):
        return
    
    chance = random.randint(1, 5)

    # check defeat (i think gunpey works like tetris for defeat conditions? ie if it goes past the top)

    # move every row up
    for i in range(9):
        for j in range(5):
            grid[i][j] = grid[i+1][j]
    # move player up (because it's jank when the board moves up but the player doesn't)
    player[0]-=1

    # debug
    # grid[9][0] = Tile(2, 3)
    # grid[9][1] = Tile(1, 4)
    # grid[9][2] = Tile(2, 3)
    # grid[9][3] = Tile(1, 3)
    # grid[9][4] = Tile(1, 4)

    # make new row
    for j in range(5):
        rng = random.randint(1, 5)
        if (rng<=chance):
            corner1 = random.randint(1,4)
            corner2 = random.randint(1,4)
            if (corner1 == corner2 or rng > 2):
                # prevent corners from being the same
                # also, sometimes decide to give a line that guarantees crossing from left to right
                    # because rng keeps giving me 1-2 and 3-4 lines
                corner1 = random.randint(1, 2)
                corner2 = random.randint(3, 4)
            grid[9][j] = Tile(corner1, corner2)
        else:
            grid[9][j] = Tile(0, 0)
    
    checkForClear() # i will no longer check every frame, instead only when game state changes




def hasCorner(i, j, corner):
    if (grid[i][j].corner1 == corner or grid[i][j].corner2 == corner):
        return True
    return False
def checkTileConnectivity(connectivityArray, i, j):
    # corner labels:
    #   1 3
    #   2 4

    # in retrospect, it seems like sorting all this by the current tile's corners would have been neater

    # check tiles above
    if (i>0):
        # top left
        if (hasCorner(i-1, j-1, 4) and hasCorner(i, j, 1) and connectivityArray[i-1][j-1]):
            connectivityArray[i][j] = True
        # top mid
        elif ((hasCorner(i-1, j, 2) and hasCorner(i, j, 1)) or 
                (hasCorner(i-1, j, 4) and hasCorner(i, j, 3)) and 
                connectivityArray[i-1][j]):
            connectivityArray[i][j] = True
        # top right
        elif (j<4 and hasCorner(i-1, j+1, 2) and hasCorner(i, j, 3) and connectivityArray[i-1][j+1]):
            connectivityArray[i][j] = True
    # check tiles below
    if (i<9):
        # bot left
        if (hasCorner(i+1, j-1, 3) and hasCorner(i, j, 2) and connectivityArray[i+1][j-1]):
            connectivityArray[i][j] = True
        # bot mid
        elif ((hasCorner(i+1, j, 1) and hasCorner(i, j, 2)) or 
                (hasCorner(i+1, j, 3) and hasCorner(i, j, 4)) and 
                connectivityArray[i-1][j]):
            connectivityArray[i][j] = True
        # bot right
        elif (j<4 and hasCorner(i+1, j+1, 3) and hasCorner(i, j, 2) and connectivityArray[i+1][j+1]):
            connectivityArray[i][j] = True
    # check tiles on same row
    # left
    if (((hasCorner(i, j-1, 3) and hasCorner(i, j, 1)) or 
        (hasCorner(i, j-1, 4) and hasCorner(i, j, 2))) and 
        connectivityArray[i][j-1]):
        connectivityArray[i][j] = True
    # right
    if (j<4 and ((hasCorner(i, j+1, 1) and hasCorner(i, j, 3)) or 
        (hasCorner(i, j+1, 2) and hasCorner(i, j, 4))) and 
        connectivityArray[i][j+1]):
        connectivityArray[i][j] = True
    
    return connectivityArray


def checkForClear():
    connectivity = []
    for i in range(0, 10):
        connectivity.append([])
        for j in range(0, 5):
            connectivity[i].append(False)
    
    # is left column connected to left wall
    for i in range(10):
        if (hasCorner(i, 0, 1) or hasCorner(i, 0, 2)):
            connectivity[i][0] = True

    # check middle columns
    for j in range(1, 4):
        for i in range(10):
            connectivity = checkTileConnectivity(connectivity, i, j)

    # is right column connected to right wall AND a tile to its left has connectivity = 
        # edit: since we are checking backwards as well, we no longer need to check for connectivity to right wall
    for i in range(10):
        # if (hasCorner(i, 4, 3) or hasCorner(i, 4, 4)): # is connected to right wall
        connectivity = checkTileConnectivity(connectivity, i, 4) # tile to its left has connectivity = True
    
    # if this algorithm doesn't work do a verification check going in the opposite direction
        # oh great it doesn't work
        # actually i think it does but it basically always deletes any left wall touching nodes because they're always true
            # so yeah doing the same thing again but in the opposite direction would probably solve the issues
                # wait wtf?????? now random lines will just arbritrarily disappear
                    # and the board occasionally just
                    # completely changes?????
                    # huh what why
    # ok idk what i did but most of the issues seem fixed
        # but for some reason if the last line moved to form a valid connection is on either the leftmost or rightmost column
            # only either the leftmost or rightmost line will disappear (that line is not necessarily the line that was moved)
                # i have no clue why this happens
                # wait maybe it's not related to this
                # maybe it's related to different tiles being the same object
    # TODO: debug this, it's probably an error in checkTileConnectivity()
    checkForClear2(connectivity)


def checkForClear2(connectivity):
    trueConnectivity = []
    for i in range(0, 10):
        trueConnectivity.append([])
        for j in range(0, 5):
            trueConnectivity[i].append(False)

    # is right column connected to right wall
    for i in range(9, -1, -1):
        if ((hasCorner(i, 4, 3) or hasCorner(i, 4, 4)) and connectivity[i][4]):
            trueConnectivity[i][4] = True

    # check middle columns
    for j in range(3, 0, -1):
        for i in range(9, -1, -1):
            trueConnectivity = checkTileConnectivity(trueConnectivity, i, j)
            trueConnectivity[i][j] = trueConnectivity[i][j] and connectivity[i][j]

    # is left column connected to left wall AND a tile to its right has connectivity = True
        # edit: no need to check for left wall connectivity
    for i in range(9, -1, -1):
        # if (hasCorner(i, 0, 1) or hasCorner(i, 0, 2)): # is connected to left wall
        trueConnectivity = checkTileConnectivity(trueConnectivity, i, 0) # tile to its right has connectivity = True
        trueConnectivity[i][0] = trueConnectivity[i][0] and connectivity[i][0]
                
    # TODO: delay deletion by like 2 seconds so the player can do cool combos like in gunpey psp
    # delete all connectivity = True tiles:
    for i in range(0, 10):
        for j in range(0, 5):
            if (trueConnectivity[i][j]):
                grid[i][j] = Tile(0,0)

# https://www.geeksforgeeks.org/introduction-to-pygame/
while on:
    # what is this program structure
    controls()
    spawning()
    drawGrid()
    drawPlayer()
    tick+=1
    pygame.display.flip()

pygame.quit()
sys.exit()