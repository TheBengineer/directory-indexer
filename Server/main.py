__author__ = 'Wild_Doogy'

from threading import Thread
import socket
import time

import Scanner
import SearchServer

def log(*args):
    print "[Main]",
    print time.strftime("%c"),
    print " ",
    for arg in args:
        print arg,
    print ""



class FindIt(Thread):
    def __init__(self, version):
        """

        :return:
        """
        Thread.__init__(self)
        self.version = version

        self.go = True
        self.clients = {}
        self.scanner = Scanner.Scanner()
        self.scanner.start()
        self.search_server = SearchServer.SearchServer(self.scanner)
        self.search_server.start()


    def run(self):
        while self.go:
            time.sleep(1)


if __name__ == '__main__':
    version = "2.0.0"
    F = FindIt(version)
    F.scanner.scan_dir("/media/M/")
    F.start()



