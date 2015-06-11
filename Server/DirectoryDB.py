__author__ = 'Ben'
import sqlite3 as lite

from threading import Thread
from threading import Lock
import time
import os

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
        self.GUI = GUI
        self.go = 1
        """
        :type self.lock: threading.Lock
        :type self.local_lock: threading.Lock
        """

    def create_tables(self):
        create_table_files = "CREATE TABLE files " \
                             "(directory INTEGER, filename TEXT, scan_time REAL, CONSTRAINT unq UNIQUE (directory, filename));"
        create_table_directories = "CREATE TABLE directories " \
                                   "(id INTERGER, path TEXT, scan_time REAL, CONSTRAINT unq UNIQUE (path));"
        self.lock.acquire()
        tables = self.DB_cursor.execute("SELECT name FROM sqlite_master"
                                        " WHERE type='table'").fetchall()
        log("Found tables:", tables, "in the DB.")
        if ("files",) not in tables:
            self.DB_cursor.execute(create_table_files)
        if ("directories",) not in tables:
            self.DB_cursor.execute(create_table_directories)
        self.lock.release()

    def add_file(self, file_path):
        path, filename = os.path.split(file_path)
        self.local_lock.acquire()
        self.add_fileB(path, filename)
        self.local_lock.release()

    def add_fileB(self, path, filename):
        if filename and path:
            self.local_lock.acquire()
            self.files_to_add.append([path, filename])
            self.local_lock.release()
            if self.GUI:
                self.GUI.add_scanned_path(os.path.join(path, filename))

    def del_folder(self, folder_path):
        if folder_path:
            self.local_lock.acquire()
            self.folders_to_delete.append(folder_path)
            self.local_lock.release()

    def del_file(self, file_path):
        path, filename = os.path.split(file_path)
        if filename and path:
            self.files_to_delete.append([path, filename])

    def run(self):
        """
        Does nothing at this point
        May need to be polling instead of event based to make the DB happy
        :return:
        """

        def fix_path(path):
            if path.startswith("/media/"):
                path2 = path[7:]  # Slice off the leading "/media/"
                drive = path2[:path2.find("/")]
                path = drive + ":" + path[8:]  # TODO this is hardcoded to my drive system
            return path.replace("/", "\\")

        while self.go:
            self.local_lock.acquire()
            if len(self.files_to_add):
                for path, filename in self.files_to_add:
                    path = fix_path(path)
                    query = "INSERT OR REPLACE INTO files (path, filename, scan_time) VALUES(\"{path}\", " \
                            " \"{filename}\", \"{time}\");".format(path=path, filename=filename,
                                                                   time=time.time())
                    self.lock.acquire()
                    try:
                        self.DB_cursor.execute(query)
                    except lite.OperationalError:
                        log("ERROR, could not add file: ", query)
                    self.lock.release()
            self.files_to_add = []
            if len(self.files_to_delete):
                for path, filename in self.files_to_delete:
                    path = fix_path(path)
                    query = "DELETE FROM files WHERE path ='{path}' AND filename ='{filename}'" \
                            " ;".format(path=path, filename=filename)
                    self.lock.acquire()
                    self.DB_cursor.execute(query)
                    self.lock.release()
            self.files_to_delete = []
            if len(self.folders_to_delete):
                for path in self.folders_to_delete:
                    path = fix_path(path)
                    query = "DELETE FROM files WHERE path LIKE '{path}%'".format(path=path)
                    self.lock.acquire()
                    self.DB_cursor.execute(query)
                    self.lock.release()
            self.folders_to_delete = []
            self.local_lock.release()
            self.writeout()
            # TODO is 30 seconds a good time for the database to be written to?
            time.sleep(.1)

    def get_folders(self, filename):
        query = "SELECT path, filename FROM files WHERE filename LIKE '{filename}';".format(filename=filename)
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        return data

    def get_folders_500(self, filename):
        query = "SELECT path, filename FROM files WHERE filename LIKE '{filename}' LIMIT 500".format(filename=filename)
        log("Getting results for ", query)
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        return data

    def get_folders_limit(self, filename, limit=500):
        query = "SELECT directories.path, files.filename FROM files WHERE filename LIKE '{filename}' LIMIT {limit}".format(
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

    def nuke(self):
        query1 = "DELETE FROM files;"
        query2 = "DELETE FROM directories;"
        self.lock.acquire()
        self.DB_cursor.execute(query1)
        self.DB_cursor.execute(query2)
        self.DB_cursor.execute("VACUUM;")
        self.lock.release()
