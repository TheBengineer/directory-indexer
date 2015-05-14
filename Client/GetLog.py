__author__ = 'boh01'

from threading import Thread
import socket


def getlocalip():
    import os

    if os.sys.platform == "win32":
        back = os.popen("ipconfig /all")
        cmd = back.read(2000)
        cmd2 = cmd[cmd.find("IP Address"):cmd.find("IP Address") + 70]
        cmd3 = cmd2[cmd2.find(":") + 2:cmd2.find(":") + 19]
        c4 = cmd3[0:cmd3.find(" ") - 2]

    if os.sys.platform == "linux2":
        back = os.popen("ifconfig")
        cmd = back.read(2000)
        cmd2 = cmd[cmd.find("Ethernet"):cmd.find("Ethernet") + 300]
        cmd3 = cmd2[cmd2.find("inet addr:") + 10:cmd2.find("inet addr:") + 50]
        c4 = cmd3[0:cmd3.find(" ")]

    if c4 != "":
        return c4
    else:
        return "BOH001"


def getadd():
    local = getlocalip()
    host = raw_input("Type host, skip for " + str(local) + ":")
    if host == "":
        host = local
    port = raw_input("Type port, skip for 9092 :")
    if port:
        port = int(port)
    else:
        port = 9092
    address = (host, port)
    return address


def setup(address):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(address)
    return client


class ThreadClass(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        pass


def startclass():
    TClass = ThreadClass()
    TClass.start()
    return TClass


def mainprog(client):
    i = 0
    while 1:
        i += 1
        try:
            print "Asking for log"
            client.send("log")
            data = client.recv(20000000)
            print "got", len(data), "bytes of data"
            while data:
                print data
                data = client.recv(20000000)
        except:
            print "Socket closed. Reconnecting."
            break
        if data == "":
            break
        print data,


while 1:
    client = setup(("BOH001", 9092))
    raw_input("Enter to continue")
    mainprog(client)


