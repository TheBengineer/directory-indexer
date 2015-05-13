__author__ = 'Wild_Doogy'

from threading import Thread
import socket
import time

import Scanner


def log(*args):
    print "[Main]",
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


class FindIt(Thread):
    def __init__(self, version):
        """

        :return:
        """
        Thread.__init__(self)
        self.version = version
        self.socket = self.socket_init()
        """
        :type self.socket: socket.socket
        """
        self.socket_start(self.socket, (getlocalip(), 9091))
        self.go = True
        self.clients = {}
        self.scanner = Scanner.Scanner()
        self.scanner.start()


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
            client, address = self.socket_accept(self.socket)
            data = ""
            while 1:
                try:
                    data = client.recv(10000)
                    if not data:
                        break
                    log("From ", address, " Got data ", data)
                except:
                    break
                if data:
                    result = self.scanner.directory_database.get_folders_500("%" + data + "%")
                    data_to_send = ""
                    i = 0
                    for i, r in enumerate(result):
                        if i > 510:
                            log("Too many results for search term", data)
                            data_to_send += "Displaying only first 500 results\n"
                            break
                        data_to_send += r[0] + "\\" + r[1] + "\n"
                    log("Sending ", i, "Results to ", address)
                    client.send(data_to_send)
                    client.close()
                else:
                    client.send("No results")


if __name__ == '__main__':
    version = "2.0.0"
    F = FindIt(version)
    F.scanner.scan_dir("/media/M/")
    F.start()



