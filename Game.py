import Units, InputProcessor, pygame, math, sys, Interface
from Units import Grunt, Sword, Base
from random import randint



# pygame.init()
started = True
RES = [(800, 450), (960, 540), (1600, 900)]

# note: very bad and quite an ugly effect but stops units from stacking
class Game():
    def __init__(self, resIndex):
        pygame.init()
        self.screenWidth = RES[resIndex][0]
        self.screenHeight = RES[resIndex][1]
        self.displayEnabled = False
        self.unitList = [[], []]
        self.buildings = [[], []]
        self.unitID = 0
        self.depthSortTimer = 12
        self.proximityTimer = 8
        self.clock = pygame.time.Clock()
        if self.displayEnabled:
            self.screen = pygame.Surface((self.screenWidth, self.screenHeight), pygame.HWSURFACE | pygame.HWACCEL)
            # self.scaledScreen = pygame.display.set_mode((screenWidth*2, screenHeight*2), pygame.HWSURFACE | pygame.HWACCEL)
            self.scaledScreen = pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.HWSURFACE | pygame.HWACCEL)

            self.gui = pygame.font.Font(pygame.font.get_default_font(), 10)
            self.guiServer = self.gui.render("SERVER FOOTAGE", False, (225, 225, 250))
        self.keys = [None, None]
        self.moveState = [-1, -1]
        self.unitsToSpawn = [[], []]

        # self.inProc = InputProcessor.InputProcessor()

    def receive(self, keys, player, buildings, units, state):
        self.keys[player] = keys
        self.buildings[player] = buildings
        self.unitsToSpawn[player] = units
        self.moveState[player] = state

    def getData(self, signature):
        # format: { unitID : [teamID, x, y, health, imageIndex, direction, targetX, currentState, healthMod, unitType] }
        dataDict = {}
        finalData = {}
        for uL in self.unitList:
            for u in uL:
                currentState = -1
                uID = u.unitID
                if u.sprite == u.spriteIdle:
                    currentState = 0
                elif u.sprite == u.spriteMoving:
                    currentState = 1
                elif u.sprite == u.spriteAttack:
                    currentState = 2
                else:
                    print("failed all cases.", [u.teamID, u.x, u.y, u.health, u.imageIndex, u.direction, currentState, u.healthMod])
                unitType = u.__class__.__name__
                targetX = -1
                if u.target:
                    targetX = u.target.x
                dataDict[uID] = [u.teamID, u.x, u.y, u.health, u.imageIndex, u.direction, targetX, currentState, u.healthMod, unitType]
        finalData['units'] = dataDict
        finalData["buildings"] = self.buildings[(signature-1)*-1]
        return finalData

    def proximityCorrection(self, uList = [], uList2 = []):
        for uIndex in range(len(uList)):
            for uIndex2 in range(len(uList)):
                if uIndex != uIndex2:
                    if Units.getDist(uList[uIndex], uList[uIndex2]) <= 8:
                        uList[uIndex].x += randint(0, 2) - 1
                        uList[uIndex].y += randint(0, 2) - 1
        for uIndex in range(len(uList2)):
            for uIndex2 in range(len(uList2)):
                if uIndex != uIndex2:
                    if Units.getDist(uList2[uIndex], uList2[uIndex2]) <= 8:
                        uList2[uIndex].x += randint(0, 2) - 1
                        uList2[uIndex].y += randint(0, 2) - 1

    def drawBG(self):
        self.screen.fill((132, 112, 103))

    def unitAct(self, u, keys):
        u.updateTarget(self.unitList[(u.teamID - 1) * (-1)])
        if u.selected and keys:
            #if u.teamID == signature:
            u.playerAction(keys)
            #else:
                #u.move()
                #u.animate()
        else:
            u.aiAction()
        if self.displayEnabled:
            u.draw(self.screen)
        self.removeUnits()

    def removeUnits(self):
        for ul in self.unitList:
            for u in ul:
                if u.health<=0:
                    self.unitList[u.teamID].remove(u)


    def spawnUnit(self, unitType, teamID, x, y, healthMod = 1, damageMod = 1, moveSpeedMod = 1, rangeMod = 1, attackSpeedMod = 1):
        self.unitList[teamID].append(eval(unitType + "(self.unitID, teamID, x, y, healthMod, damageMod, moveSpeedMod, rangeMod, attackSpeedMod)"))
        print("unit spawned! ID:", self.unitID)
        self.unitID += 1

    def startGame(self):
        # player input processor
        # inter = Interface.Interface(screen)
        # for quick reference, the unit constructor goes as follows: (teamID, x, y, <statMod>)
        self.spawnUnit("Base", 0, 0, self.screenHeight/3+24)
        self.spawnUnit("Base", 1, self.screenWidth-48, self.screenHeight/3+24)
        for i in range(8):
            if i % 2 == 0:
                self.spawnUnit("Grunt", 0, 70, 100 + randint(20, 180))
            else:
                self.spawnUnit("Sword", 0, 80, 100 + randint(0, 200))
        for i in range(8):
            if i % 2 == 0:
                self.spawnUnit("Grunt", 1, self.screenWidth-70, 100 + randint(20, 180))
            else:
                self.spawnUnit("Sword", 1, self.screenWidth-80, 100 + randint(0, 200))

        for uL in self.unitList:
            for u in uL:
                self.unitAct(u, None)

    def runGame(self):
        if self.displayEnabled:
            self.drawBG()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    ssName = "screenshot.png"
                    pygame.image.save(self.screen, ssName)
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
        if self.proximityTimer > 0:
            self.proximityTimer -=1
        else:
            self.proximityTimer = 8
            self.proximityCorrection(self.unitList[0], self.unitList[1])


        '''if self.depthSortTimer > 0:
            self.depthSortTimer -=1
        else:
            depthSortTimer = 12
            for uL in self.unitList:
                uL.sort(key=lambda x: x.y*-1, reverse=True)'''

        '''i = 0
        j = 0
        u0exists = False
        u1exists = False
        while i < len(self.unitList[0]) or j < len(self.unitList[1]):
            if i < len(self.unitList[0]):
                u0 = self.unitList[0][i]
                u0exists = True
            if j < len(self.unitList[1]):
                u1 = self.unitList[1][j]
                u1exists = True

            if u0exists and (not u1exists or u0.y < u1.y):
                self.unitAct(u0, keys, signature)
                i += 1
            else:
                self.unitAct(u1, keys, signature)
                j += 1

            u0exists = False
            u1exists = False'''
        for i in range(0, 2):
            for u in self.unitsToSpawn[i]:
                self.spawnUnit(u[0], i, u[1], u[2])

        for i in range(0, 2):
            for u in self.unitList[i]:
                if self.moveState[i] != -1:
                    u.moveState = self.moveState[i]
                self.unitAct(u, self.keys[i])

        # will be modified to work on a client/server
        # teamID = 0
        # self.inProc.updateSelection(self.unitList[teamID], screen)
        if self.displayEnabled:
            self.screen.blit(self.guiServer, (22, 22))

        # ui testing code
        # inter.draw(screen)

        # print(pygame.mouse.get_pressed()[0])
        self.clock.tick(60)
        # scaledScreen.blit(pygame.transform.scale2x(screen), (0, 0))
        if self.displayEnabled:
            self.scaledScreen.blit(self.screen, (0, 0))
            pygame.event.pump()
            pygame.display.update()
