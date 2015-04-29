__author__ = 'Wild_Doogy'

from threading import Thread
import socket

import Scanner


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
        self.socket_start(self.socket, ("localhost", 9091))
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
        my_socket.listen(5)

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
                    print "Got data", data
                except:
                    break
                if data:
                    result = self.scanner.directory_database.get_folders("%" + data + "%")
                    data_to_send = ""
                    for i in result:
                        data_to_send += i[0] +"\\" +  i[1] + "\n"
                    client.send(data_to_send)


if __name__ == '__main__':
    version = "2.0.0"
    F = FindIt(version)
    F.start()

