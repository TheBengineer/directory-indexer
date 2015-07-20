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
import string

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
        self.linux = (sys.platform == "linux2")

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
        self.time_cache = {}

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
        elif self.linux:
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
            mtime = os.path.getmtime(path)
            if mtime > scan_time:
                return (0, mtime)  # The folder was updated.
            else:
                return (1, mtime)  # The folder was NOT updated.
        except os.error:  # Not accessible.
            return (2, 0.0)  # The folder non-accessible.

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

    def linux_path(self, path):
        try:
            if path[1] == ":":
                drive = path[0].upper()
                new_path = "/media/" + drive + "/" + string.replace(path[3:], "\\", "/")
                return new_path
            else:
                return False
        except:
            return False

    def schedule_refresh(self, path, last_scan_time):
        if path and not last_scan_time==None:
            self.directories_to_refresh.append((path, last_scan_time))
        else:
            log("Trying to schedule a refresh on invalid path/time:", path/ last_scan_time)

    def run(self):
        # gc.disable()
        gc.set_threshold(10)

        time.sleep(.1)
        log("Roots:", self.roots)
        self.directories_to_refresh += self.directory_database.dump_paths_dict(self.time_cache)
        t2 = time.time()
        while self.go:
            if not len(self.directories_to_refresh) and not len(self.directories_to_scan):
                time.sleep(1)
            else:
                self.tmp_to_freshen = []
                for i in xrange(min(len(self.directories_to_refresh), 512)):  # Get the next 512 directories to freshen
                    try:
                        (self.path, scan_time) = self.directories_to_refresh.pop()
                        if self.linux:
                            self.l_path = self.linux_path(self.path)
                            try:
                                if self.l_path:
                                    if "//" in self.l_path:
                                        self.directory_database.del_folder(self.l_path)
                                        self.l_path = self.l_path.replace("//","/")
                                        while "//" in self.l_path:
                                            self.l_path = self.l_path.replace("//","/")
                                    self.tmp_to_freshen.append((self.l_path, scan_time))
                                elif self.path[:7] == '/media/':
                                    if "//" in self.path:
                                        self.path = self.path.replace("//","/")
                                        while "//" in self.path:
                                            self.path = self.path.replace("//","/")
                                    self.tmp_to_freshen.append((self.path, scan_time))  # Already in linux format.
                                    # log("Path seems to be already linux", path)
                                else:
                                    log("Path could not be converted to linux.", self.path)
                            except TypeError:
                                log("Malformed path", self.path, scan_time)
                        else:
                            self.tmp_to_freshen.append((self.path, scan_time))
                    except IndexError:
                        break
                # log("To freshen", tmp_to_freshen)
                t3 = time.time()
                delta = t3 - t2
                log("Refresh prep overhead: ", delta, "Seconds (", round(delta * 300), "~Folders)")
                t = time.time()
                results_fresh = self.scan_pool.map(
                    lambda (path_scan_time): self.refresh_folder(path_scan_time), self.tmp_to_freshen)
                t2 = time.time()
                delta = max(t2 - t, .001)
                log("Refreshed ", len(self.tmp_to_freshen), "in ", delta, "Seconds (", len(self.tmp_to_freshen) / delta,
                    "Folders/Second)")
                # log("Fresh results", results_fresh)
                for index, (result, mtime) in enumerate(results_fresh):
                    path = self.tmp_to_freshen[index][0]
                    # log("Processing ", result, index, tmp_to_freshen[index][0])
                    if result == 0:
                        # log("Adding", tmp_to_freshen[index][0])
                        self.directories_to_scan.append(path)
                        self.time_cache[path] = mtime
                        #log("Adding path to cache:", path)
                    elif result == 1:
                        self.time_cache[path] = mtime
                        #log("Adding path to cache:", path)
                    elif result == 2:
                        # directory needs to be deleted from DB.
                        self.directory_database.del_folder(self.tmp_to_freshen[index][0])
                # log("To scan:", self.directories_to_scan)
                self.tmp_to_scan = []
                for i in xrange(min(len(self.directories_to_scan), 512)):  # Get the next 512 directories to freshen
                    try:
                        self.tmp_to_scan.append(self.directories_to_scan.pop())
                    except IndexError:
                        break
                # log("To Scan", tmp_to_scan)
                # t3 = time.time()
                # delta = t3 - t2
                # log("Post refresh overhead: ", delta, "Seconds (", round(delta * 300), "~Folders)")
                # Not needed. This is always super fast.
                t = time.time()
                results_scan = self.scan_pool.map(self.scan_folder, self.tmp_to_scan)
                t2 = time.time()
                delta = max(t2 - t, .001)
                log("Scanned ", len(self.tmp_to_scan), "in ", delta, "Seconds (", len(self.tmp_to_scan) / delta,
                    "Folders/Second)")
                # log("Scan results", results_scan)
                for (path, directories, files) in results_scan:
                    for directory in directories:
                        if self.linux:
                            if not path[-1] == "/":
                                folderpath = path + "/" + directory
                            else:
                                folderpath = path + directory
                        else:
                            if not path[-1] == "\\":
                                folderpath = path + "\\" + directory
                            else:
                                folderpath = path + directory
                        # log("Debug", folderpath, self.time_cache) # This breaks all the things.
                        # log("Debug", folderpath)
                        if folderpath in self.time_cache:
                            scan_time = self.time_cache[folderpath]
                        else:
                            scan_time = 0.0
                            #log("Path not in cache", folderpath)
                        self.directories_to_refresh.append(
                            (os.path.join(path, directory), scan_time))
                    for file in files:
                        self.directory_database.add_fileB(path, file)
                # Post scan overhead is not needed. Now that writeout is handled separately, this is very fast.
                #t3 = time.time()
                #delta = t3 - t2
                #log("Post scan overhead:", len(directories), "Dirs,",len(files), "Files in", delta, "Seconds (", (len(directories)+len(files))/delta, "Items/Second)")
                t2 = time.time()
            current_time = str(datetime.datetime.now())
            if time.time() - self.last_update > self.update_interval and current_time[current_time.find(" ")+1:current_time.find(":")] == "18" :
                self.last_update = time.time()
                self.directories_to_refresh += self.directory_database.dump_paths()
                for root_dir in self.roots:
                    self.schedule_refresh(root_dir, 0.0)
            time.sleep(.1)
        os._exit(1) # When loops drops, then exit.

    def add_to_roots(self, folder_to_scan):
        if not os.path.isdir(folder_to_scan):  # Make sure the folder exists
            log("Cannot access the folder to be scanned: ", folder_to_scan)
        else:
            self.directories_to_refresh.append((folder_to_scan, 0.0))
            self.roots.append(folder_to_scan)

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
