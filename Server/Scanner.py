__author__ = 'boh01'

from threading import Thread

# Needed for scanning
from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock
import Queue

# Needed for backup
import datetime, shutil

import os, time, sys

import DirectoryDB
import Directory


class Scanner(Thread):
    def __init__(self, GUI=None):
        Thread.__init__(self)
        """
        :type GUI: GUI.Window
        :return:
        """
        self.GUI = GUI

        self.directory_dictionary = {}
        self.directory_database = self.init_database()
        self.roots = []
        """ :type self.directory_dictionary: dict of Directory.Directory"""
        self.start_time = time.time()

        self.number_of_threads = 16
        self.update_pool = ThreadPool(self.number_of_threads)
        self.update_pool.thread_count = 0
        self.update_pool.thread_lock = Lock()
        self.update_pool.messages = Queue.Queue()

        self.go = 1
        self.log = ""
        self.last_update = time.time()
        self.update_interval = 10 # Seconds


    def init_database(self):
        FindIt = self.create_FindIt_folder()
        if not FindIt:
            print "Could not create the FindIt directory. Will now crash."
            quit()
        database_filename = os.path.join(FindIt, "FindIt.db")
        # self.backup_db(database_filename)
        directory_database = DirectoryDB.DirectoryDB(database_filename, self.GUI)
        directory_database.start()
        return directory_database


    def create_FindIt_folder(self):
        if sys.platform == "win32":
            appdata = os.getenv('APPDATA')
            FindIt = os.path.join(appdata, "FindIt")
            if not os.path.isdir(FindIt):
                os.mkdir(FindIt)
            if os.path.isdir(FindIt):
                return FindIt
            else:
                return False
        elif sys.platform == "linux2":
            home = os.getenv('HOME')
            FindIt = os.path.join(home, "FindIt")
            if not os.path.isdir(FindIt):
                os.mkdir(FindIt)
            if os.path.isdir(FindIt):
                return FindIt
            else:
                return False
        else:
            print "Crashing. Not made to run on mac"


    def load_preferences(self):
        # import csv
        # TODO need to create a config file
        pass

    def run(self):
        self.importOldScanFromDB(self.directory_database, self.directory_dictionary)
        while self.go:
            if self.update_pool.thread_count > 0:
                while self.update_pool.thread_count > 0:
                    while not self.update_pool.messages.empty():
                        self.log += self.update_pool.messages.get()
                    time.sleep(.1)
                while not self.update_pool.messages.empty():
                    self.log += self.update_pool.messages.get()
                if self.GUI:
                    self.GUI.set_status("Done Scanning.")
                else:
                    print "Done Scanning"
            time.sleep(.1)  # Poll
            if time.time() > self.last_update + self.update_interval:
                self.last_update = time.time()
                self.freshen()
        self.update_pool.close()
        self.update_pool.join()
        self.directory_database.go = 0

    def scan_dir(self, folder_to_scan):
        if not os.path.isdir(folder_to_scan):  # Make sure the folder exists
            print "Cannot access the folder to be scanned:", folder_to_scan
        else:
            print "adding path", folder_to_scan
            if folder_to_scan not in self.directory_dictionary:
                self.directory_dictionary[folder_to_scan] = Directory.Directory(folder_to_scan, 0.0,
                                                                                self.directory_dictionary)  # Create Root and reset time.
            self.update_pool.apply_async(self.directory_dictionary[folder_to_scan].update,
                                         args=(self.update_pool, self.directory_database,))  # Go. Scan. Be Free.
            if self.GUI:
                self.GUI.set_status("Scanning: " + folder_to_scan)
            else:
                print "Scanning:", folder_to_scan

    def backup_db(self, pathToDB):
        try:
            nm = pathToDB + str(datetime.datetime.now()).replace(":", "-") + ".backup"
            print nm
            if os.path.isfile(pathToDB):
                shutil.copy(pathToDB, nm)  # Move old database to a backup location
                print "Output file backed up."
        except ValueError:
            print "Output file not backed up. File may not exist, permissions, etc. This might be a problem later"

    def freshen(self):
        for i in self.roots:
            if i in self.directory_dictionary:
                self.directory_dictionary[i].update(self.update_pool, self.directory_database)

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
            if sys.platform == "linux2":
                if path[1] == ":":
                    drive = path[0]
                    path = "/media/"+drive+path[2:]
                    path = os.path.normpath(path)
            if not os.sep in path:
                self.roots.append(path)
            if f[2]:
                s_time = f[2]
            if path not in tmpDirectoryDictionary:
                tmpDirectoryDictionary[path] = Directory.Directory(path, s_time, tmpDirectoryDictionary)
                tmpDirectoryDictionary[path].files.append(mfile)
            else:
                tmpDirectoryDictionary[path].files.append(mfile)
        print "Done Importing"

