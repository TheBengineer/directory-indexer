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
            elif command.upper() == "S":
                scanner_attributes = [a for a in dir(self.scanner) if not a.startswith('_')]
                DB_attributes = [a for a in dir(self.scanner.directory_database) if not a.startswith('_')]
                #log("Scanner variables", scanner_attributes)
                #log("Scanner variables", type(scanner_attributes[1]))
                #log("DB variables", DB_attributes)
                message = ""
                for attribute in scanner_attributes:
                    try:
                        real_attribute = getattr(self.scanner, attribute)
                    except AttributeError as e:
                        log(e)
                        break
                    try:
                        max = 5
                        if type(real_attribute) == str:
                            max = 100
                        if len(real_attribute) > max:
                            message += "\tLen of {0}:{1}\n".format(attribute, len(real_attribute))
                        else:
                            message += "\t{0}:{1}\n".format(attribute, str(real_attribute))
                    except Exception as e:
                        pass
                        #log("Error:", e)
                message += "DB Status:\n"
                for attribute in DB_attributes:
                    try:
                        real_attribute = getattr(self.scanner.directory_database, attribute)
                    except AttributeError:
                        break
                    try:
                        max = 5
                        if type(real_attribute) == str:
                            max = 100
                        if len(real_attribute) > max:
                            message += "\tLen of {0}:{1}\n".format(attribute, len(real_attribute))
                        else:
                            message += "\t{0}:{1}\n".format(attribute, str(real_attribute))
                    except Exception as e:
                        pass
                        #log("Error:", e)
                log("Scanner Status:\n", message)
            elif len(command):
                if command.upper()[0] == "$":
                    try:
                        result = eval(command[1:])
                        log(command[1:], "$", result)
                    except:
                        log(sys.exc_info())
                elif command.upper()[0] == "#":
                    try:
                        exec command[1:]
                    except:
                        log(sys.exc_info())


if __name__ == '__main__':
    version = "2.0.0"
    F = FindIt(version)
    if sys.platform == "linux2":
        F.scanner.add_to_roots("/media/I/")
        F.scanner.add_to_roots("/media/K/")
        F.scanner.add_to_roots("/media/N/")
        F.scanner.add_to_roots("/media/O/")
        #F.scanner.add_to_roots("/media/W/")
        F.scanner.add_to_roots("/media/M/")
    elif sys.platform == "win32":
        F.scanner.add_to_roots("I:\\")
        F.scanner.add_to_roots("K:\\")
        F.scanner.add_to_roots("N:\\")
        F.scanner.add_to_roots("O:\\")
        #F.scanner.add_to_roots("W:\\")
        F.scanner.add_to_roots("M:\\")
    F.start()
    s = F.scanner
    d = s.directory_database

