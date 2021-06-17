import pygame, Units, math, glob
from Interface import Button, Bar
from Units import loadSprite

SPR_EMPTY = loadSprite("Building\\nothing")
SPR_FORGE = loadSprite("Building\\Forge")
SPR_ARMOR = loadSprite("Building\\Armory")
SPR_MINES = loadSprite("Building\\Mine")
SPR_CLONE = loadSprite("Building\\Cloning")

SPR_CANCEL = loadSprite("Icon\\Cancel")
SPR_MAKEBODY = loadSprite("Icon\\Body")
SPR_DOLLAR = loadSprite("Icon\\Dollar")

class Building():
    def __init__(self, teamID, x, y, font:pygame.font.Font):
        self.teamID = teamID
        self.highlighted = False
        self.x = x
        self.y = y
        self.bar = None
        self.buildOptions = []
        self.sprite = SPR_EMPTY
        self.cornerX = self.x - self.sprite[0].get_rect().center[0]
        self.cornerY = self.y - self.sprite[0].get_rect().center[1]
        self.selected = False
        self.imageIndex = 0
        self.animInterval = 5
        self.defaultInterval = self.animInterval
        self.selectBox = pygame.Rect(self.cornerX, self.cornerY, 48, 48)
        self.sprID = 0
        self.markedForDelete = False
        self.upgradeBuilding = None
        self.font = font
        self.queuedAction = -1
        self.queuedUnit = None
        self.generatedResources = ['$', 0]
        self.repeatingAction = -1
        self.cancelButton = Button(SPR_CANCEL[0], self.font, "Cancel", additionalText="Will not refund cost")
        self.cancelButton.width = 40
        self.cancelButton.height = 40

    def animate(self):
        if self.animInterval > 0:
            self.animInterval -= 1
        else:
            self.imageIndex += 1
            if self.imageIndex >= len(self.sprite):
                self.imageIndex = 0
            self.animInterval = self.defaultInterval

        if self.bar:
            self.bar.act()

    def action(self, screen):
        if self.bar:
            if self.bar.progress >= 256:
                self.bar = None
                self.makeAction()
            if self.cancelButton.clicked:
                print('CANCELLING!')
                self.bar = None
                self.queuedAction = -1
                self.repeatingAction = -1
                self.resetButtons()
                self.cancelButton.clicked = False
        else:
            for i in range(len(self.buildOptions)):
                b = self.buildOptions[i]
                if b.clicked:
                    print("clicked!")
                    self.queuedAction = i
                    self.bar = Bar(b.rate)
        if self.repeatingAction != -1:
            self.buildOptions[self.repeatingAction].clicked = True
            self.queuedAction = self.repeatingAction

        self.draw(screen)

    def getClicked(self):
        clickedButton = None
        for b in self.buildOptions:
            if b.clicked:
                clickedButton = b
        return clickedButton

    def interface(self):
        if self.bar:
            return [self.name, [self.bar, self.cancelButton]]
        else:
            return [self.name, self.buildOptions]

    def upgrade(self, upgradeType):
        self.markedForDelete = True
        self.upgradeBuilding = eval(upgradeType + "(self.teamID, self.x, self.y, self.font)")
        print("upgraded to", self.upgradeBuilding)
        self.resetButtons()

    # keys are '$', 'ß', and '¶'. These are 'harvested' then reset by the client.
    # generated resource list is formatted: ['key', amount]
    def generateResource(self, key = '$', amount = 0):
        self.generatedResources[0] = key
        self.generatedResources[1] = amount
        self.resetButtons()

    def buildUnit(self, unitType):
        if self.teamID == 0:
            xOffset = 24
        else:
            xOffset = -24
        self.queuedUnit = [unitType, self.x + xOffset, self.y]
        self.resetButtons()

    def resetButtons(self):
        for b in self.buildOptions:
            b.clicked = False
            b.highlighted = False
        self.bar = None
        self.queuedAction = -1

    def draw(self, screen):
        self.animate()
        if self.highlighted:
            pygame.draw.ellipse(screen, (128, 150, 160), (self.cornerX, self.cornerY+32, 48, 12), width = 1)
        if self.selected:
            pygame.draw.ellipse(screen, (128, 150, 160), (self.cornerX-2, self.cornerY+30, 52, 16), width = 1)
        screen.blit(self.sprite[self.imageIndex], (self.cornerX, self.cornerY))


class EmptySpace(Building):
    # this building is used both as the 'empty space' building like in colony, but also as the
    def __init__(self, teamID, x, y, font:pygame.font.Font):
        super().__init__(teamID, x, y, font)
        self.name = font.render("Empty Space", True, (200, 200, 180))
        self.sprID = 0
        self.buildOptions.append(Button(SPR_FORGE[0], self.font, "Build Forge", cost={'$':50, 'ß':0, '¶':0}, rate=1))
        self.buildOptions.append(Button(SPR_ARMOR[0], self.font, "Build Armory", cost={'$':50, 'ß':0, '¶':0}, rate=1))
        self.buildOptions.append(Button(SPR_CLONE[0], self.font, "Build Cloning", cost={'$':30, 'ß':0, '¶':0}, rate=1))
        self.buildOptions.append(Button(SPR_MINES[0], self.font, "Build Mines", cost={'$':30, 'ß':0, '¶':0}, rate=1))
        self.sprite = SPR_EMPTY


    def makeAction(self):
        if self.queuedAction == 0:
            self.upgrade("Forge")
        if self.queuedAction == 1:
            self.upgrade("Armory")
        if self.queuedAction == 2:
            self.upgrade("Cloning")
        if self.queuedAction == 3:
            self.upgrade("Mine")
        self.queuedAction = -1

class Forge(Building):
    def __init__(self, teamID, x, y, font:pygame.font.Font):
        super().__init__(teamID, x, y, font)
        self.name = font.render("Forge", True, (200, 200, 180))
        self.sprID = 1
        self.sprite = SPR_FORGE
        self.buildOptions.append(Button(SPR_FORGE[0], self.font, "Upgrade", cost={'$':80, 'ß':30, '¶':0}, rate=1))
        if teamID == 0:
            self.buildOptions.append(Button(Units.SPR_BIR[0], self.font, "Produce Grunt", cost={'$':10, 'ß':0, '¶':1}, rate = 3))
        if teamID == 1:
            self.buildOptions.append(Button(Units.SPR_RIL[0], self.font, "Produce Grunt", cost={'$':10, 'ß':0, '¶':1}, rate = 3))
        self.buildOptions.append(Button(SPR_CLONE[0], self.font, "Weapons Research", additionalText="Generates: ß1/sec", rate=4.25))

    def makeAction(self):
        if self.queuedAction == 0:
            self.upgrade("Forge2")
        if self.queuedAction == 1:
            self.buildUnit("Grunt")
        if self.queuedAction == 2:
            self.generateResource('ß', 1)
            self.repeatingAction = 2
        self.queuedAction = -1

class Armory(Building):
    def __init__(self, teamID, x, y, font:pygame.font.Font):
        super().__init__(teamID, x, y, font)
        self.name = font.render("Armory", True, (200, 200, 180))
        self.sprID = 2
        self.sprite = SPR_ARMOR
        self.buildOptions.append(Button(SPR_ARMOR[0], self.font, "Upgrade", cost={'$':80, 'ß':30, '¶':0}, rate=1))
        if teamID == 0:
            self.buildOptions.append(Button(Units.SPR_B2IR[0], self.font, "Produce Sword", cost={'$':10, 'ß':0, '¶':1}, rate = 3))
        if teamID == 1:
            self.buildOptions.append(Button(Units.SPR_R2IL[0], self.font, "Produce Sword", cost={'$':10, 'ß':0, '¶':1}, rate = 3))
        self.buildOptions.append(Button(SPR_CLONE[0], self.font, "Weapons Research", additionalText="Generates: ß1/sec", rate=4.25))

    def makeAction(self):
        if self.queuedAction == 0:
            self.upgrade("Armory2")
        if self.queuedAction == 1:
            self.buildUnit("Sword")
        if self.queuedAction == 2:
            self.generateResource('ß', 1)
            self.repeatingAction = 2
        self.queuedAction = -1

class Mine(Building):
    def __init__(self, teamID, x, y, font:pygame.font.Font):
        super().__init__(teamID, x, y, font)
        self.name = font.render("Mine", True, (200, 200, 180))
        self.sprID = 3
        self.sprite = SPR_MINES
        self.buildOptions.append(Button(SPR_MINES[0], self.font, "Upgrade", cost={'$':80, 'ß':30, '¶':0}, rate=1))
        self.buildOptions.append(Button(SPR_DOLLAR[0], self.font, "Mine Resources", additionalText="Generates: $1/sec", rate=4.25))
        if teamID == 0:
            self.buildOptions.append(Button(Units.SPR_BIR[0], self.font, "Call Militia", cost={'$':5, 'ß':0, '¶':1}, rate = 3))
        if teamID == 1:
            self.buildOptions.append(Button(Units.SPR_RIL[0], self.font, "Call Militia", cost={'$':5, 'ß':0, '¶':1}, rate = 3))


    def makeAction(self):
        if self.queuedAction == 0:
            self.upgrade("Mine2")
        if self.queuedAction == 1:
            self.generateResource('$', 1)
            self.repeatingAction = 1
        if self.queuedAction == 2:
            self.buildUnit("Worker")

class Cloning(Building):
    def __init__(self, teamID, x, y, font:pygame.font.Font):
        super().__init__(teamID, x, y, font)
        self.name = font.render("Cloning", True, (200, 200, 180))
        self.sprID = 4
        self.sprite = SPR_CLONE
        self.buildOptions.append(Button(SPR_CLONE[0], self.font, "Upgrade", cost={'$':80, 'ß':30, '¶':0}, rate=1))
        self.buildOptions.append(Button(SPR_MAKEBODY[0], self.font, "Clone Bodies", additionalText="Gain ¶1/2 sec", rate=2.125))

    def makeAction(self):
        if self.queuedAction == 0:
            self.upgrade("Cloning2")
        if self.queuedAction == 1:
            self.generateResource('¶', 1)
            self.repeatingAction = 1