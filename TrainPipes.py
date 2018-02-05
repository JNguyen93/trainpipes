# Train Labyrinth   
# By Justin Nguyen
# For use by Project Panic

import random, pygame, sys, math
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 800
WINDOWHEIGHT = 800
CELLSIZE = 40
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (237,  31,  36)
GREEN     = (106, 189,  69)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
GRAY      = (169, 168, 168)
BLUE      = (126, 149, 204)
ORANGE    = (246, 139,  31)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

bg = "TrainPipes.png"
bgimg = pygame.image.load(bg)
wList = None
cList = []
chainList = []
pointList = []
coordinates = []
activeChain = None

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, cList

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('TrainPipes')
    drawWalls()
    findPoints()
    updateScreen()
    #showStartScreen()
    while True:
        runGame()
        #showGameOverScreen()


def runGame():
    global activeChain, wList, cList, chainList, pointList

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
                
            elif event.type == MOUSEMOTION and pygame.mouse.get_pressed()[0] == 1:
                mousex, mousey = event.pos
                if activeChain is not None:
                    if activeChain.getPreviousLink() is not None:
                        if activeChain.getPreviousLink().checkCollision(event.pos) == 1:
                            lastLink = activeChain.getLinks().pop()
                            if lastLink is activeChain.getCurrentLink():
                                print('Removing Current Link...')
                                activeChain.setCurrentLink(activeChain.getPreviousLink())
                                index = activeChain.getLinks().index(activeChain.getCurrentLink())
                                if (index - 1) >= 0:
                                    activeChain.setPreviousLink(activeChain.getLinks()[index - 1])
                                updateScreen()
                                print('Complete')
                            else:
                                activeChain.getLinks().append(lastLink)
                    print(event.pos)
                    clear = True
                    for point in pointList:
                        if point.checkCollision(event.pos) == 1:
                            for chain in activeChain.getLinks():
                                if chain.checkCollision(event.pos) == 1:
                                    clear = False
                                    break
                            if clear is True:
                                activeChain.addLink(point.getPos())
                                updateScreen()
                    
            elif event.type == MOUSEBUTTONDOWN:		
                mousex, mousey = event.pos
                for circle in cList:
                    if circle.checkCollision(event.pos) is True:
                        for chain in chainList:
                            if chain.getStart() == circle or chain.getEnd() == circle:
                                activeChain = chain
                                print("Active Chain is set.")
                                activeChain.setActive(True)
                                activeChain.setCurrentLink(circle)
                                if chain.isLocked():
                                    chain.setLock(False)
                        if activeChain == None:
                            chain = Chain(circle)
                            print("Active Chain is set.")
                            activeChain = chain
                            activeChain.setActive(True)
                     
                mouseClicked = True
            elif event.type == MOUSEBUTTONUP:
                if activeChain is not None and activeChain.start.isPaired() is False:
                    activeChain.setActive(False)
                    activeChain = None
                    updateScreen()
##            elif event.type == KEYUP and event.key == K_j:
##                cheatFlag = True
##            elif event.type == KEYDOWN:
##                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
##                    direction = LEFT
##                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
##                    direction = RIGHT
##                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
##                    direction = UP
##                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
##                    direction = DOWN
##                elif event.key == K_ESCAPE:
##                    terminate()

##        # check if the worm has hit itself or the edge
##        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
##            return # game over
##        for wormBody in wormCoords[1:]:
##            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
##                return # game over
##
##        # check if worm has eaten an apple
##        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
##            # don't remove worm's tail segment
##            apple = getRandomLocation() # set a new apple somewhere
##        else:
##            del wormCoords[-1] # remove worm's tail segment
##
##        # move the worm by adding a segment in the direction it is moving
##        if direction == UP:
##            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
##        elif direction == DOWN:
##            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
##        elif direction == LEFT:
##            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
##        elif direction == RIGHT:
##            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
##        wormCoords.insert(0, newHead)
        #DISPLAYSURF.blit(bgimg, (0, 0))
        #drawCircles()
        #drawGrid()
        #drawWorm(wormCoords)
        #drawApple(apple)
        #drawScore(len(wormCoords) - 3)
        #pygame.display.update()
        updateScreen()
        FPSCLOCK.tick(FPS)

def drawChains():
    global chainList

    if activeChain is not None:
        for link in activeChain.getLinks():
            pygame.draw.circle(DISPLAYSURF, link.getColor(), link.getPos(), int(link.getRadius()), 0)
        
    for chain in chainList:
        if chain.isLocked():
            for link in chains.getLinks():
                pygame.draw.circle(DISPLAYSURF, link.getColor(), link.getPos(), int(link.getRadius()), 0)

def updateScreen():
    DISPLAYSURF.blit(bgimg, (0, 0))
    drawCircles()
    #drawGrid()
    drawPoints()
    drawChains()
    pygame.display.update()
    
def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        #wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        #pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        circ = Circle(DARKGREEN, (int((x + CELLSIZE/2)), int((y + CELLSIZE/2))), (CELLSIZE/2));
        pygame.draw.circle(DISPLAYSURF, circ.getColor(), circ.getPos(), int(circ.getRadius()), 0)
        #wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        #pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)

def drawGrid():    
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

def findPoints():
    global coordinates
    xIntersects = []
    yIntersects = []
    
    for x in range(int((CELLSIZE + (CELLSIZE / 2))), int((WINDOWWIDTH - ((CELLSIZE / 2)))), int((CELLSIZE / 2))):
        xIntersects.append(x)
    for y in range(int((CELLSIZE + (CELLSIZE / 2))), int((WINDOWHEIGHT - ((CELLSIZE / 2)))), int((CELLSIZE / 2))):
        yIntersects.append(y)
    for x in xIntersects:
        for y in yIntersects:
            coordinates.append((x, y))
            
def drawPoints():
    global coordinates
    
    for coords in coordinates:
        valid = True
        for wall in wList:
            if wall.checkCollision(coords) == 1:
                valid = False
                break
        if valid is True:
            for circle in cList:
                if circle.checkCollision(coords) == 1:
                    valid = False
                    break
        if valid is True:
            point = Circle(DARKGRAY, coords, 5)
            pygame.draw.circle(DISPLAYSURF, point.getColor(), point.getPos(), point.getRadius(), 0)
            pointList.append(point)
                
def checkWin():
    for c in cList:
        if c.isPaired() is False:
            return False
        else:
            return True
        
def drawCircles():
    global cList

    rad = 16
    blue0 = Circle(BLUE, (int((3.5 * CELLSIZE)), int((1.5 * CELLSIZE))), rad)
    blue1 = Circle(BLUE, (int((15 * CELLSIZE)), int((13.5 * CELLSIZE))), rad)
    blue0.setPair(blue1)
    blue1.setPair(blue0)

    green0 = Circle(GREEN, (int((6.5 * CELLSIZE)), int((5 * CELLSIZE))), rad)
    green1 = Circle(GREEN, (int((10 * CELLSIZE)), int((18.5 * CELLSIZE))), rad)
    green0.setPair(green1)
    green1.setPair(green0)

    red0 = Circle(RED, (int((13 * CELLSIZE)), int((5 * CELLSIZE))), rad)
    red1 = Circle(RED, (int((5 * CELLSIZE)), int((15 * CELLSIZE))), rad)
    red0.setPair(red1)
    red1.setPair(red0)

    orange0 = Circle(ORANGE, (int((12 * CELLSIZE)), int((9 * CELLSIZE))), rad)
    orange1 = Circle(ORANGE, (int((18.5 * CELLSIZE)), int((5 * CELLSIZE))), rad)
    orange0.setPair(orange1)
    orange1.setPair(orange0)

    cList = [blue0, blue1, green0, green1, red0, red1, orange0, orange1]
    
    for c in cList:
        hitbox = pygame.draw.circle(DISPLAYSURF, c.getColor(), c.getPos(), int(c.getRadius()), 0)
        c.setHitbox(hitbox)
        #pygame.draw.rect(DISPLAYSURF, GREEN, c.getHitbox())

def drawWalls():
    global wList

    #Outer Wall
    Rect0 = Rect(int((0 * CELLSIZE)), int((0 * CELLSIZE)), int((20 * CELLSIZE)), int((1 * CELLSIZE)))
    Rect1 = Rect(int((0 * CELLSIZE)), int((1 * CELLSIZE)), int((1 * CELLSIZE)), int((19 * CELLSIZE)))
    Rect2 = Rect(int((1 * CELLSIZE)), int((19 * CELLSIZE)), int((19 * CELLSIZE)), int((1 * CELLSIZE)))
    Rect3 = Rect(int((19 * CELLSIZE)), int((1* CELLSIZE)), int((1 * CELLSIZE)), int((18 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3]

    wall0 = Wall(rList)

    #Top Right Side Quadrilateral
    Rect0 = Rect(int((5 * CELLSIZE)), int((2 * CELLSIZE)), int((4.5 * CELLSIZE)), int((2.5 * CELLSIZE)))
    Rect1 = Rect(int((3 * CELLSIZE)), int((2 * CELLSIZE)), int((2 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((3.5 * CELLSIZE)), int((2.5 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((4 * CELLSIZE)), int((3 * CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect4 = Rect(int((4.5 * CELLSIZE)), int((3.5* CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3, Rect4]

    wall1 = Wall(rList)

    Rect0 = Rect(int((10.5 * CELLSIZE)), int((2 * CELLSIZE)), int((4.5 * CELLSIZE)), int((2.5 * CELLSIZE)))
    Rect1 = Rect(int((15 * CELLSIZE)), int((2 * CELLSIZE)), int((0.5 * CELLSIZE)), int((2 * CELLSIZE)))
    Rect2 = Rect(int((15.5 * CELLSIZE)), int((2 * CELLSIZE)), int((0.5 * CELLSIZE)), int((1.5 * CELLSIZE)))
    Rect3 = Rect(int((16 * CELLSIZE)), int((2 * CELLSIZE)), int((0.5 * CELLSIZE)), int((1 * CELLSIZE)))
    Rect4 = Rect(int((16.5 * CELLSIZE)), int((2 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3, Rect4]

    wall2 = Wall(rList)

    Rect0 = Rect(int((15.5 * CELLSIZE)), int((5 * CELLSIZE)), int((2.5 * CELLSIZE)), int((4.5 * CELLSIZE)))
    Rect1 = Rect(int((16 * CELLSIZE)), int((4.5 * CELLSIZE)), int((2 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((16.5 * CELLSIZE)), int((4 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((17 * CELLSIZE)), int((3.5* CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect4 = Rect(int((17.5 * CELLSIZE)), int((3 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3, Rect4]

    wall3 = Wall(rList)

    Rect0 = Rect(int((15.5 * CELLSIZE)), int((10.5 * CELLSIZE)), int((2.5 * CELLSIZE)), int((4.5 * CELLSIZE)))
    Rect1 = Rect(int((16 * CELLSIZE)), int((15 * CELLSIZE)), int((2 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((16.5 * CELLSIZE)), int((15.5 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((17 * CELLSIZE)), int((16 * CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect4 = Rect(int((17.5 * CELLSIZE)), int((16.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3, Rect4]

    wall4 = Wall(rList)

    Rect0 = Rect(int((10.5 * CELLSIZE)), int((15.5 * CELLSIZE)), int((4.5 * CELLSIZE)), int((2.5 * CELLSIZE)))
    Rect1 = Rect(int((15 * CELLSIZE)), int((16 * CELLSIZE)), int((0.5 * CELLSIZE)), int((2 * CELLSIZE)))
    Rect2 = Rect(int((15.5 * CELLSIZE)), int((16.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((1.5 * CELLSIZE)))
    Rect3 = Rect(int((16 * CELLSIZE)), int((17 * CELLSIZE)), int((0.5 * CELLSIZE)), int((1 * CELLSIZE)))
    Rect4 = Rect(int((16.5 * CELLSIZE)), int((17.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3, Rect4]

    wall5 = Wall(rList)

    Rect0 = Rect(int((5 * CELLSIZE)), int((15.5 * CELLSIZE)), int((4.5 * CELLSIZE)), int((2.5 * CELLSIZE)))
    Rect1 = Rect(int((3 * CELLSIZE)), int((17.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((3.5 * CELLSIZE)), int((17 * CELLSIZE)), int((0.5 * CELLSIZE)), int((1 * CELLSIZE)))
    Rect3 = Rect(int((4 * CELLSIZE)), int((16.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((1.5 * CELLSIZE)))
    Rect4 = Rect(int((4.5 * CELLSIZE)), int((16 * CELLSIZE)), int((0.5 * CELLSIZE)), int((2 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3, Rect4]

    wall6 = Wall(rList)
    
    Rect0 = Rect(int((2 * CELLSIZE)), int((10.5 * CELLSIZE)), int((2.5 * CELLSIZE)), int((4.5 * CELLSIZE)))
    Rect1 = Rect(int((2 * CELLSIZE)), int((15 * CELLSIZE)), int((2 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((2 * CELLSIZE)), int((15.5 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((2 * CELLSIZE)), int((16 * CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect4 = Rect(int((2 * CELLSIZE)), int((16.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3, Rect4]

    wall7 = Wall(rList)

    #Top Left Side Quadrilateral
    Rect0 = Rect(int((2 * CELLSIZE)), int((5 * CELLSIZE)), int((2.5 * CELLSIZE)), int((4.5 * CELLSIZE)))
    Rect1 = Rect(int((2 * CELLSIZE)), int((4.5 * CELLSIZE)), int((2 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((2 * CELLSIZE)), int((4 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((2 * CELLSIZE)), int((3.5 * CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect4 = Rect(int((2 * CELLSIZE)), int((3 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3, Rect4]

    wall8 = Wall(rList)

    #Inner Walls

    Rect0 = Rect(int((8 * CELLSIZE)), int((5.5 * CELLSIZE)), int((1.5 * CELLSIZE)), int((2 * CELLSIZE)))
    Rect1 = Rect(int((6.5 * CELLSIZE)), int((5.5 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((7 * CELLSIZE)), int((6 * CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((7.5 * CELLSIZE)), int((6.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3]

    wall9 = Wall(rList)

    Rect0 = Rect(int((10.5 * CELLSIZE)), int((5.5 * CELLSIZE)), int((1.5 * CELLSIZE)), int((2 * CELLSIZE)))
    Rect1 = Rect(int((12 * CELLSIZE)), int((5.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((1.5 * CELLSIZE)))
    Rect2 = Rect(int((12.5 * CELLSIZE)), int((5.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((1 * CELLSIZE)))
    Rect3 = Rect(int((13 * CELLSIZE)), int((5.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3]

    wall10 = Wall(rList)

    Rect0 = Rect(int((12.5 * CELLSIZE)), int((8 * CELLSIZE)), int((2 * CELLSIZE)), int((1.5 * CELLSIZE)))
    Rect1 = Rect(int((13 * CELLSIZE)), int((7.5 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((13.5 * CELLSIZE)), int((7 * CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((14 * CELLSIZE)), int((6.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3]

    wall11 = Wall(rList)

    Rect0 = Rect(int((12.5 * CELLSIZE)), int((10.5 * CELLSIZE)), int((2 * CELLSIZE)), int((2 * CELLSIZE)))
    Rect1 = Rect(int((10.5 * CELLSIZE)), int((12.5 * CELLSIZE)), int((4 * CELLSIZE)), int((2 * CELLSIZE)))
    rList = [Rect0, Rect1]

    wall12 = Wall(rList)

    Rect0 = Rect(int((8 * CELLSIZE)), int((12.5 * CELLSIZE)), int((1.5 * CELLSIZE)), int((2 * CELLSIZE)))
    Rect1 = Rect(int((6.5 * CELLSIZE)), int((14 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((7 * CELLSIZE)), int((13.5 * CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((7.5 * CELLSIZE)), int((13 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3]
    
    wall13 = Wall(rList)

    Rect0 = Rect(int((5.5 * CELLSIZE)), int((10.5 * CELLSIZE)), int((2 * CELLSIZE)), int((1.5 * CELLSIZE)))
    Rect1 = Rect(int((5.5 * CELLSIZE)), int((12 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((5.5 * CELLSIZE)), int((12.5 * CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((5.5 * CELLSIZE)), int((13 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3]

    wall14 = Wall(rList)
    
    Rect0 = Rect(int((5.5 * CELLSIZE)), int((8 * CELLSIZE)), int((2 * CELLSIZE)), int((1.5 * CELLSIZE)))
    Rect1 = Rect(int((5.5 * CELLSIZE)), int((6.5 * CELLSIZE)), int((0.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect2 = Rect(int((5.5 * CELLSIZE)), int((7 * CELLSIZE)), int((1 * CELLSIZE)), int((0.5 * CELLSIZE)))
    Rect3 = Rect(int((5.5 * CELLSIZE)), int((7.5 * CELLSIZE)), int((1.5 * CELLSIZE)), int((0.5 * CELLSIZE)))
    rList = [Rect0, Rect1, Rect2, Rect3]
    
    wall15 = Wall(rList)

    #Inner Inner Walls
    Rect0 = Rect(int((8.5 * CELLSIZE)), int((8.5 * CELLSIZE)), int((1 * CELLSIZE)), int((3 * CELLSIZE)))
    rList = [Rect0]

    wall16 = Wall(rList)

    Rect0 = Rect(int((10.5 * CELLSIZE)), int((8.5 * CELLSIZE)), int((1 * CELLSIZE)), int((1 * CELLSIZE)))
    rList = [Rect0]

    wall17 = Wall(rList)

    Rect0 = Rect(int((10.5 * CELLSIZE)), int((10.5 * CELLSIZE)), int((1 * CELLSIZE)), int((1 * CELLSIZE)))
    rList = [Rect0]

    wall18 = Wall(rList)

    wList = [wall0, wall1, wall2, wall3, wall4, wall5, wall6, wall7, wall8, wall9, wall10, wall11, wall12, wall13, wall14, wall15, wall16, wall17, wall18]

    #for wall in wList:
    #    wall.drawWalls()
    
class Circle:
    
    def __init__(self, color, pos, radius):
        self.pos = pos
        self.radius = radius
        self.color = color
        self.connected = False
        self.hitbox = None
        self.pair = None
        self.paired = False

    def setPaired(self, boolean):
        self.paired = boolean

    def isPaired(self):
        return self.paired
    
    def setPair(self, circle):
        self.pair = circle

    def getPair(self):
        return self.pair
    
    def getPos(self):
        return self.pos

    def getX(self):
        return self.pos[0]

    def getY(self):
        return self.pos[1]

    def getRadius(self):
        return self.radius

    def getColor(self):
        return self.color

    def setHitbox(self, rect):
        self.hitbox = rect

    def getHitbox(self):
        return self.hitbox
        
    def checkMatch(self, circle):
        if self.getPair() == circle.getPair():
            self.setPaired(True)
            circle.setPaired(True)
            return True
        else:
            return False
        
    def checkCollision(self, pos):
        x = pos[0]
        y = pos[1]

        sqx = (x - self.pos[0])**2
        sqy = (y - self.pos[1])**2

        if math.sqrt(sqx + sqy) < self.radius:
            return True
        else:
            return False

class Wall:
    
    def __init__(self, rList):
        self.rectList = rList

    def getRectList(self):
        return self.rectList

    def drawWalls(self):
        for rect in self.rectList:
            pygame.draw.rect(DISPLAYSURF, RED, rect)

    def checkCollision(self, pos):
        for rect in self.rectList:
            if rect.collidepoint(pos) == 1:
                return True
        return False

class Chain:

    def __init__(self, start):
        self.start = start
        self.locked = False
        self.end = None
        self.links = []
        self.currentLink = start
        self.active = False
        self.previousLink = None

    def setActive(self, boolean):
        self.active = boolean

    def isActive(self):
        return self.active
    
    def setLock(self, boolean):
        self.locked = boolean

    def isLocked(self):
        return self.locked

    def getLinks(self):
        return self.links

    def getStart(self):
        return self.start

    def setEnd(self, circle):
        self.end = circle

    def getEnd(self):
        return self.end

    def setCurrentLink(self, circle):
        self.currentLink = circle

    def getCurrentLink(self):
        return self.currentLink

    def setPreviousLink(self, circle):
        self.previousLink = circle

    def getPreviousLink(self):
        return self.previousLink
    
    def addLink(self, pos):
        print("Adding Link..")
        link = Circle(self.start.getColor(), pos, self.start.getRadius())
        self.links.append(link)
        pygame.draw.circle(DISPLAYSURF, link.getColor(), link.getPos(), int(link.getRadius()), 0)
    
if __name__ == '__main__':
    main()
