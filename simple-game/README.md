README

Concept
---
User plays an unwinnable game
The only way to win is to MITM the packets being sent to the server and modify them to outside of a boundary

Game should be a simple get the golden egg, but they are stuck in a box of x y dimensions and the egg is outside
They will have to decode the packets to determine how the movement is sent to the server and then manipulate it
to get the flag

TODO:
Create game
-Create board
-Have character able to move within board, server will be sent movement
-have character interact with objects, e.g. pick up an apple etc

Server will send responses to client on where to move in the array
clientside will not have flag.

server should only be accessible via ip port
client should be compiled