__author__ = 'boh01'

from threading import Thread

# Needed for scanning
from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock
import Queue

# Needed for backup
import datetime, shutil

import os, time

import DirectoryDB
import Directory


class Scanner(Thread):
    def __init__(self):
        Thread.__init__(self)
        """ :type self.directory_dictionary: dict of Directory.Directory"""
        self.directory_dictionary = {}
        self.directory_database = self.init_database()
        self.start_time = time.time()

        self.number_of_threads = 16
        self.update_pool = ThreadPool(self.number_of_threads)
        self.update_pool.thread_count = 0
        self.update_pool.thread_lock = Lock()
        self.update_pool.messages = Queue.Queue()

        self.importOldScanFromDB(self.directory_database, self.directory_dictionary)

        self.go = 1


    def init_database(self):
        FindIt = self.create_FindIt_folder()
        if not FindIt:
            print "Could not create the FindIt directory. Will now crash."
            quit()
        database_filename = os.path.join(FindIt, "FindIt.db")
        self.backup_db(database_filename)
        directory_database = DirectoryDB.DirectoryDB(database_filename)
        directory_database.start()
        return directory_database


    def create_FindIt_folder(self):
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

    def run(self):
        while self.go:
            while self.update_pool.thread_count > 0:
                while not self.update_pool.messages.empty():
                    print self.update_pool.messages.get()
                time.sleep(.1)
            while not self.update_pool.messages.empty():
                print self.update_pool.messages.get()
            time.sleep(.1)  # Poll
        self.update_pool.close()
        self.update_pool.join()
        self.directory_database.go = 0

    def scan_dir(self, folder_to_scan):
        if not os.path.isdir(folder_to_scan):  # Make sure the folder exists
            print "Cannot access the folder to be scanned:", folder_to_scan
        else:
            self.directory_dictionary[folder_to_scan] = Directory.Directory(folder_to_scan, 0.0,
                                                                            self.directory_dictionary)  # Create Root and reset time.
            self.update_pool.apply_async(self.directory_dictionary[folder_to_scan].update,
                                         args=(self.update_pool, self.directory_database,))  # Go. Scan. Be Free.

    def backup_db(self, pathToDB):
        try:
            nm = pathToDB + str(datetime.datetime.now()).replace(":", "-") + ".backup"
            print nm
            if os.path.isfile(pathToDB):
                shutil.copy(pathToDB, nm)  # Move old database to a backup location
                print "Output file backed up."
        except ValueError:
            print "Output file not backed up. File may not exist, permissions, etc. This might be a problem later"


    def importOldScanFromDB(self, DB, tmpDirectoryDictionary):
        """
        Used to import from a sqlite file generated from the last scan.
        :param DB: The path to the .csv file
        :type DB: DirectoryDB.DirectoryDB
        :param tmpDirectoryDictionary: A dictionary to hold all the imported Directory classes
        :type tmpDirectoryDictionary: dict of Directory.Directory
        :return: Does not return anything.
        """
        print "Attempting to import old Database from", DB.file_path
        data = DB.dump()
        for f in data:
            path = f[0].strip("\"")
            mfile = f[1].strip("\"")
            s_time = 0.0
            if f[2]:
                s_time = f[2]
            if path not in tmpDirectoryDictionary:
                tmpDirectoryDictionary[path] = Directory.Directory(path, s_time, tmpDirectoryDictionary)
                tmpDirectoryDictionary[path].files.append(mfile)
            else:
                tmpDirectoryDictionary[path].files.append(mfile)
        print "Done Importing"

