import pygame
from Units import loadSprite


SPR_MOVES = loadSprite("Icon\\Moves")

class Bar(pygame.Rect):
    def __init__(self, rate):
        super().__init__(0, 0, 256, 12)
        self.rate = rate
        self.progress = 0
    def act(self):
        if self.progress < 256:
            self.progress += self.rate
        # self.draw()
    def draw(self, screen):
        pygame.draw.rect(screen, (36, 36, 36), self)
        pygame.draw.rect(screen, (128, 220, 84), (self.x, self.y, self.progress, 12))

class Button(pygame.Rect):
    def __init__(self, image: pygame.Surface, font: pygame.font.Font, text: str, cost={'$':0, 'ß':0, '¶':0}, additionalText=None, rate=1):
        super().__init__(-80, -80, 64, 64)
        self.image = image
        self.cost = cost
        costString = ""
        costsAnything = False
        for k, c in self.cost.items():
            if c > 0:
                costString += str(k) + str(c) + " "
                costsAnything = True
        if costsAnything:
            costString = "Cost: " + costString
        elif additionalText:
            costString += additionalText
        self.text = {'0' : font.render(text, False, (245, 235, 230)), '14': font.render(costString, False, (245, 240, 200))}

        print(self.text)
        self.rate = rate
        self.clicked = False
        self.buildRate = rate
        self.highlighted = False
        self.highlightThickness = 1.0
        self.highlightRate = 0.25
        self.bar = None

    def checkClicked(self, mouse, resources):
        mousePoint = mouse.get_pos()
        if pygame.Rect(mousePoint[0] - 4, mousePoint[1] - 4, 8, 8).colliderect(self):
            self.highlighted = True
        else:
            self.highlighted = False

        if mouse.get_pressed()[0]:
            enough = True
            # print(resources)
            # print(self.cost)
            for k in resources:
                if resources[k] < self.cost[k]:
                    enough = False
            if enough:
                if self.highlighted:
                    self.clicked = True
                    for k in resources:
                        resources[k] -= self.cost[k]
                else:
                    self.clicked = False
            else:
                self.clicked = False
        else:
            self.clicked = False

    def act(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, (180, 176, 148), self)
        if self.highlighted:
            self.highlightThickness += self.highlightRate
            if self.highlightThickness > 4:
                self.highlightRate = -0.25
            if self.highlightThickness < 1:
                self.highlightRate = 0.25
            pygame.draw.rect(screen, (200, 200, 155), self, width=int(self.highlightThickness))
        screen.blit(self.image, (self.centerx-self.image.get_width()/2, self.centery-self.image.get_height()/2))
        for k, t in self.text.items():
            screen.blit(t, (self.x, self.y+self.height + 12 + int(k)))

class Interface():
    def __init__(self, screen, teamID, font):
        self.back = pygame.Rect(0, screen.get_height()*2/3, screen.get_width(), screen.get_height()*1/3)
        self.teamID = teamID
        self.buttonList = []
        self.font = font
        self.globalActions = [
            Button(SPR_MOVES[teamID], self.font, "Advance"),
            Button(SPR_MOVES[2], self.font, "Hold"),
            Button(SPR_MOVES[(teamID*-1)+1], self.font, "Retreat")
        ]
        for b in self.globalActions:
            b.width = 36
            b.height = 36

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 110, 112, 32), self.back)
        pygame.draw.rect(screen, (112, 120, 135, 32), self.back, width = 1)
        i = 0
        if self.teamID == 0:
            dir = -1
            i = screen.get_width() - 48
        if self.teamID == 1:
            dir = 1
            i = screen.get_width() - 160
        for b in self.globalActions:
            b.x = i
            b.y = screen.get_height()*2/3 + 8
            b.draw(screen)
            i += dir * 56


