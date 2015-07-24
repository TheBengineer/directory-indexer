__author__ = 'Ben'
import sqlite3 as lite
from threading import Thread
from threading import Lock
import time
import os
import sys

"""
This database will hold all the files and paths that are normally written to a CSV file.

"""


def log(*args):
    print "[DirectoryDB]",
    print time.strftime("%c"),
    print " ",
    for arg in args:
        print arg,
    print ""


class DirectoryDB(Thread):
    def __init__(self, file_path, GUI=None):
        # TODO make this save data more efficiently
        Thread.__init__(self)
        self.lock = Lock()
        self.local_lock = Lock()
        self.lock.acquire()
        self.file_path = file_path
        self.DB = lite.connect(self.file_path, check_same_thread=False)
        self.DB.text_factory = str
        self.DB_cursor = self.DB.cursor()
        self.lock.release()
        self.create_tables()
        self.files_to_add = []
        self.files_to_delete = []
        self.folders_to_delete = []
        self.tmp_files_to_add = {}
        self.tmp_files_to_del = {}
        self.folder_ids = {}
        self.GUI = GUI
        self.go = 1
        self.platform = sys.platform
        self.write_interval = 600
        self.changed = 0
        """
        :type self.lock: threading.Lock
        :type self.local_lock: threading.Lock
        """

    def create_tables(self):
        create_table_files = "CREATE TABLE files " \
                             "(directory INTEGER, filename TEXT, scan_time REAL, CONSTRAINT unq UNIQUE (directory, filename));"
        create_table_directories = "CREATE TABLE directories " \
                                   "(id INTEGER PRIMARY KEY, path TEXT, scan_time REAL, CONSTRAINT unq UNIQUE (path));"
        self.lock.acquire()
        tables = self.DB_cursor.execute("SELECT name FROM sqlite_master"
                                        " WHERE type='table'").fetchall()
        log("Found tables:", tables, "in the DB.")
        if ("files",) not in tables:
            self.DB_cursor.execute(create_table_files)
        if ("directories",) not in tables:
            self.DB_cursor.execute(create_table_directories)
        self.changed = 1
        self.lock.release()

    def add_file(self, file_path):
        path, filename = os.path.split(file_path)
        self.add_fileB(path, filename)

    def add_fileB(self, path, filename):
        if filename and path:
            # self.local_lock.acquire()
            self.files_to_add.append([path, filename])
            # self.local_lock.release()
            if self.GUI:
                self.GUI.add_scanned_path(os.path.join(path, filename))

    def del_folder(self, folder_path):
        if folder_path:
            # self.local_lock.acquire()
            self.folders_to_delete.append(folder_path)
            # self.local_lock.release()

    def del_file(self, file_path):
        path, filename = os.path.split(file_path)
        if filename and path:
            self.files_to_delete.append([path, filename])

    def get_path_id(self, path, scan_time=0.0):
        query = "INSERT OR IGNORE INTO directories(path, scan_time) VALUES(\"{0}\", {1});".format(path, scan_time)
        query2 = "SELECT directories.id FROM directories WHERE path LIKE \"{0}\";".format(path)
        self.lock.acquire()
        self.DB_cursor.execute(query)
        self.DB_cursor.execute(query2)
        data = self.DB_cursor.fetchall()
        self.changed = 1
        self.lock.release()
        if len(data):
            return data[0][0]
        else:
            return -1

    def get_path_time(self, path):
        query = "SELECT directories.scan_time FROM directories WHERE path LIKE \"{0}\";".format(path)
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        if len(data):
            return data[0][0]
        else:
            return 0.0

    def fix_path(self, path, destination="normal"):
        if self.platform == "win32" or destination == "DB":
            if path.startswith("/media/"):
                path2 = path[7:]  # Slice off the leading "/media/"
                drive = path2[0]  # Grab the next char
                path = drive + ":" + path[8:]  # TODO this is hardcoded to my drive system
            return path.replace("/", "\\")
        elif self.platform == "linux2":
            if path[1] == ":":
                drive = path[0].upper()  # Grab the next char
                path = "/media/" + drive + "/" + path[2:]  # TODO this is hardcoded to my drive system
            return path.replace("\\", "/")
        else:
            return path  # TODO Make a Mac version?

    def refresh_ids(self):
        for path, path_id in self.dump_paths_ids():
            self.folder_ids[path] = path_id

    def manage_add_files(self):
        self.tmp_files_to_add = {}
        t = time.time()
        self.status = "Starting batch add"
        while len(self.files_to_add) and len(self.tmp_files_to_add) < 10000:  # Get 10K files to play with
            path, filename = self.files_to_add.pop()
            if path not in self.tmp_files_to_add:
                self.tmp_files_to_add[path] = [[filename], [""]]
            else:
                self.tmp_files_to_add[path][0].append(filename)
        self.status = "Refreshing ids"
        if len(self.tmp_files_to_add):  # Refresh the local id cache
            self.refresh_ids()
        self.status = "Fixing paths for {0} files".format(len(self.tmp_files_to_add))
        self.substatus = 0
        add_folders_staging = []
        for path in self.tmp_files_to_add:  # Make a Dict of the files to add
            self.substatus += 1
            fixed_path = self.fix_path(path, "DB")
            self.tmp_files_to_add[path][1] = fixed_path
            if fixed_path not in self.folder_ids:
                add_folders_staging.append((fixed_path, time.time()))
        self.status = "Batch add {0} folders".format(len(add_folders_staging))
        if len(add_folders_staging):
            query = "INSERT OR IGNORE INTO directories(path, scan_time) VALUES(?, ?);"
            self.lock.acquire()
            try:
                self.DB_cursor.executemany(query, add_folders_staging)
            except lite.OperationalError as e:
                log("ERROR, could not add directory: ", query, "With data", add_folders_staging, e)
            self.changed = 1
            self.lock.release()
            self.status = "Refresh again"
        if len(self.tmp_files_to_add):  # Refresh the local id cache
            self.refresh_ids()
        self.status = "Looping through {0} paths".format(len(self.tmp_files_to_add))
        add_files_staging = []
        for path in self.tmp_files_to_add:  # Loop through paths
            fixed_path = self.tmp_files_to_add[path][1]
            self.substatus = "Looping through {0} files".format(len(self.tmp_files_to_add[path][0]))
            for filename in self.tmp_files_to_add[path][0]:  # Loop through files and add them
                add_files_staging.append((self.folder_ids[fixed_path], filename, time.time()))
        self.status = "Batch add {0} files at time {1}".format(len(add_files_staging), time.strftime("%c"))
        if len(add_files_staging):
            query = "INSERT OR REPLACE INTO files (directory, filename, scan_time) " \
                    "VALUES(?, ?, ?);"
            self.lock.acquire()
            try:
                self.DB_cursor.executemany(query, add_files_staging)
            except lite.OperationalError as e:
                log("ERROR, could not add file: ", query, "With data", add_files_staging, e)
            self.changed = 1
            self.lock.release()
        self.status = "Done adding files, cleaning up."

    def manage_del_files(self):
        """
        This function is just to clean the code in the run loop up.
        This function will delete the next 10K files in the list of files to delete
        :return: None
        """
        self.tmp_files_to_del = {}
        t = time.time()
        self.status = "Grabbing a list of files to batch delete"
        while len(self.files_to_delete) and len(self.tmp_files_to_del) < 10000:  # Get 10K files to play with
            path, filename = self.files_to_delete.pop()
            if path not in self.tmp_files_to_del:
                self.tmp_files_to_del[path] = [[filename], [""]]
            else:
                self.tmp_files_to_del[path][0].append(filename)
        self.status = "Refreshing ids"
        if len(self.tmp_files_to_del):  # Refresh the local id cache
            self.refresh_ids()
        self.status = "Fixing paths for {} folders".format(len(self.tmp_files_to_del))
        self.substatus = 0
        for path in self.tmp_files_to_del:  # Make a Dict of the files to delete
            self.substatus += 1
            fixed_path = self.fix_path(path, "DB")
            self.tmp_files_to_del[path][1] = fixed_path
            if fixed_path not in self.folder_ids:
                del self.tmp_files_to_del[path]
        self.status = "Batch delete {0} folders".format(len(self.tmp_files_to_del))
        for path in self.tmp_files_to_del:
            fixed_path = self.tmp_files_to_del[path][1]
            filename_string = ""
            for filename in self.tmp_files_to_del[path][0]:
                filename_string += "\"{0}\",".format(filename)
            filename_string = filename_string[:-1]  # Slice off the trailing comma
            query = "DELETE FROM files WHERE directory = {0} AND filename IN ({1});".format(self.folder_ids[fixed_path],
                                                                                            filename_string)
            self.do(query)
        self.delete_empty_folders()
        self.delete_orphan_files()

    def do(self, query):
        self.lock.acquire()
        try:
            self.DB_cursor.execute(query)
        except lite.OperationalError as e:
            log("ERROR, could not execute query: ", query, e)
        self.changed = 1
        self.lock.release()

    def delete_empty_folders(self):
        self.do("DELETE FROM directories WHERE id NOT IN (SELECT directory FROM files);")

    def delete_orphan_files(self):
        self.do("DELETE FROM files WHERE directory NOT IN (SELECT id FROM directories);")

    def run(self):
        """
        :return:
        """
        self.last_write = 0.0
        self.refresh_ids()
        while self.go:
            self.local_lock.acquire()
            self.manage_add_files()
            self.manage_del_files()
            loops = 0
            while len(self.folders_to_delete) and loops < 1000:
                path = self.folders_to_delete.pop()
                path = self.fix_path(path)
                path_id = self.get_path_id(path)
                query = "DELETE FROM files WHERE directory = {0}".format(path_id)
                query2 = "DELETE FROM directories WHERE id = {0}".format(path_id)
                log("Deleting path", path)
                self.do(query)
                self.do(query2)
                loops += 1
            self.local_lock.release()
            if self.changed:
                if time.time() - self.last_write > self.write_interval / 100:
                    self.writeout()
            else:
                if time.time() - self.last_write > self.write_interval:
                    self.writeout()
            if not len(self.files_to_add) and not len(self.folders_to_delete) and not len(self.files_to_delete):
                time.sleep(.5)

    def get_folders(self, filename):
        query = "SELECT directories.path, f.filename FROM files f JOIN directories ON f.directory=directories.id WHERE f.filename LIKE '{filename}';".format(
            filename=filename)
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        return data

    def get_folders_500(self, filename):
        query = "SELECT directories.path, f.filename FROM files f JOIN directories ON f.directory=directories.id WHERE f.filename LIKE '{filename}' LIMIT 500;".format(
            filename=filename)
        log("Getting results for ", query)
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        return data

    def funnel_folders(self, folders):
        for path in folders:
            query = "INSERT OR IGNORE INTO directories(path, scan_time) VALUES(\"{0}\", {1});".format(path, time.time())
            self.lock.acquire()
            self.DB_cursor.execute(query)
            self.lock.release()
        return

    def get_folders_limit(self, filename, limit=500):
        query = "SELECT directories.path, f.filename  FROM files f JOIN directories ON f.directory=directories.id WHERE f.filename LIKE '{filename}' LIMIT {limit};".format(
            filename=filename, limit=limit)
        log("Getting results for ", query)
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        return data

    def writeout(self):
        self.lock.acquire()
        self.DB.commit()
        self.lock.release()
        self.changed = 0
        self.last_write = time.time()

    def dump(self):
        query = "SELECT path, filename, scan_time FROM files;"
        # TODO need a join here
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        return data

    def dump_paths(self):
        query = "SELECT DISTINCT path, scan_time FROM directories;"
        log("Starting to dump all stored paths. This may take a while.")
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        log("Done dumping all paths.")
        return data

    def dump_paths_ids(self):
        query = "SELECT DISTINCT path, id FROM directories;"
        log("Starting to dump all stored paths and IDs. This may take a while.")
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        log("Done dumping all paths.")
        return data

    def dump_paths_dict(self, dict):
        data = self.dump_paths()
        result = []
        for path, time_ in data:
            if path:
                path_fixed = self.fix_path(path)
                dict[path_fixed] = time_
                result.append((path_fixed, time_))
        return result

    def nuke(self):
        query1 = "DELETE FROM files;"
        query2 = "DELETE FROM directories;"
        self.lock.acquire()
        self.DB_cursor.execute(query1)
        self.DB_cursor.execute(query2)
        self.DB_cursor.execute("VACUUM;")
        self.changed = 1
        self.lock.release()
