import Units, pygame, math, sys, json, InputProcessor, Interface, Buildings, Client
from Units import Grunt, Sword
from Network import Network

RES = [(800, 450), (960, 540), (1600, 900)]
COL_BG = (132, 112, 103)


c = Client(2, False)
c.startGame()
