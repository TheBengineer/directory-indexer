__author__ = 'boh01'

from threading import Thread

# Needed for scanning
from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock
import Queue

import os, time
import datetime, shutil # Needed for backup

import DirectoryDB


class Scanner(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.directory_dictionary = {}
        self.init_db()
        self.start_time = time.time()

        self.number_of_threads = 16
        self.update_pool = ThreadPool(self.number_of_threads)
        self.update_pool.thread_count = 0
        self.update_pool.thread_lock = Lock()
        self.update_pool.messages = Queue.Queue()



    def init_db(self):
        FindIt = self.create_FindIt()
        if not FindIt:
            print "Could not create the FindIt directory. Will now crash."
            quit()
        database_filename = os.path.join(FindIt, "FindIt.db")
        self.backup_db(database_filename)
        self.directory_database = DirectoryDB.DirectoryDB(database_filename)
        self.directory_database.start()


    def create_FindIt(self):
        appdata = os.getenv('APPDATA')
        FindIt = os.path.join(appdata, "FindIt")
        if os.path.isdir(FindIt):
            print "Yes"
        else:
            os.mkdir(FindIt)
        if os.path.isdir(FindIt):
            return FindIt
        else:
            return False

    def load_preferences(self):
        # import csv
        # TODO need to create a config file
        pass


    def load_database(self):
        pass

    def run(self):
        pass

    def scan_dir(self, folder_to_scan):
        if not os.path.isdir(folder_to_scan):  # Make sure the folder exists
            print "Cannot access the folder to be scanned:", folder_to_scan
            raw_input("Press enter to exit")
            exit()
        else:
            pass

    def backup_db(self, pathToDB):
        try:
            nm = pathToDB + str(datetime.datetime.now()).replace(":", "-") + ".backup"
            print nm
            if os.path.isfile(pathToDB):
                shutil.copy(pathToDB, nm)  # Move old database to a backup location
                print "Output file backed up."
        except ValueError:
            print "Output file not backed up. File may not exist, permissions, etc. This might be a problem later"


a = Scanner()