import socket, sys, json, Game
import traceback
from _thread import *
import threading
import time

serverIP = "localhost"
port = 5555
started = False
packetSize = 4
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
testDict = {"wemis": 9, "teapot": 7}
inputData = {}
def jEncode(dict):
    #turns into json formatted string
    return json.dumps(dict)

def jDecode(string):
    #turns formatted string into dict
    return json.loads(string)


def startServer():
    started = True
    try:
        s.bind((serverIP, port))

    except socket.error as e:
        str(e)

    s.listen(2)
    print("Server started, waiting for a connection")

def threaded_client(conn, game, player):
    #sendDict = game.getData()
    #print(sendDict)
    global locks
    global mutex
    conn.send(str.encode(str(player)))
    print("team id sent! ", player)
    reply = ""
    while started:
        #locks[player].acquire()
        mutex.acquire()
        try:
            # receives input/selection data from the client
            # data = jDecode(conn.recv(1024*packetSize).decode())

            toReceive = True
            recDat = ""
            while toReceive:
                incooming = conn.recv(1024*packetSize).decode()
                recDat += incooming
                if len(incooming)>0:
                    if incooming[-1] == "*":
                        toReceive = False
                    else:
                        print("didnt receive all")
                else:
                    print("no data received!")
                    break
            recDat = recDat[:-1]
            # recDat = conn.recv(1024*packetSize).decode()
            #print(recDat)
            data = jDecode(recDat)
            keys = data['keys']
            selections = data['selections']
            buildings = data['buildings']
            units = data['units']
            state = data['moveState']
            #buildings = [1,1,1,1,1,1,1]

            for u in game.unitList[player]:
                if u.unitID in selections:
                    u.selected = True
                else:
                    u.selected = False
            if not data:
                print("Disconnected")
                break
            else:
                #print("Received: ", data['signature'])
                #print("Sending: ", [k for k in sendDict])
                game.receive(keys, player, buildings, units, state)
                sendDict = game.getData(player)
                reply = jEncode(sendDict)
                conn.sendall(str.encode(reply))
        except:
            traceback.print_exc()
            break

        #if locks[(player-1)*(-1)].locked():
            #locks[(player-1)*(-1)].release()
        mutex.release()
        time.sleep(.01)

    print("Connection lost.")
    conn.close()

def gameLoop(g):
    while started:
        g.runGame()

startServer()
started = True
g = Game.Game(2)
g.startGame()
start_new_thread(gameLoop, (g,))
player = 0
locks = [allocate_lock(), allocate_lock()]
mutex = allocate_lock()
while started:
    conn, address = s.accept()
    print("connected to", address)

    start_new_thread(threaded_client, (conn, g, player))
    player += 1