__author__ = 'boh01'

import socket

go = True
while go:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("10.196.112.99", 9091))
    msg = raw_input()
    if msg == "q":
        g = 0
    s.send(msg)
    print s.recv(10000000)
    s.close()