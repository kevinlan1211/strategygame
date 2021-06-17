import pygame
from Units import loadSprite
SPR_SPAWN = loadSprite("Fx\\Spawn")


class LoopingEffect:
    def __init__(self, x, y, repeat):
        self.x = x
        self.y = y
        self.loops = repeat
        self.imageIndex = 0
        self.defaultInterval = 1
        self.imageInterval = self.defaultInterval
        self.sprite = SPR_SPAWN
        self.markedForDelete = False

    def animate(self):
        if self.imageInterval>0:
            self.imageInterval -=1
        else:
            self.imageInterval = self.defaultInterval
            self.imageIndex += 1
        if self.imageIndex >= len(self.sprite):
            self.imageIndex = 0
            self.loops -=1
            if self.loops < 0:
                self.markedForDelete = True

    def draw(self, screen):
        if not self.markedForDelete:
            self.cornerX = self.x - self.sprite[0].get_rect().center[0]
            self.cornerY = self.y - self.sprite[0].get_rect().center[1]
            screen.blit(self.sprite[self.imageIndex], (self.cornerX, self.cornerY))
        self.animate()

class SpawnEffect(LoopingEffect):
    def __init__(self, x, y):
        super().__init__(x, y, 0)
