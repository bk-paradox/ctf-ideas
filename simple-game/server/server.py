import socket
import struct
import sys
import os
from time import sleep
from threading import Thread

class objects(object):
    WALL = '#'
    PLAYER = '$'
    GOLDEN_EGG = '@'

class packets(object):
    MOVE = 0x676d
    INIT = 0x1337
    QUIT = 0xDEAD
    NOOP = 0x9090
    GEGG = 0x2020

board = []
size = 24
for i in range(size):
    row = []
    for j in range(size):
        row.append('.')
    board.append(row)
for i in range(size/2):
    board[0][i] = objects.WALL
    board[i][0] = objects.WALL
    board[size/2][i] = objects.WALL
    board[i][size/2] = objects.WALL
board[size/2][size/2] = objects.WALL

offset = size-1
for i in range(offset/4):
    board[offset][offset-i] = objects.WALL
    board[offset-i][offset] = objects.WALL
    board[offset-i][(offset-(offset/4))] = objects.WALL
    board[(offset-(offset/4))][offset-i] = objects.WALL
board[offset-(offset/4)][offset-(offset/4)] = objects.WALL
board[offset-(offset/6)][offset-(offset/6)] = objects.GOLDEN_EGG
egg_position = (offset-offset/6, offset-offset/6)


def noop(data):
    #print "[nop] do something"
    return struct.pack(">H", packets.NOOP)

def golden_egg():
    #print "[golden_egg] do something"
    flag = "flag{You've got the power!!!!}"
    return struct.pack(">HI30s", packets.GEGG, 30, flag)

def move(data):
    #print "[move] do something"
    x ,y = struct.unpack(">II", data)
    if x == 20 and y == 20:
        return golden_egg()
    elif x >= 24 or x <= 0 or y >=24 or y <=0 or board[x][y] == "#":
        return struct.pack(">HII", packets.NOOP, 1, 1) 
    else:
        return struct.pack(">HII", packets.MOVE, x, y)

def quit(data):
    #print "[quitting]"
    game.running = False
    try:
        os._exit(data)
    except:
        os._exit(struct.unpack(">i", data[0:4])[0])


def init(data):
    #print "[init] Let client know they are good to go."
    return struct.pack(">H", packets.INIT)

handlers = {
    packets.MOVE: move,
    packets.INIT: init,
    packets.NOOP: noop,
    packets.QUIT: quit
}

class GameServer(Thread):
    def __init__(self, host, port):
        super(GameServer, self).__init__()
        #Socket connection unkown yet
        self.running = True
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host,port))
        sock.listen(1)
        #waiting for connection
        self.game, self.addr = sock.accept()
        print "Recieved connection from {}".format(self.addr)

    def run(self):
        while self.running == True:
            try:
                data = self.game.recv(4096)
                print "[({})] {}".format(self.addr, data[:100].encode('hex'))
                if len(data)>=2:
                        packet_id = struct.unpack(">H", data[0:2])[0]
                        if packet_id == packets.QUIT:
                            quit(1)
                            break
                        if packet_id not in handlers:
                            self.game.send(struct.pack(">H", packets.NOOP))
                        else:
                            data = handlers.get(packet_id, noop)(data[2:])
                            self.game.send(data)
            except socket.error as e:
                print "Something went a foul", e
                quit(-1)
                break
            if not data:
                quit(-1)
                break

if __name__=='__main__':
    if len(sys.argv) > 2:
        host = str(sys.argv[1])
        port = int(sys.argv[2])
    else:
        host = '127.0.0.1'
        port = 3333
        
    game = GameServer(host, port)
    game.start()

    while True:
        try:
            cmd = raw_input('$ ')
            if cmd[:4] == 'quit':
                quit(-1)
        except Exception as e:
            print e