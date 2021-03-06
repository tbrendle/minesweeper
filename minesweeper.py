# -*- coding: cp1252 -*-
# INTIALISATION
import pygame
import math
import sys
import random
import datetime
from pygame.locals import *
pygame.font.init()
IMG_BOMB = pygame.image.load('pictures/bomb.png')
IMG_IDLE = pygame.image.load('pictures/question.png')
IMG_MARK = pygame.image.load('pictures/bombMark.png')
IMG_BOX = pygame.image.load('pictures/box.png')
TUTORIAL = pygame.image.load('pictures/tutorial.png')
BACKGROUND = pygame.image.load('pictures/background.jpg')
XBACK, YBACK = BACKGROUND.get_rect().size
LEFT = 1  # Mouse
RIGHT = 3  # Mouse
HEIGHT = 720
WIDTH = 1080
NO_CHANGE = -2
GAMEOVER = -1
WIN = 0
KEEP_GOING = 1
EXIT = -3
font = pygame.font.Font(None, 36)
NUMBERS = [font.render(str(i), 1, (10 + 25 * i, 10, 250 - 25 * i))
           for i in xrange(1, 9)]
LEVELS = {"Easy": (9, 9, 10), "Medium": (16, 16, 40), "Hard": (30, 16, 99)}
# CLASS DECLARATION


class ClassicBox(pygame.sprite.Sprite):

    def __init__(self, position, height, width):
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        self.height = height
        self.width = width
        self.image = IMG_BOX
        self.image = pygame.transform.scale(self.image, (height, width))
        self.rect = self.image.get_rect()
        self.rect.center = self.position


class DynamicBox(pygame.sprite.Sprite):

    def __init__(self, position, height, width, isBomb):
        pygame.sprite.Sprite.__init__(self)
        self.height = height
        self.width = width
        self.position = position
        self.isBomb = isBomb
        self.revealed = False
        self.marked = False
        self.image = IMG_IDLE
        self.resizeIcon()
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def mark(self):
        if not self.revealed:
            if self.marked:
                self.image = IMG_IDLE
                self.resizeIcon()
            else:
                self.image = IMG_MARK
                self.resizeIcon()
            self.marked = not self.marked

    def reveal(self):
        if not self.revealed:
            self.revealed = True
            if self.isBomb:
                self.image = IMG_BOMB
                self.resizeIcon()
            else:
                self.image = IMG_BOX
                self.resize()
            return True
        else:
            return False

    def resize(self):
        self.image = pygame.transform.scale(
            self.image, (self.height, self.width))
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def resizeIcon(self):
        self.image = pygame.transform.scale(
            self.image, (int(self.height * 0.85), int(self.width * 0.85)))
        self.rect = self.image.get_rect()
        self.rect.center = self.position


class ValueError(Exception):

    def __init__(self, r, c, b):
        self.r = r
        self.c = c
        self.b = b

    def __str__(self):
        return "Value Error : %d > %d" % (r * c, b)


class Grid():

    def __init__(self, r, c, b):
        if b > r * c:
            raise ValueError(r, c, b)
        else:
            self.r = r
            self.c = c
            self.b = b
            self.sizeOfBox = int(min(HEIGHT * 0.8 / c, WIDTH * 0.8 / r))
            self.yMargin = (HEIGHT - self.sizeOfBox * c) / 2
            self.xMargin = (WIDTH - self.sizeOfBox * r) / 2
            self.values = range(0, r * c)
            self.bombValues = random.sample(self.values, b)
            self.emptyValues = r * c - b
            listOfDynamicBoxes = []
            listOfNormalBoxes = []
            for i in self.values:
                (xPos, yPos) = self.convertIntToXY(i)
                newBox = DynamicBox(
                    (xPos, yPos), self.sizeOfBox, self.sizeOfBox, (i in self.bombValues))
                listOfDynamicBoxes.append(newBox)
                classBox = ClassicBox(
                    (xPos, yPos), self.sizeOfBox, self.sizeOfBox)
                listOfNormalBoxes.append(classBox)
            self.dynamicBoxes = listOfDynamicBoxes
            self.normalBoxes = listOfNormalBoxes
            self.revealedBoxes = {}

    def draw(self, screen):
        boxes = pygame.sprite.Group(self.normalBoxes)
        boxes.draw(screen)
        boxes = pygame.sprite.Group(self.dynamicBoxes)
        boxes.draw(screen)
        for k in self.revealedBoxes.keys():
            if not self.revealedBoxes[k] == 0:
                numberImg = NUMBERS[self.revealedBoxes[k] - 1]
                sx, sy = NUMBERS[self.revealedBoxes[k] - 1].get_rect().size
                x, y = self.convertIntToXY(k)
                screen.blit(
                    NUMBERS[self.revealedBoxes[k] - 1], (x - sx / 2, y - sy / 2))

    def convertIntToXY(self, i):
        x = self.xMargin + self.sizeOfBox * (i // self.c) + self.sizeOfBox / 2
        y = self.yMargin + self.sizeOfBox * (i % self.c) + self.sizeOfBox / 2
        return (x, y)

    def convertXYtoInt(self, x, y):
        i = (x - self.xMargin) / self.sizeOfBox
        j = (y - self.yMargin) / self.sizeOfBox
        if(i < 0 or j < 0 or i >= self.r or j >= self.c):
            return -1
        return i * self.c + j

    def exploreAround(self, i):
        l = [i]
        keepGoing = True
        while l != []:
            i = l.pop()
            if(self.dynamicBoxes[i].reveal()):
                if(i % self.c == self.c - 1):
                    arround = [
                        i + self.c, i + self.c - 1, i - self.c - 1, i - self.c, i - 1]
                elif(i % self.c == 0):
                    arround = [
                        i + self.c, i + self.c + 1, i - self.c, i - self.c + 1, i + 1]
                else:
                    arround = [i + self.c, i + self.c + 1, i + self.c - 1,
                               i - self.c - 1, i - self.c, i - self.c + 1, i - 1, i + 1]
                trueArround = [
                    j for j in arround if j >= 0 and j < self.r * self.c]
                count = 0
                for e in trueArround:
                    if self.dynamicBoxes[e].isBomb:
                        count += 1
                self.revealedBoxes[i] = count
                self.emptyValues -= 1
                if count == 0:
                    for e in trueArround:
                        if not e in self.revealedBoxes:
                            self.revealedBoxes[e] = 0
                            l.append(e)

    def handleClick(self, event):
        (x, y) = event.pos
        i = self.convertXYtoInt(x, y)
        if(i != -1 and i < self.r * self.c):
            if event.button == LEFT:
                if(self.dynamicBoxes[i].isBomb):
                    self.dynamicBoxes[i].reveal()
                    return GAMEOVER
                else:
                    self.exploreAround(i)
                    return self.emptyValues
            elif event.button == RIGHT:
                self.dynamicBoxes[i].mark()
                return self.emptyValues
        return NO_CHANGE


class Label():

    def __init__(self, text, pos, color):
        self.pos = pos
        self.color = color
        self.text = text
        self.font = font.render(self.text, 1, (10, 10, 10))

    def setText(self, newText):
        self.text = newText
        self.font = font.render(self.text, 1, (10, 10, 10))

    def draw(self, screen):
        (x, y, width, height) = self.pos
        textW, textH = self.font.get_rect().size
        pygame.draw.rect(
            screen, self.color, (x - width / 2, y - height / 2, width, height))
        screen.blit(self.font, (x - textW / 2, y - textH / 2))


class Button(Label):

    def __init__(self, text, pos, color, value):
        Label.__init__(self, text, pos, color)
        self.value = value

    def handleClick(self, xPos, yPos):
        (x, y, width, height) = self.pos
        if xPos > x - width / 2 and xPos < x + width / 2 and yPos > y - height / 2 and yPos < y + height / 2:
            return True
        else:
            return False


class Menu():

    def __init__(self, screen):
        self.screen = screen
        height = 2 * (2 * HEIGHT / 3 / 13)
        width = 300
        tutorial = TUTORIAL
        x, y = tutorial.get_rect().size
        self.tutorial = pygame.transform.scale(
            tutorial, ((x * HEIGHT / 3) / y, HEIGHT / 3))
        x, y = self.tutorial.get_rect().size
        self.label = Label(
            'Choose a level', (WIDTH / 2, HEIGHT - y - 11 * height / 2, width, height), (0, 0, 255))
        self.buttons = [
            Button('Easy', (WIDTH / 2, HEIGHT - y - 4 * height,
                            width, height), (0, 255, 0), 'Easy'),
            Button(
                'Hard', (WIDTH / 2, HEIGHT - y - height, width, height), (255, 0, 0), 'Hard'),
            Button('Medium', (WIDTH / 2, HEIGHT - y - 5 * height / 2,
                              width, height), (155, 155, 0), 'Medium'),
        ]

    def draw(self):
        screen.fill((255, 255, 255))
        screen.blit(BACKGROUND, [(WIDTH - XBACK) / 2, (HEIGHT - YBACK) / 2])
        x, y = self.tutorial.get_rect().size
        self.screen.blit(self.tutorial, (WIDTH / 2 - x / 2, HEIGHT - y))
        self.label.draw(self.screen)
        for b in self.buttons:
            b.draw(self.screen)

    def handleClick(self, pos):
        (xPos, yPos) = pos
        for b in self.buttons:
            if b.handleClick(xPos, yPos):
                self.level = b.value
                return WIN
        return KEEP_GOING

    def run(self):
        self.draw()
        pygame.display.flip()
        status = KEEP_GOING
        while status == KEEP_GOING:
            trigger = pygame.event.wait()
            ev = [trigger] + pygame.event.get()
            for event in ev:
                if hasattr(event, 'key') and event.key == K_ESCAPE:
                    status = EXIT
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    status = self.handleClick(event.pos)
        if status != EXIT:
            return self.level
        else:
            return EXIT
# Class managing workflow


class Game():

    def __init__(self, screen, level):
        self.screen = screen
        self.level = level
        (r, c, s) = LEVELS[self.level]
        self.grid = Grid(r, c, s)
        width = 150
        height = 100
        self.label = Label(str(
            self.grid.emptyValues) + " squares left",  (WIDTH / 2, 25, 500, 50), (255, 0, 0))
        self.gameOverLabel = Label('It was a nice game ! Do you want to play again ?', (
            WIDTH / 2, HEIGHT / 2 - 3 * height / 2, 4 * width, height), (0, 0, 255))
        self.buttons = [
            Button(
                'Yes', (WIDTH / 2 - width, HEIGHT / 2, width, height), (0, 255, 0), True),
            Button(
                'No', (WIDTH / 2 + width, HEIGHT / 2, width, height), (255, 0, 0), False)
        ]

    def draw(self):
        self.screen.fill((255, 255, 255))
        screen.blit(BACKGROUND, [(WIDTH - XBACK) / 2, (HEIGHT - YBACK) / 2])
        self.grid.draw(self.screen)
        self.label.draw(self.screen)

    def drawGameOver(self):
        self.gameOverLabel.draw(self.screen)
        for b in self.buttons:
            b.draw(self.screen)

    def handleGameOverClick(self, pos):
        (xPos, yPos) = pos
        for b in self.buttons:
            if b.handleClick(xPos, yPos):
                if b.value:
                    return WIN
                else:
                    return EXIT
        return KEEP_GOING

    def run(self):
        self.draw()
        pygame.display.flip()
        status = KEEP_GOING
        while status == KEEP_GOING:
            trigger = pygame.event.wait()
            ev = [trigger] + pygame.event.get()
            for event in ev:
                if hasattr(event, 'key') and event.key == K_ESCAPE:
                    status = EXIT
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    emptyVal = self.grid.handleClick(event)
                    if emptyVal != NO_CHANGE:
                        if emptyVal == WIN:
                            self.label.setText("You have won, congratz")
                            status = WIN
                        elif emptyVal == GAMEOVER:
                            self.label.setText("You have lost, :(")
                            status = GAMEOVER
                        else:
                            self.label.setText(str(emptyVal) + " squares left")
                        self.draw()
                        pygame.display.flip()
        if status != EXIT:
            return self.runPlayAgain()
        else:
            return False

    def runPlayAgain(self):
        self.drawGameOver()
        pygame.display.flip()
        status = KEEP_GOING
        while status == KEEP_GOING:
            trigger = pygame.event.wait()
            ev = [trigger] + pygame.event.get()
            for event in ev:
                if hasattr(event, 'key') and event.key == K_ESCAPE:
                    status = EXIT
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    status = self.handleGameOverClick(event.pos)
        return (status == WIN)


# RUN
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    menu = Menu(screen)
    keepGoing = True
    while(keepGoing):
        level = menu.run()
        if(level != EXIT):
            game = Game(screen, level)
            keepGoing = game.run()
        else:
            keepGoing = False
    pygame.quit()
