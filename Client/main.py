__author__ = 'Wild_Doogy'

import GUI
import Scanner


if __name__ == '__main__':
    version = "2.0.1"
    localScan = Scanner.Scanner()
    localScan.start()
    gui = GUI.Window()
    gui.version = version
    gui.start()

