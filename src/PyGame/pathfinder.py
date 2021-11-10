# -*- coding: utf-8 -*-
"""
    My first try on path finder code, using PyGame module.
"""
__author__ = "Luciano Kendzierski"
__version__ = "0.0.2"
__email__ = "luciano.kendzierski@gmail.com"


import pygame
import random
import math

class Config:
    def __init__(self):
        self.W_DISP = 800
        self.H_DISP = 600 
        # Table Config
        self.SpotSize = 10
        self.tableLineColor = (10, 100, 50)
        self.tableLineWidth = 1
        self.borderDistance = 1
        self.blockPinsCount = 700
        self.blockPinsColor = (100,0,0)
        self.show_block_pins = True
        self.showTable = True

        # Pin Config
        self.PinRadius = int(self.SpotSize/2)

        # Walker
        self.walkerColor = ( 51, 255 , 208 )
        self.targetColor = (100,0,100)

        self.backGroundColor = ( 50 , 50 , 50 )
        self.tickValue = 60

        

    def get_resolution(self):
        return (self.W_DISP,self.H_DISP)

class Table:
    def __init__(self, config):
        self.config = config
        self.SpotSize = config.SpotSize
        self.lineWidth = config.tableLineWidth
        self.lineColor = config.tableLineColor
        self.borderDistance = config.borderDistance

        (self.d_width, self.d_height) = config.get_resolution()

        self.width_spots = int(self.d_width/self.SpotSize)
        self.height_spots = int(self.d_height/self.SpotSize)
        self.maxWidth = self.width_spots-3
        self.maxHeight = self.height_spots-3

        self.blockPins = []

        dropped = 0
        
        while dropped < config.blockPinsCount:
            i = random.randrange(0, self.maxWidth)
            j = random.randrange(0, self.maxHeight)
            if     not (i > self.maxWidth-3 and j < 3):
                self.blockPins.append((i,j))
                dropped += 1


    # usando position como posição relativa dos spots na table 
    # e coordenadas como valor absoluto em y e x no display
    def get_coordinates(self, position):
        coord_w = self.SpotSize * (position[0] + self.borderDistance) + int(self.SpotSize/2)
        coord_h = self.SpotSize * (position[1] + self.borderDistance) + int(self.SpotSize/2)

        return (coord_w, coord_h)

    def onTable(self, position):
        if position[0] < 0 or position[0] > self.maxWidth:
            return False

        if position[1] < 0 or position[1] > self.maxHeight:
            return False

        return True

    def get_distance(self, pinA, pinB):
        a = pinA.position[0]-pinB.position[0]
        b = pinA.position[1]-pinB.position[1]
        return math.sqrt(math.pow(a,2) + math.pow(b,2))


    def update(self):
        pass

    def draw(self, display, draw_lines=True, draw_block_pins=True):
        if draw_lines:
            self.draw_lines(display)
        
        if draw_block_pins:
            self.draw_block_pins(display)

    def draw_lines(self, display):
        for index in range(self.borderDistance, self.width_spots):
            tmpPos = index * self.SpotSize
            startPoint = (tmpPos, self.SpotSize)
            endPoint = (tmpPos, self.d_height-self.SpotSize)
            pygame.draw.line(display, self.lineColor, startPoint, endPoint, self.lineWidth)

        for index in range(self.borderDistance, self.height_spots):
            tmpPos = index * self.SpotSize
            startPoint = (self.SpotSize, tmpPos)
            endPoint = (self.d_width-self.SpotSize, tmpPos)
            pygame.draw.line(display, self.lineColor, startPoint, endPoint, self.lineWidth)

    def draw_block_pins(self, display):
        for blockPin in self.blockPins:
            tmpPin = Pin(self.config, self.config.blockPinsColor, blockPin)
            tmpPin.draw(display, self)


class Pin:
    def __init__(self, config, color, position):
        self.radius = config.PinRadius
        self.color = color
        self.position = position

    def update(self):
        pass

    def draw(self, display, table):
        coordinates = table.get_coordinates(self.position)
        pygame.draw.circle(display, self.color, coordinates, self.radius, 0)

    def set_position(self, position):
        self.position = position


class Walker:
    def __init__(self, config, table):
        self.config = config
        self.color = config.walkerColor
        self.table = table

        targetPos = (self.table.maxWidth, 0)
        self.target = Pin(self.config, self.config.targetColor, targetPos)

        self.i = random.randrange(0, self.table.maxWidth)
        self.j = random.randrange(0, self.table.maxHeight)
        position = (self.i, self.j)
        self.pin = Pin(config, self.color, position)

        self.allowedSteps = ((1,0),(0,1),(-1,0),(0,-1))
        self.path = []
        self.pathChecked = False
        self.onTarget = False
        self.pathCount = 0
        self.finish = False
        self.badPins = []

    def update(self):
        if self.pin.position != self.target.position:
            self.step()    
        else:
            if not self.pathChecked:
                self.checkPath()
                self.pathChecked = True

            self.onTarget = True
        

    def step(self):
        bestH = None
        bestPos = None
        for step in self.allowedSteps:
            tmpPos = (self.i + step[0], self.j + step[1])
            if self.table.onTable(tmpPos) and not tmpPos in (self.path + self.badPins + self.table.blockPins):
                tmpPin = Pin(self.config, self.color, tmpPos)
                tmpH = self.table.get_distance(tmpPin, self.target)
                if bestPos is None or bestH > tmpH:
                    bestH = tmpH
                    bestPos = tmpPos

        if not bestPos is None:
            self.path.append(bestPos)
            (self.i, self.j) = bestPos
            self.pin.set_position(bestPos)
        elif len(self.path) > 0:
            tmpPos = self.path[-1]
            (self.i, self.j) = tmpPos
            self.path.remove(tmpPos)
            self.badPins.append(tmpPos)
            self.pin.set_position(tmpPos)
        else:
            print("Len", len(self.path))
            
    def checkPath(self):
        for index in range(len(self.path)):
            if index >= len(self.path):
                break
                
            nearNodes = []
            actualNode = self.path[index]
            for step in self.allowedSteps:
                stepPos = (actualNode[0]+step[0], actualNode[1]+step[1])
                if stepPos in self.path and not self.path.index(stepPos) in (index-1, index+1):
                    nearNodes.append(self.path.index(stepPos))
            if len(nearNodes) > 0:
                if len(nearNodes) == 2 and nearNodes[0] < nearNodes[1]:
                    nearNodes[0] = nearNodes[1]

                self.path = self.path[0:index] + self.path[nearNodes[0]:-1]

    def draw(self, display):

        self.target.draw(display, self.table)

        if not self.onTarget:
            self.pin.draw(display, self.table)
        else:
            for index in range(self.pathCount):
                color = (10,10,155)
                tPin = Pin(self.config, color, self.path[index])
                tPin.draw(display, self.table)
            self.pathCount += 1
            if self.pathCount >= len(self.path):
                self.finish = True

class Game:
    def __init__(self, config, display ):
        self.display = display
        self.config = config
        self.table = Table(self.config)
        self.walker = Walker(self.config, self.table)
        self.over = False
        self.clock = pygame.time.Clock()

    def update(self):
        self.table.update()
        self.walker.update()
        if self.walker.finish:
            self.over = True


    def draw(self, display):
        self.walker.draw(display)

        self.table.draw(display, self.config.showTable, self.config.show_block_pins)

    def events( self ):
        for event in pygame.event.get():
            self.event_checker( event ) 

    def event_checker( self, event ):
        if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                pygame.quit()
                quit()
                
            if event.key == pygame.K_r:
                self.over = True

            if event.key == pygame.K_t:
                self.config.showTable = False if self.config.showTable else True

            if event.key == pygame.K_b:
                self.config.show_block_pins = False if self.config.show_block_pins else True

    def run( self ):
        while not self.over:
            self.display.fill( self.config.backGroundColor )

            self.events()

            self.update()
            self.draw(self.display)


            pygame.display.flip()
            self.clock.tick( self.config.tickValue )


def main():
    pygame.init()
    config = Config()
    display = pygame.display.set_mode( config.get_resolution() )
    pygame.display.set_caption("Teste")

    while True:
        game = Game(config, display)
        game.run()


if __name__ == '__main__':
    main()
