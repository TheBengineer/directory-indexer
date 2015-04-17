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


    # FolderToScan = "M:\\Drawings" # CHANGE this to whatever you want to. Just remember to use double slashes
    FolderToScan = "M:\\Projects"
    #FolderToScan = "C:\\tmp"
    db_folder = "C:\\Projects"  # os.getcwd()
    db_file = "DB.csv"  # Will be placed next to the python file. Probably best to not run from network drive.
    DB_path = "C:\\tmp\\Monster-Projects.db"
    last_update_date = 0.0 # datetime.datetime(1990, 1, 1)







    """ :type DirectoryDictionary: dict of Directory"""
    DirectoryDictionary[FolderToScan] = Directory(FolderToScan, last_update_date, DirectoryDictionary)
    # Above plants a seed at the base of the folder tree. Any folders created before the date will not be scanned

    importOldScanFromDB(DB, DirectoryDictionary)  # populate memory with already scanned files.
    DirectoryDictionary[FolderToScan].timeUpdated = 0.0 # Reset time for root.

    update_pool.apply_async(DirectoryDictionary[FolderToScan].update, args=(update_pool, DB,))  # Go. Scan. Be Free.
    time.sleep(.3)
    while update_pool.thread_count > 0:
        while not update_pool.messages.empty():
            print update_pool.messages.get()
        time.sleep(.1)
    print "No threads left, printing trailing messages"
    while not update_pool.messages.empty():
        print update_pool.messages.get()

    update_pool.close()
    update_pool.join()


    DB.go = 0
    print DB.get_folders("%QSA80%")
    #raw_input("Completed in " + str((time.time() - startTime) / 60) + " Minutes")
