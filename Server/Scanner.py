__author__ = 'boh01'

from threading import Thread

# Needed for scanning
from multiprocessing.dummy import Pool as ThreadPool
from threading import Lock
import Queue

# Needed for backup
import datetime, shutil

import gc
import os, time, sys

import DirectoryDB
import Directory


def log(*args):
    print "[Scanner]",
    print time.strftime("%c"),
    print " ",
    for arg in args:
        print arg,
    print ""


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
        self.last_update = 0
        self.update_interval = 60 * 60 * 12  # Seconds
        # TODO make this scan at a time, say 8 PM

    def init_database(self):
        FindIt = self.create_FindIt_folder()
        if not FindIt:
            log("Could not create the FindIt directory. Will now crash.")
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
            log("Crashing. Not made to run on mac")

    def load_preferences(self):
        # import csv
        # TODO need to create a config file
        pass

    def run(self):
        # gc.disable()
        gc.set_threshold(10)
        self.importOldScanFromDB(self.directory_database, self.directory_dictionary)
        # This is not technically needed for anything except updating
        # gc.enable()
        self.freshen()
        log("Roots:", self.roots)
        while self.go:
            if self.update_pool.thread_count > 0:
                while self.update_pool.thread_count > 0:
                    while not self.update_pool.messages.empty():
                        self.log += self.update_pool.messages.get() + "\n"
                    time.sleep(.1)
                while not self.update_pool.messages.empty():
                    self.log += self.update_pool.messages.get() + "\n"
                if self.GUI:
                    self.GUI.set_status("Done Scanning.")
                else:
                    log("Done Scanning")
            else:
                if time.time() > self.last_update + self.update_interval:
                    self.last_update = time.time()
                    self.freshen()
            time.sleep(.1)  # Poll
        self.update_pool.close()
        self.update_pool.join()
        self.directory_database.go = 0


    def add_to_roots(self, folder_to_scan):
        if not os.path.isdir(folder_to_scan):  # Make sure the folder exists
            log("Cannot access the folder to be scanned: ", folder_to_scan)
        else:
            if folder_to_scan not in self.roots:
                self.roots.append(folder_to_scan)
                log("Adding path ", folder_to_scan, " to roots")
            else:
                log("Path ", folder_to_scan, " already in roots")

    def scan_dir(self, folder_to_scan):
        self.add_to_roots(folder_to_scan)
        if os.path.isdir(folder_to_scan):  # Make sure the folder exists
            log("Scanning path ", folder_to_scan)
            if folder_to_scan not in self.directory_dictionary:
                self.directory_dictionary[folder_to_scan] = Directory.Directory(folder_to_scan, 0.0,
                                                                                self.directory_dictionary,
                                                                                self)  # Create Root and reset time.
            self.update_pool.apply_async(self.directory_dictionary[folder_to_scan].update,
                                         args=(self.update_pool, self.directory_database,))  # Go. Scan. Be Free.
            if self.GUI:
                self.GUI.set_status("Scanning: " + folder_to_scan)
            else:
                log("Scanning: ", folder_to_scan)

    def backup_db(self, pathToDB):
        try:
            nm = pathToDB + str(datetime.datetime.now()).replace(":", "-") + ".backup"
            log(nm)
            if os.path.isfile(pathToDB):
                shutil.copy(pathToDB, nm)  # Move old database to a backup location
                log("Output file backed up.")
        except ValueError:
            log("Output file not backed up. File may not exist, permissions, etc. This might be a problem later")

    def freshen(self):
        log("Freshening ", self.roots)
        for i in self.roots:
            if i in self.directory_dictionary:
                log("Rescanning ", i)
                self.directory_dictionary[i].update(self.update_pool, self.directory_database)
            else:
                log("Directory ", i, "not in dictionary:", self.directory_dictionary.keys())

    def importOldScanFromDB(self, DB, tmpDirectoryDictionary):
        """
        Used to import from a sqlite file generated from the last scan.
        :param DB: The path to the .csv file
        :type DB: DirectoryDB.DirectoryDB
        :param tmpDirectoryDictionary: A dictionary to hold all the imported Directory classes
        :type tmpDirectoryDictionary: dict of Directory.Directory
        :return: Does not return anything.
        """

        def test(file_path, directory_dict):
            path = file_path[0].strip("\"")
            # mfile = f[1].strip("\"")
            s_time = 0.0
            if sys.platform == "linux2":
                if path[1] == ":":
                    drive = path[0]
                    path = "/media/" + drive + path[2:]
                    path = os.path.normpath(path)
            if file_path[1]:
                s_time = file_path[1]
            if path not in directory_dict:
                directory_dict[path] = Directory.Directory(path, s_time, directory_dict, self)

        log("Attempting to import old Database from ", DB.file_path)
        data = DB.dump_paths()
        log("Got ", sys.getsizeof(data) / 1000000.0, " MB of data")
        line = ""
        bench_time = time.time()
        for line in xrange(len(data)):
            test(data[line], tmpDirectoryDictionary)
        log("Imported", line, "files in ", len(tmpDirectoryDictionary), " unique folders. (Parsed in", time.time()-bench_time, " Seconds)")
        # log("Size of directory:", sys.getsizeof(tmpDirectoryDictionary))
        # log("Total size of dictionary:", SizeOf.asizeof(tmpDirectoryDictionary))
