__author__ = 'boh01'

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 9091))
s.send("18560")
print s.recv(10000000)
s.close()