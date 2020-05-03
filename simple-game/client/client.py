from threading import Thread
import struct
import socket
import os
import sys

class packets(object):
    MOVE = 0x676d
    INIT = 0x1337
    QUIT = 0xDEAD
    NOOP = 0x9090
    GEGG = 0x2020

class objects(object):
    WALL = '#'
    PLAYER = '$'
    GOLDEN_EGG = '@'

class PointlessGame:
    
    size = 0
    board = []
    hist = []

    def __init__(self, size):
        board = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.size = size
        self.running = True
        self.player_position = (1, 1)
        for i in range(size):
            row = []
            for j in range(size):
                row.append('.')
            self.board.append(row)
        x,y = self.player_position
        self.board[x][y] = objects.PLAYER
        for i in range(self.size/2):
            self.board[0][i] = objects.WALL
            self.board[i][0] = objects.WALL
            self.board[size/2][i] = objects.WALL
            self.board[i][size/2] = objects.WALL
        self.board[size/2][size/2] = objects.WALL

        offset = self.size-1
        for i in range(offset/4):
            self.board[offset][offset-i] = objects.WALL
            self.board[offset-i][offset] = objects.WALL
            self.board[offset-i][(offset-(offset/4))] = objects.WALL
            self.board[(offset-(offset/4))][offset-i] = objects.WALL
        self.board[offset-(offset/4)][offset-(offset/4)] = objects.WALL
        self.board[offset-(offset/6)][offset-(offset/6)] = objects.GOLDEN_EGG
        self.egg_position = (offset-offset/6, offset-offset/6)
    
    def connect(self, host, port):
        print "Attempting connection to ({}, {}).....".format(host,port),
        try:
            self.server.connect((host,port))
        except Exception as e:
            print "Something failed ", e
            quit(-1)
        self.server.send(struct.pack(">H", packets.INIT))
        temp = self.server.recv(4096)
        print temp.encode('hex')
        if struct.unpack(">H", temp)[0] == packets.INIT:
            print "Connection successfuly"
        else:
            print "Connection failed"
            self.quit()
    
    def quit(self):
        self.running = False
        self.server.send(struct.pack(">HI", packets.QUIT, 0))
        self.server.close()    

    def print_board (self):
        os.system('clear')
        print "Collect the golden egg '@' to get the flag"
        for i in self.board:
            print "  ".join(i)
    def golden_egg(self, data):
        print "[flag handler] Looks like you got the golden egg!"
        length = struct.unpack(">I", data[0:4])[0]
        print "The flag is ", data[4:length+4]
        self.quit()

    def move(self, xy):
        x,y = xy
        cur_x, cur_y = self.player_position
        print "[move handler] x = {} , y = {}".format(x,y)
        new_x, new_y = (cur_x+x, cur_y+y)
        print "[move handler] new_x = {} , new_y = {}".format(new_x,new_y)
        if new_x >= self.size or new_x <= 0 or new_y >=self.size or new_y <=0 or self.board[new_x][new_y] == "#":
            print "Can't go that way!" 
        else:
            self.player_position = (new_x, new_y)
            self.server.send(struct.pack('>HII', 0x676d, new_x, new_y))
            data = self.server.recv(100)
            if len(data)>=2:
                packet_id, x,y =  struct.unpack(">HII", data)
                if packet_id == packets.MOVE:
                    if x != cur_x or y != cur_y:                           
                        self.board[cur_x][cur_y] = '.'
                        self.board[x][y] = '$'
                        return True
                    else:
                        return False
                elif packet_id == packets.GEGG:
                    self.golden_egg(data[2:])

    def noop(self):
        print "I dont know what you are trying to do Dave!"
    
    def get_action(self):
        direction = {
            'w': (-1,0),
            'a': (0,-1),
            's': (1,0),
            'd': (0,1),
        }
        all_userinput = raw_input("w,a,s,d,q? >")
        for userinput in all_userinput:
            if userinput == 'q':
                self.quit()
            elif userinput in direction:
                self.move(direction[userinput])
            else:
                self.noop()
   
game = PointlessGame(24)
if len(sys.argv) > 2:
    host = str(sys.argv[1])
    port = int(sys.argv[2])
else:
    host = '127.0.0.1'
    port = 3333
game.connect(host,port)

while game.running == True:
    game.print_board()
    game.get_action()

print "Thank you for playing"
    
