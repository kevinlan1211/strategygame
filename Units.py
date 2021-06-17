import pygame, math, glob

#KEY_UP = [pygame.K_w, pygame.K_UP]
#KEY_DOWN = [pygame.K_s, pygame.K_DOWN]
#KEY_LEFT = [pygame.K_a, pygame.K_LEFT]
#KEY_RIGHT = [pygame.K_d, pygame.K_RIGHT]
KEY_UP = 26
KEY_DOWN = 22
KEY_LEFT = 4
KEY_RIGHT = 7
def getDist(u1, u2):
    x1, y1 = u1.getPos()
    x2, y2 = u2.getPos()
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

def loadSprite(filename):
    pathname = "Images\\" + filename + "*"
    resultPaths = sorted(glob.glob(pathname))
    return [pygame.image.load(p) for p in resultPaths]
# usage example: loadSprite("Character\\bWalk")

def flipSprites(spr, horizontal, vertical):
    spRI = tuple(spr)
    return [pygame.transform.flip(s, horizontal, vertical) for s in spRI]

#sprite naming convention - SPR_BIR, SPR_BIL, SPR_BWR
SPR_BIR = loadSprite("Character\\bIdle")
SPR_BIL = flipSprites(SPR_BIR)
SPR_BWR = loadSprite("Character\\bWalk")
SPR_BWL = flipSprites(SPR_BWR)
SPR_BAR = loadSprite("Character\\bShoot")
SPR_BAL = flipSprites(SPR_BAR)

SPR_B2IR = loadSprite("Character\\b2Idle")
SPR_B2IL = flipSprites(SPR_B2IR)
SPR_B2WR = loadSprite("Character\\b2Walk")
SPR_B2WL = flipSprites(SPR_B2WR)
SPR_B2AR = loadSprite("Character\\b2Slash")
SPR_B2AL = flipSprites(SPR_B2AR)

SPR_RIR = loadSprite("Character\\rIdle")
SPR_RIL = flipSprites(SPR_RIR)
SPR_RWR = loadSprite("Character\\rWalk")
SPR_RWL = flipSprites(SPR_RWR)
SPR_RAR = loadSprite("Character\\rAttack")
SPR_RAL = flipSprites(SPR_RAR)

SPR_R2IR = loadSprite("Character\\r2Idle")
SPR_R2IL = flipSprites(SPR_R2IR)
SPR_R2WR = loadSprite("Character\\r2Walk")
SPR_R2WL = flipSprites(SPR_R2WR)
SPR_R2AR = loadSprite("Character\\r2Slash")
SPR_R2AL = flipSprites(SPR_R2AR)

SPR_BASE = loadSprite("Building\\Base")
# game res - 800 x 450
# playable space: 128 - 672

class Unit:
    def __init__(self, unitID, teamID, x, y, healthMod, damageMod, moveSpeedMod, rangeMod, attackSpeedMod):
        self.teamID = teamID
        self.x = x
        self.y = y
        self.healthMod = healthMod
        self.damageMod = damageMod
        self.moveSpeedMod = moveSpeedMod
        self.rangeMod = rangeMod
        self.attackSpeedMod = attackSpeedMod
        self.target = None
        self.aggroTarget = None
        self.selected = False
        self.disableFrames = 0
        self.moving = 0
        self.time = 0
        self.aggroRange = 100
        self.range = 0
        self.sprite = []
        self.spriteMoving = []
        self.spriteIdle = []
        self.spriteAttack = []
        self.imageIndex = 0
        self.animInterval = 5
        self.defaultInterval = 3 /self.moveSpeedMod
        self.defaultAttackInterval = 5 / self.attackSpeedMod
        self.attackRecovery = 0
        self.hasShadow = True
        self.cornerX = 0
        self.cornerY = 0
        self.unitID = unitID
        self.unitType = "Unit"
        print(self.unitID)
        self.moveState = 0
        if teamID == 0:
            self.direction = [1, 0]
            #self.defaultDirection = [1, 0]
        else:
            self.direction = [-1, 0]
            #self.defaultDirection = [-1, 0]
        self.updateSprites()

    def interface(self):
        return self.spriteIdle[0]

    def draw(self, screen):
        self.cornerX = self.x - self.sprite[0].get_rect().center[0]
        self.cornerY = self.y - self.sprite[0].get_rect().center[1]
        if self.hasShadow:
            pygame.draw.ellipse(screen, (60,60,60), (self.cornerX + 10, self.cornerY + 22, 16, 4))
            #pygame.draw.ellipse(screen, (210, 200, 168), (self.cornerX+6, self.cornerY+21, 24, 5), width = 1)
        if self.health < self.maxHealth:
            pygame.draw.rect(screen, (40, 42, 50), (self.cornerX+6, self.cornerY - 12, 24, 1))
            pygame.draw.rect(screen, (80, 220, 64), (self.cornerX+6, self.cornerY - 12, (self.health / self.maxHealth) * 24, 1))
        screen.blit(self.sprite[self.imageIndex], (self.cornerX, self.cornerY))


    def getPos(self):
        return self.x, self.y

    def tooClose(self, u):
        return getDist(self, u) <= self.range/1.5

    def inRange(self, u):
        return getDist(self, u) <= self.range

    def inAggroRange(self, u):
        return getDist(self, u) <= self.aggroRange

    def updateTarget(self, unitList):

        if not self.target or not self.inRange(self.target) or self.target.health <= 0:
            inRangeUnits = [u for u in unitList if self.inRange(u)]
            if not inRangeUnits == []:
                self.target = inRangeUnits[0]
            else:
                self.target = None
                self.updateDirection()

        if self.target:
            self.aggroTarget = None
        else:
            if not self.aggroTarget or not (self.inRange(self.aggroTarget) and not self.tooClose(self.aggroTarget)) or self.aggroTarget.health <= 0:
                inRangeUnits = [u for u in unitList if self.inAggroRange(u)]
                if not inRangeUnits == []:
                    self.aggroTarget = inRangeUnits[0]
                else:
                    self.aggroTarget = None
                    self.updateDirection()

    def animate(self):
        if self.animInterval > 0:
            self.animInterval -= 1
        else:
            self.imageIndex += 1
            if self.imageIndex >= len(self.sprite):
                self.animationEnd()
            if self.sprite == self.spriteMoving:
                self.animInterval = self.defaultInterval
            elif self.sprite == self.spriteAttack:
                self.animInterval = self.defaultAttackInterval

    def updateDirection(self):
        # 0 is forward, 1 is hold, 2 is retreat
        if self.moveState == 0:
            if self.teamID == 0:
                self.direction = [1, 0]
            else:
                self.direction = [-1, 0]
        elif self.moveState == 1:
            self.direction = [0, 0]
        elif self.moveState == 2:
            if self.teamID == 0:
                self.direction = [-1, 0]
            else:
                self.direction = [1, 0]




    def move(self):
        if not self.selected and self.aggroTarget:
            self.aggroMove()
        else:
            mag = math.sqrt(self.direction[0] * self.direction[0] + self.direction[1] * self.direction[1])
            if mag != 0:
                self.x += self.moveSpeed * self.direction[0] / mag
                self.y += self.moveSpeed * self.direction[1] / mag
                self.updateSprites()
                self.sprite = self.spriteMoving
                if self.imageIndex >= len(self.sprite):
                    self.animationEnd()
            else:
                self.updateSprites()
                self.sprite = self.spriteIdle
                if self.imageIndex >= len(self.sprite):
                    self.animationEnd()



    def aggroMove(self):
        self.direction = [self.aggroTarget.x - self.x, self.aggroTarget.y - self.y]
        mag = math.sqrt(self.direction[0] * self.direction[0] + self.direction[1] * self.direction[1])
        if mag != 0:
            self.x += self.moveSpeed * self.direction[0] / mag
            self.y += self.moveSpeed * self.direction[1] / mag
            self.updateSprites()
            self.sprite = self.spriteMoving
        else:
            self.updateSprites()
            self.sprite = self.spriteIdle

    def takeDamage(self, damage):
        self.health -= damage

    def checkAttackReady(self):
        return self.time == 0


    def attack(self):
        self.updateSprites()
        self.time += 1
        self.target.takeDamage(self.damage)
        self.imageIndex = 0
        self.animInterval = self.defaultAttackInterval
        self.sprite = self.spriteAttack
        self.disableFrames = self.defaultAttackInterval * len(self.sprite) + self.attackRecovery

    def aiAction(self):
        xPrevious = self.x
        yPrevious = self.y

        if self.time != 0:
            self.time += 1
            self.time = self.time % self.attackSpeed

        if self.disableFrames > 0:
            self.disableFrames -= 1
        else:
            self.updateSprites()
            if self.target:
                if self.checkAttackReady():
                    self.attack()
                else:
                    self.imageIndex = 0
                    self.sprite = self.spriteIdle
            else:
                self.move()
        self.animate()


    def playerAction(self, keys):
        if self.time != 0:
            self.time += 1
            self.time = self.time % self.attackSpeed

        moving = 0
        self.moveState = 1
        self.direction = [0,0]

        if self.disableFrames > 0:
            self.disableFrames -= 1
        else:
            # keys = pygame.key.get_pressed()
            if keys[KEY_RIGHT]:
                self.direction[0] = 1
                self.updateSprites()
                moving = 1
            elif keys[KEY_LEFT]:
                self.direction[0] = -1
                self.updateSprites()
                moving = 1

            if keys[KEY_UP]:
                self.direction[1] = -1
                self.updateSprites()
                moving = 1
            elif keys[KEY_DOWN]:
                self.direction[1] = 1
                self.updateSprites()
                moving = 1

            if moving == 0:
                self.updateSprites()
                if self.target:
                    if self.checkAttackReady():
                        self.attack()
                    else:
                        self.imageIndex = 0
                        self.sprite = self.spriteIdle
                else:
                    self.imageIndex = 0
                    self.sprite = self.spriteIdle
            else:
                self.move()

        self.animate()

    def animationEnd(self):
        if self.sprite == self.spriteMoving:
            self.imageIndex = 0
            self.animInterval = self.defaultInterval
        elif self.sprite == self.spriteIdle:
            self.imageIndex = 0
            self.animInterval = self.defaultInterval
        else:
            self.animInterval = self.defaultAttackInterval
            self.imageIndex = len(self.sprite) - 1


class Base(Unit):
    def __init__(self, unitID, teamID, x, y, healthMod = 1, damageMod = 1, moveSpeedMod = 1, rangeMod = 1, attackSpeedMod = 1):
        super().__init__(unitID, teamID, x, y, 1, 1, 1, 1, 1)
        self.health = 2000
        self.maxHealth = 2000
        self.unitType = "Base"
        self.sprite = SPR_BASE
        self.x += 24

    def updateSprites(self, x=-1):
        pass

    def aiAction(self):
        self.animate()

    def animate(self):
        if self.animInterval > 0:
            self.animInterval -= 1
        else:
            self.animInterval = self.defaultInterval
            self.imageIndex += 1
            if self.imageIndex >= len(self.sprite):
                self.imageIndex = 0

class Grunt(Unit):
    def __init__(self,unitID, teamID, x, y, healthMod = 1, damageMod = 1, moveSpeedMod = 1, rangeMod = 1, attackSpeedMod = 1):
        super().__init__(unitID, teamID, x, y, healthMod, damageMod, moveSpeedMod, rangeMod, attackSpeedMod)
        self.health = 100 * self.healthMod
        self.maxHealth = self.health
        self.damage = 18 * self.damageMod
        self.range = 90 * self.rangeMod
        self.aggroRange = self.range*1.5
        self.moveSpeed = 1 * self.moveSpeedMod
        self.attackSpeed = 100 / self.attackSpeedMod
        self.attackDelay = 4

        self.unitType = "Grunt"


    def updateSprites(self, targetX=-1):
        disabled = False
        if self.target and targetX == -1:
            targetX = self.target.x
        elif targetX == -1 and not self.target:
            disabled = True

        if self.direction[0] > 0:
            if self.teamID == 0:
                self.spriteMoving = SPR_BWR
                self.spriteIdle = SPR_BIR
            else:
                self.spriteMoving = SPR_RWR
                self.spriteIdle = SPR_RIR
        elif self.direction[0] < 0:
            if self.teamID == 0:
                self.spriteMoving = SPR_BWL
                self.spriteIdle = SPR_BIL
            else:
                self.spriteMoving = SPR_RWL
                self.spriteIdle = SPR_RIL

        if not disabled:
            if targetX > self.x:
                if self.teamID == 0:
                    self.spriteAttack = SPR_BAR
                else:
                    self.spriteAttack = SPR_RAR
            else:
                if self.teamID == 0:
                    self.spriteAttack = SPR_BAL
                else:
                    self.spriteAttack = SPR_RAL

    def aiAction(self):
        super().aiAction()


class Sword(Unit):
    def __init__(self, unitID, teamID, x, y, healthMod = 1, damageMod = 1, moveSpeedMod = 1, rangeMod = 1, attackSpeedMod = 1):
        super().__init__(unitID, teamID, x, y, healthMod, damageMod, moveSpeedMod, rangeMod, attackSpeedMod)
        self.health = 90 * self.healthMod
        self.maxHealth = self.health
        self.damage = 20 * self.damageMod
        self.range = 24 * self.rangeMod
        self.aggroRange = self.range * 6
        self.moveSpeed = 1 * self.moveSpeedMod
        self.attackSpeed = 80 / self.attackSpeedMod
        self.unitType = "Sword"

    def updateSprites(self, targetX = -1):
        disabled = False
        if self.target and targetX == -1:
            targetX = self.target.x
        elif targetX == -1 and not self.target:
            disabled = True

        if self.direction[0] > 0:
            if self.teamID == 0:
                self.spriteMoving = SPR_B2WR
                self.spriteIdle = SPR_B2IR
            else:
                self.spriteMoving = SPR_R2WR
                self.spriteIdle = SPR_R2IR
        elif self.direction[0] < 0:
            if self.teamID == 0:
                self.spriteMoving = SPR_B2WL
                self.spriteIdle = SPR_B2IL
            else:
                self.spriteMoving = SPR_R2WL
                self.spriteIdle = SPR_R2IL

        if not disabled:
            if targetX > self.x:
                if self.teamID == 0:
                    self.spriteAttack = SPR_B2AR
                else:
                    self.spriteAttack = SPR_R2AR
            else:
                if self.teamID == 0:
                    self.spriteAttack = SPR_B2AL
                else:
                    self.spriteAttack = SPR_R2AL

    def aiAction(self):
        super().aiAction()

