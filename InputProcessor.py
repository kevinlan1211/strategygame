import pygame, Interface

SELECTBOX_COLOR = (240, 215, 125)

class InputProcessor:
    def __init__(self, teamID, moveStateButtons = []):
        # Rect(corner x, corner y, width, height)
        self.point1 = (0, 0)
        self.point2 = (0, 0)
        #will be edited to be sent from client
        self.selectBox = pygame.Rect(self.point1, self.point2)
        self.isClicked = False
        self.selected = []
        self.selectedBuilding = None
        self.moveStateButtons = moveStateButtons
        self.teamID = teamID

    def coordToRect(self):
        if self.point1[0] > self.point2[0] or self.point1[1] > self.point2[1]:
            # return pygame.Rect(self.point1, (self.point2[0]-self.point1[0], self.point2[1]-self.point1[1]))
            return pygame.Rect(self.point2, (self.point1[0]-self.point2[0], self.point1[1]-self.point2[1]))
        else:
            # return pygame.Rect(self.point2, (self.point1[0]-self.point2[0], self.point1[1]-self.point2[1]))
            return pygame.Rect(self.point1, (self.point2[0]-self.point1[0], self.point2[1]-self.point1[1]))

    def updateBuildingSelection(self, buildingList, mouse):
        mousePoint = mouse.get_pos()
        for bL in buildingList:
            for b in bL:
                if pygame.Rect(mousePoint[0]- 4, mousePoint[1] - 4, 8, 8).colliderect(b.selectBox) and b.teamID == self.teamID:
                    b.highlighted = True
                else:
                    b.highlighted = False
                if mouse.get_pressed()[0]:
                    if b.highlighted:
                        b.selected = True
                        self.selected = []
                        self.selectedBuilding = b
                    else:
                        b.selected = False

    def checkButtonsClicked(self, mouse, resources):
        if self.selectedBuilding:
            if self.selectedBuilding.repeatingAction == -1:
                if self.selectedBuilding.bar:
                    self.selectedBuilding.cancelButton.checkClicked(mouse, resources)
                else:
                    for b in self.selectedBuilding.buildOptions:
                        b.checkClicked(mouse, resources)
            else:
                self.selectedBuilding.cancelButton.checkClicked(mouse, resources)

        for b in self.moveStateButtons:
            b.checkClicked(mouse, resources)



    # populates an interface with buttons based on selected units
    def updateInterface(self, interface:Interface.Interface):
        return self.selectedBuilding.interface()

    def updateSelection(self, unitList, screen):
        mouse = pygame.mouse
        if not self.isClicked:
            if mouse.get_pressed()[0]:
                self.isClicked = True
                self.point1 = mouse.get_pos()
                self.selectBox = self.coordToRect()
        else:
            self.point2 = mouse.get_pos()
            self.selectBox = self.coordToRect()
            self.selectBox.normalize()
            self.draw(screen)
            if not mouse.get_pressed()[0]:
                self.isClicked = False
                self.selected = []
            # mess with indentation here based on what feels better - either selecting units immediately upon being in
            # the box, or only changing units to selected once the user lets go.

                for u in unitList:
                    if self.teamID == u.teamID and self.checkCollision(u):
                        if u.unitType != "Base":
                            self.selected.append(u)

                if len(self.selected) > 0:
                    if self.selectedBuilding:
                        self.selectedBuilding.selected = False
                        self.selectedBuilding = None

        for u in self.selected:
            if u.health <= 0:
                self.selected.remove(u)

        return [u.unitID for u in self.selected]

    def drawSelection(self, screen, unitList):
        for u in self.selected:
            if u in unitList:
                if u.health>0:
                    pygame.draw.ellipse(screen, (210, 200, 168), (u.cornerX+6, u.cornerY+21, 24, 6), width = 1)

    def drawSelectionInterface(self, screen):
        i = 0
        for u in self.selected:
            screen.blit(u.interface(), (i, (screen.get_height() * 2 / 3 ) + 4))
            i += 30
        if self.selectedBuilding:
            interface = self.selectedBuilding.interface()
            i = 32
            screen.blit(interface[0], (i, screen.get_height()-24))
            for b in interface[1]:
                b.x = i
                b.y = screen.get_height()*2/3 + 36
                b.draw(screen)
                if self.selectedBuilding.bar:
                    i += 320
                else:
                    i += 128

    def checkCollision(self, u, width = 24, height = 24):
        return pygame.Rect(u.cornerX+6, u.cornerY, width, height).colliderect(self.selectBox)

    def draw(self, screen):
        # print(self.selectBox)
        if not (-2 < self.selectBox.width < 2 or -2 < self.selectBox.height < 2):
            pygame.draw.rect(screen, SELECTBOX_COLOR, self.selectBox, width = 1)
        else:
            pygame.draw.rect(screen, SELECTBOX_COLOR, self.selectBox)
