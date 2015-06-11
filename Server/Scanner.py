__author__ = 'boh01'

from threading import Thread

# Needed for scanning
from multiprocessing.pool import ThreadPool as Pool_for_map
from multiprocessing.dummy import Pool as ThreadPool

from threading import Lock
import Queue

# Needed for backup
import datetime, shutil

import gc
import os, time, sys

import DirectoryDB
import Directory

import scandir as myScandir


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

        self.directories_to_refresh = []
        self.directories_to_scan = []
        self.scan_results = [[], [], []]

        self.scan_pool = Pool_for_map(128)

        self.go = 1
        self.log = ""
        self.last_update = time.time()
        self.update_interval = 60 * 60 * 12  # Seconds
        # TODO make this scan at a time, say 8 PM

    def init_database(self):
        FindIt = self.create_FindIt_folder()
        if not FindIt:
            log("Could not create the FindIt directory. Will now crash.")
            quit()
        database_filename = os.path.join(FindIt, "FindItV2.db")
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

    def refresh_folder(self, (path, scan_time)):
        try:
            if os.path.getmtime(path) > scan_time:
                return 0  # The folder was updated.
            else:
                return 1  # The folder was NOT updated.
        except os.error:  # Not accessible.
            return 2  # The folder non-accessible.

    def scan_folder(self, path):
        try:
            for (pathS, directoriesS, filesS) in myScandir.walk(path):
                break
            return (pathS, directoriesS, filesS)
        except os.error:
            pass

    def run(self):
        # gc.disable()
        gc.set_threshold(10)

        log("Roots:", self.roots)
        self.directories_to_refresh.append(
            ("O:\\Technical_Support", 1.2))  # TODO remove debug
        while self.go:
            tmp_to_freshen = []
            for i in xrange(min(len(self.directories_to_refresh), 512)):  # Get the next 512 directories to freshen
                try:
                    tmp_to_freshen.append(self.directories_to_refresh.pop())
                except IndexError:
                    break
            log(tmp_to_freshen)
            results_fresh = self.scan_pool.map(
                lambda (path_scan_time): self.refresh_folder(path_scan_time),tmp_to_freshen)
            log(results_fresh)
            for result, index in enumerate(results_fresh):
                if result == 0:
                    self.directories_to_scan.append(tmp_to_freshen[index][0])
                elif result == 1:
                    pass  # Directory is up to date
                    # TODO make this save the new scan time
                elif result == 2:
                    # directory needs to be deleted from DB.
                    self.directory_database.del_folder(tmp_to_freshen[index][0])
            log("To scan:", self.directories_to_scan)
            # TODO add scanning here
            tmp_to_scan = []
            for i in xrange(min(len(self.directories_to_scan), 512)):  # Get the next 512 directories to freshen
                try:
                    tmp_to_scan.append(self.directories_to_scan.pop())
                except IndexError:
                    break
            log(tmp_to_scan)
            results_scan = self.scan_pool.map(self.scan_folder, tmp_to_scan)
            log(results_scan)
            for (path, directories, files) in results_scan:
                for directory in directories:
                    self.directories_to_refresh.append((os.path.join(path, directory), 0.0)) # TODO add a way to look up times.
                for file in files:
                    pass
                    #self.directory_database.add_fileB(path, file)
            self.directory_database.writeout()

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
            # log("Attempting to scan path ", folder_to_scan) # Not needed
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
        for i in self.roots:
            if i in self.directory_dictionary:
                log("Freshening ", i)
                self.update_pool.apply_async(self.directory_dictionary[i].update,
                                             args=(self.update_pool, self.directory_database,))  # Go. Scan. Be Free.
            else:
                log("Directory ", i, "not in dictionary. Scanning.")
                self.scan_dir(i)

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
        log("Imported", line, "files in ", len(tmpDirectoryDictionary), " unique folders. (Parsed in",
            time.time() - bench_time, " Seconds)")
        # log("Size of directory:", sys.getsizeof(tmpDirectoryDictionary))
        # log("Total size of dictionary:", SizeOf.asizeof(tmpDirectoryDictionary))
