#!/usr/bin/python
from builder import Builder
import socket
from sys import exit

f = open("dhcp/discover.pkt")
s = f.read()

b = Builder(s)

if b.is_correct() is not True:
    print("Msg is NOT correct")
    exit()
else:
    print("Msg is correct")

raw = b.get_raw()

SERVER_IP = "255.255.255.255"
SERVER_PORT = 67
CLIENT_PORT = 68

server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_sock.sendto(raw, (SERVER_IP, SERVER_PORT))

data, addr = client_sock.recvfrom(CLIENT_PORT)
print("I received something!")
