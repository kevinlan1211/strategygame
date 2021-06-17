import Units, pygame, math, sys, json, InputProcessor, Interface, Buildings, Effects
from Units import Grunt, Sword, Base
from Network import Network

RES = [(800, 450), (960, 540), (1600, 900)]
COL_BG = (132, 112, 103)

class Client():
    def __init__(self, resIndex, scaled):

        pygame.init()
        self.teamID = 0
        self.started = True
        self.screenWidth = RES[resIndex][0]
        self.screenHeight = RES[resIndex][1]
        self.screen = pygame.Surface((self.screenWidth, self.screenHeight))
        self.screenScalingEnabled = scaled
        if scaled:
            self.scaledScreen = pygame.display.set_mode((self.screenWidth*2, self.screenHeight*2), pygame.HWSURFACE | pygame.HWACCEL)
        else:
            self.scaledScreen = pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.HWSURFACE | pygame.HWACCEL)
        self.clock = pygame.time.Clock()
        self.inProc = None
        self.gui = pygame.font.Font("Fonts\\Kenney Mini Square.ttf", 12)
        self.guiClient = None
        self.receivedData = {}
        self.unitList = []
        self.fxList = []
        self.buildingList = [[], []]
        self.buildingsToSend = []
        self.resources = {'$': 0, 'ß': 0, '¶': 0}
        self.makeResText()


        #self.teamID = teamID

    def drawBG(self, screen):
        screen.fill(COL_BG)

    def jEncode(self, dict):
        #turns into json formatted string
        return json.dumps(dict) + "*"

    def jDecode(self, string):
        #turns formatted string into dict
        return json.loads(string)

    def spawnUnit(self, unitID, unitType, teamID, x, y, healthMod = 1, damageMod = 1, moveSpeedMod = 1, rangeMod = 1, attackSpeedMod = 1):
        result = eval(unitType + "(unitID, teamID, x, y, healthMod, damageMod, moveSpeedMod, rangeMod, attackSpeedMod)")
        self.unitList.append(result)
        print("unit spawned! ID:", unitID)
        return result

    def makeRects(self, unitList):
        rectList = []
        for u in unitList:
            rectList.append(pygame.Rect(u.cornerX + 6, u.cornerY, 24, 24))
        return rectList

    def makeResText(self):
        resString = "Resources: "
        for k, c in self.resources.items():
            resString += str(k) + ": " + str(c) + "   "
        self.resourceGui = self.gui.render(resString, False, (212, 222, 210))

    def updateResText(self, prev):
        changed = False
        if not prev["$"] == self.resources["$"]:
            changed = True
        if not prev["ß"] == self.resources["ß"]:
            changed = True
        if not prev["¶"] == self.resources["¶"]:
            changed = True
        if changed:
            self.makeResText()

    def updateBuildings(self):
        for i in range(len(self.receivedData["buildings"])):
            # sprIDs:
            # 0 = SPR_EMPTY
            # 1 = SPR_FORGE
            # 2 = SPR_ARMOR
            # 3 = SPR_MINES
            # 4 = SPR_CLONE
            sprID = self.receivedData["buildings"][i]
            if sprID == 0 and not self.buildingList[(self.teamID - 1) * -1][i].sprite == Buildings.SPR_EMPTY:
                self.buildingList[(self.teamID - 1) * -1][i].sprite = Buildings.SPR_EMPTY
            if sprID == 1 and not self.buildingList[(self.teamID - 1) * -1][i].sprite == Buildings.SPR_FORGE:
                self.buildingList[(self.teamID - 1) * -1][i].sprite = Buildings.SPR_FORGE
            if sprID == 2 and not self.buildingList[(self.teamID - 1) * -1][i].sprite == Buildings.SPR_ARMOR:
                self.buildingList[(self.teamID - 1) * -1][i].sprite = Buildings.SPR_ARMOR
            if sprID == 3 and not self.buildingList[(self.teamID - 1) * -1][i].sprite == Buildings.SPR_MINES:
                self.buildingList[(self.teamID - 1) * -1][i].sprite = Buildings.SPR_MINES
            if sprID == 4 and not self.buildingList[(self.teamID - 1) * -1][i].sprite == Buildings.SPR_CLONE:
                self.buildingList[(self.teamID - 1) * -1][i].sprite = Buildings.SPR_CLONE


    def startGame(self):
        n = Network()
        self.teamID = int(n.getData())
        playerString = "TEAMID: " + str(self.teamID)
        self.guiClient = self.gui.render(playerString, False, (225, 225, 250))
        interface = Interface.Interface(self.screen, self.teamID, self.gui)
        self.inProc = InputProcessor.InputProcessor(self.teamID, interface.globalActions)
        self.resources = {'$': 50, 'ß': 0, '¶': 8}
        self.makeResText()

        buildingSpacing = (self.screenHeight*2/3) / 8
        for b in range(7):
            xMod = -0.00065*((b*buildingSpacing) - self.screenHeight/3)**2.0 + 96
            self.buildingList[0].append(Buildings.EmptySpace(0, xMod, b*buildingSpacing+72, self.gui))
            self.buildingList[1].append(Buildings.EmptySpace(1, self.screenWidth-xMod, b*buildingSpacing+72, self.gui))


        # dictionary formatting:
        # { unitID : [teamID, x, y, health, imageIndex, direction, targetX, currentState, healthMod, unitType] }
        # currentState: 0 is idle, 1 is moving, 2 is attacking

        depthSortTimer = 8
        moneyTimer = 60
        peopleTimer = 600
        while self.started:
            prevResources = self.resources.copy()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        ssName = "screenshot.png"
                        pygame.image.save(self.screen, ssName)
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()


            # draw the background
            self.drawBG(self.screen)
            # per server communication or whatever:
            # signature = self.teamID

            # sent buildings list setup
            self.buildingsToSend = [b.sprID for b in self.buildingList[self.teamID]]
            # sent unit making list setup
            unitsToSend = [b.queuedUnit for b in self.buildingList[self.teamID] if b.queuedUnit]
            # reset queued units
            for b in self.buildingList[self.teamID]:
                b.queuedUnit = None

            selections = self.inProc.updateSelection(self.unitList, self.screen)
            self.inProc.updateBuildingSelection(self.buildingList, pygame.mouse)
            self.inProc.checkButtonsClicked(pygame.mouse, self.resources)

            states = -1
            for i in range(len(interface.globalActions)):
                b = interface.globalActions[i]
                if b.clicked:
                    states = i

            self.inProc.drawSelection(self.screen, self.unitList)
            # print(selections)
            keys = pygame.key.get_pressed()
            # print([(i, v) for i, v in enumerate(keys) if v == 1]
            toSend = {"keys": keys, "selections": selections, "buildings": self.buildingsToSend, "units": unitsToSend, "moveState": states}
            n.send(self.jEncode(toSend))

            # ^ SEND STUFF v PROCESS RECEIVED STUFF

            self.receivedData = self.jDecode(n.getData())
            # print([(uID, params[3], params[4], params[7]) for uID, params in self.receivedData.items()])
            for unitID, paramList in self.receivedData['units'].items():
                unitID = int(unitID)
                found = False
                
                u = None
                for un in self.unitList:
                    if un.unitID == unitID:
                        found = True
                        u = un
                        break
                if not found:
                    u = self.spawnUnit(unitID, paramList[9], paramList[0], paramList[1], paramList[2], paramList[8])
                    # make spawning effect
                    self.fxList.append(Effects.SpawnEffect(paramList[1], paramList[2]))

                u.x = paramList[1]
                u.y = paramList[2]
                u.health = paramList[3]
                u.imageIndex = paramList[4]
                u.direction = paramList[5]
                u.updateSprites(paramList[6])
                if paramList[7] == 0:
                    u.sprite = u.spriteIdle
                elif paramList[7] == 1:
                    u.sprite = u.spriteMoving
                elif paramList[7] == 2:
                    u.sprite = u.spriteAttack
                if u.health <= 0:
                    self.unitList.remove(u)
            for u in self.unitList:
                if str(u.unitID) not in self.receivedData['units']:
                    u.selected = False
                    self.unitList.remove(u)
            # this updates enemy building sprites based on their upgrades
            self.updateBuildings()

            # money gain timers here
            if moneyTimer > 0:
                moneyTimer -= 1
            else:
                moneyTimer = 60
                self.resources['$'] += 1
                self.makeResText()

            if peopleTimer > 0:
                peopleTimer -= 1
            else:
                peopleTimer = 600
                self.resources['¶'] += 1
                self.makeResText()


            if depthSortTimer > 0:
                depthSortTimer -=1
            else:
                depthSortTimer = 8
                self.unitList.sort(key=lambda x: x.y*-1, reverse=True)

            for bL in self.buildingList:
                for b in bL:
                    b.action(self.screen)
            i = 0
            for b in self.buildingList[self.teamID]:
                # 'harvests' resources generated by buildings
                if b.generatedResources[1] > 0:
                    self.resources[b.generatedResources[0]] += b.generatedResources[1]
                    b.generatedResources[1] = 0

                if b.markedForDelete:
                    self.buildingList[self.teamID][i] = b.upgradeBuilding
                    if self.inProc.selectedBuilding == b:
                        print("updating selection to new building")
                        b.selected = False
                        self.buildingList[self.teamID][i].selected = True
                        self.inProc.selectedBuilding = self.buildingList[self.teamID][i]
                i += 1

            for u in self.unitList:
                u.draw(self.screen)

            for f in self.fxList:
                f.draw(self.screen)

            for f in self.fxList:
                if f.markedForDelete:
                    self.fxList.remove(f)
                    del f

            # updates rendered resources text of the player
            self.updateResText(prevResources)

            # self.inProc.draw(self.screen)
            self.screen.blit(self.guiClient, (22, 22))
            interface.draw(self.screen)
            self.inProc.drawSelectionInterface(self.screen)
            # draw the resources of the player ((somewhere))
            self.screen.blit(self.resourceGui, (self.screenWidth - 280, self.screenHeight - 24))
            self.clock.tick(60)
            pygame.event.pump()
            if self.screenScalingEnabled:
                self.scaledScreen.blit(pygame.transform.scale2x(self.screen), (0, 0))
            else:
                self.scaledScreen.blit(self.screen, (0, 0))




            pygame.display.update()

c= Client(2, False)
c.startGame()