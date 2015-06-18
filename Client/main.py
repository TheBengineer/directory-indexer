__author__ = 'Wild_Doogy'

import GUI
import Scanner

if __name__ == '__main__':
    version = "2.1.0"
    localScan = Scanner.Scanner()
    localScan.add_to_roots("H:\\")
    localScan.start()
    gui = GUI.Window(localScan.directory_database)
    gui.version = version
    gui.start()
