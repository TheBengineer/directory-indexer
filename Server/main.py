__author__ = 'Wild_Doogy'

from threading import Thread
import time
import sys

import Scanner
import SearchServer
import LogServer


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
        self.log_server = LogServer.LogServer(self.scanner)
        self.log_server.start()

    def run(self):
        while self.go:
            command = raw_input()
            if command.upper() == "Q":
                self.scanner.go = False
            elif command.upper() == "X":
                import os

                os._exit(1)
            elif command.upper()[0] == "$":
                try:
                    result = eval(command[1:])
                    log(command[1:], "$", result)
                except(RuntimeError, TypeError, NameError):
                    log((RuntimeError, TypeError, NameError))
            elif command.upper()[0] == "#":
                try:
                    exec command[1:]
                except(RuntimeError, TypeError, NameError):
                    log((RuntimeError, TypeError, NameError))


if __name__ == '__main__':
    version = "2.0.0"
    F = FindIt(version)
    if sys.platform == "linux2":
        F.scanner.add_to_roots("/media/O/")
        F.scanner.add_to_roots("/media/M/")
        F.scanner.add_to_roots("/media/K/")
    elif sys.platform == "win32":
        F.scanner.add_to_roots("O:\\")
        F.scanner.add_to_roots("M:\\")
        F.scanner.add_to_roots("K:\\")
    F.start()
