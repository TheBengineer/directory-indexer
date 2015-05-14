__author__ = 'boh01'

from threading import Thread
import time
import socket

import errno

def log(*args):
    print "[LogServer]",
    print time.strftime("%c"),
    print " ",
    for arg in args:
        print arg,
    print ""


def getlocalip():
    import os

    c4 = ""
    if os.sys.platform == "win32":
        back = os.popen("ipconfig /all")
        cmd = back.read(2000)
        cmd2 = cmd[cmd.find("IP Address"):cmd.find("IP Address") + 70]
        cmd3 = cmd2[cmd2.find(":") + 2:cmd2.find(":") + 19]
        c4 = cmd3[0:cmd3.find(" ") - 2]
    elif os.sys.platform == "linux2":
        back = os.popen("ifconfig")
        cmd = back.read(2000)
        cmd2 = cmd[cmd.find("Ethernet"):cmd.find("Ethernet") + 300]
        cmd3 = cmd2[cmd2.find("inet addr:") + 10:cmd2.find("inet addr:") + 50]
        c4 = cmd3[0:cmd3.find(" ")]
    if c4 != "":
        return c4
    else:
        return "localhost"


class LogServer(Thread):
    def __init__(self, scanner):
        Thread.__init__(self)
        self.scanner = scanner
        self.socket = self.socket_init()
        """
        :type self.socket: socket.socket
        """
        self.socket_start(self.socket, (getlocalip(), 9092))
        self.go = 1


    def socket_init(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def socket_start(self, my_socket, address):
        """

        :param my_socket: A socket object to start listening on
        :type my_socket: socket.socket
        :param address: The address to start listening on. Format: ("localhost", 80)
        :type address: tuple of (str, int)
        :return:
        """
        my_socket.bind(address)
        my_socket.listen(50)

    def socket_accept(self, my_socket):
        """

        :param my_socket: A socket to accept connections on
        :type my_socket: socket.socket
        :return:
        """
        return my_socket.accept()

    def run(self):
        while self.go:
            try:
                client, address = self.socket_accept(self.socket)
                data = ""
                while 1:
                    try:
                        data = client.recv(10000)
                    except:
                        break
                    if "log" in data:
                        log("From ", address, " Got request for log data ")
                        data_to_send = ""
                        i = 0
                        message_length = 0
                        for i, char in enumerate(self.scanner.log):
                            if message_length > 2500:
                                client.send(data_to_send)
                                data_to_send = ""
                                message_length = 0
                            data_to_send += char
                            message_length += 1
                        log("Sending ", i/1000000.0, "MB to ", address)
                        client.send(data_to_send)
                        client.send("")
                    else:
                        client.send("No results")
                        client.send("")
                    client.close()
            except socket.error, v:
                errorcode=v[0]
                if errorcode==errno.ECONNRESET:
                    print "Connection Reset"
