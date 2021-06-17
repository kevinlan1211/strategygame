import socket
import traceback


packetSize = 4

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5555
        self.address = self.server, self.port
        self.data = self.connect()

    def getData(self):
        return self.data

    def connect(self):
        data = ""
        try:
            self.client.connect(self.address)
            data = self.client.recv(1024*packetSize).decode()
        except:
            traceback.print_exc()
        return data

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            self.data = self.client.recv(1024*packetSize).decode()
        except socket.error as e:
            print(e)
