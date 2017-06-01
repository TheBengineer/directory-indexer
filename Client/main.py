__author__ = 'Wild_Doogy'

import GUI
import Scanner

if __name__ == '__main__':
    version = "3.0.0"
    localScan = Scanner.Scanner()
    localScan.load_roots()
    localScan.start()
    gui = GUI.Window(localScan.directory_database)
    gui.version = version
    gui.start()
