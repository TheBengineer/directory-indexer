__author__ = 'Wild_Doogy'

import shutil
from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock

import Scanner
import GUI



if __name__ == '__main__':
    scanner = Scanner.Scanner()
    scanner.start()
    gui = GUI.Window()
    gui.start()

