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
        (pathS, directoriesS, filesS) = ((), (), ())
        try:
            for (pathS, directoriesS, filesS) in myScandir.walk(path):
                break
            return (pathS, directoriesS, filesS)
        except os.error:
            log("Path", path, "is not accessible.")
            # except TypeError:
            #    log("Path Seems to not exist:", path)

    def run(self):
        # gc.disable()
        gc.set_threshold(10)

        log("Roots:", self.roots)
        self.directories_to_refresh = self.directory_database.dump_paths()
        t2 = time.time()
        while self.go:
            if not len(self.directories_to_refresh) and not len(self.directories_to_scan):
                time.sleep(1)
            else:
                tmp_to_freshen = []
                for i in xrange(min(len(self.directories_to_refresh), 512)):  # Get the next 512 directories to freshen
                    try:
                        tmp = self.directories_to_refresh.pop()
                        if len(tmp) == 2:
                            tmp_to_freshen.append(tmp)
                        else:
                            log("Malformed path", tmp)
                    except IndexError:
                        break
                # log("To freshen", tmp_to_freshen)
                t3 = time.time()
                delta = t3 - t2
                log("Refresh prep overhead: ", delta, "Seconds (", round(delta * 300), "~Folders)")
                t = time.time()
                results_fresh = self.scan_pool.map(
                    lambda (path_scan_time): self.refresh_folder(path_scan_time), tmp_to_freshen)
                t2 = time.time()
                delta = max(t2 - t, .001)
                log("Refreshed ", len(tmp_to_freshen), "in ", delta, "Seconds (", len(tmp_to_freshen) / delta,
                    "Folders/Second)")
                # log("Fresh results", results_fresh)
                for index, result in enumerate(results_fresh):
                    # log("Processing ", result, index, tmp_to_freshen[index][0])
                    if result == 0:
                        # log("Adding", tmp_to_freshen[index][0])
                        self.directories_to_scan.append(tmp_to_freshen[index][0])
                    elif result == 1:
                        pass  # Directory is up to date
                        # TODO make this save the new scan time
                    elif result == 2:
                        # directory needs to be deleted from DB.
                        self.directory_database.del_folder(tmp_to_freshen[index][0])
                # log("To scan:", self.directories_to_scan)
                tmp_to_scan = []
                for i in xrange(min(len(self.directories_to_scan), 512)):  # Get the next 512 directories to freshen
                    try:
                        tmp_to_scan.append(self.directories_to_scan.pop())
                    except IndexError:
                        break
                # log("To Scan", tmp_to_scan)
                t3 = time.time()
                delta = t3 - t2
                log("Post refresh overhead: ", delta, "Seconds (", round(delta * 300), "~Folders)")
                t = time.time()
                results_scan = self.scan_pool.map(self.scan_folder, tmp_to_scan)
                t2 = time.time()
                delta = max(t2 - t, .001)
                log("Scanned ", len(tmp_to_scan), "in ", delta, "Seconds (", len(tmp_to_scan) / delta,
                    "Folders/Second)")
                # log("Scan results", results_scan)
                for (path, directories, files) in results_scan:
                    for directory in directories:
                        self.directories_to_refresh.append(
                            (os.path.join(path, directory),
                             self.directory_database.get_path_time(path)))  # TODO add a way to look up times.
                    for file in files:
                        self.directory_database.add_fileB(path, file)
                self.directory_database.writeout()
                t3 = time.time()
                delta = t3 - t2
                log("Post scan overhead: ", delta, "Seconds (", round(delta * 300), "~Folders)")
            if time.time() - self.last_update > self.update_interval:
                self.directories_to_refresh = self.directory_database.dump_paths()
                for root_dir in self.roots:
                    self.directories_to_refresh += (root_dir, 0.0)

    def add_to_roots(self, folder_to_scan):
        if not os.path.isdir(folder_to_scan):  # Make sure the folder exists
            log("Cannot access the folder to be scanned: ", folder_to_scan)
        else:
            self.directories_to_refresh.append((folder_to_scan, 0.0))

    def scan_dir(self, folder_to_scan):  # TODO Delete this
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
