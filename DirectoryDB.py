__author__ = 'Ben'
import sqlite3 as lite

from threading import Thread
from threading import Lock
import cPickle
import time
import os


"""
This database will hold all the files and paths that are normally written to a CSV file.

"""


class DirectoryDB(Thread):
    def __init__(self, file_path):
        # TODO make this save data more efficiently
        Thread.__init__(self)
        self.lock = Lock()
        self.local_lock = Lock()
        self.lock.acquire()
        self.file_path = file_path
        self.DB = lite.connect(self.file_path, check_same_thread=False)
        self.DB_cursor = self.DB.cursor()
        self.lock.release()
        self.create_table()
        self.files_to_add = []
        self.files_to_delete = []
        self.folders_to_delete = []
        """
        :type self.lock: threading.Lock
        :type self.local_lock: threading.Lock
        """

    def create_table(self):
        create_updates = "CREATE TABLE files " \
                         "(path TEXT, filename TEXT);"
        self.lock.acquire()
        tables = self.DB_cursor.execute("SELECT name FROM sqlite_master"
                                        " WHERE type='table' AND name='Updates';").fetchall()
        if tables == []:
            self.DB_cursor.execute(create_updates)
        self.lock.release()

    def add_file(self, file_path):
        path, filename = os.path.split(file_path)
        if filename and path:
            self.local_lock.acquire()
            self.files_to_add.append([path, filename])
            self.local_lock.release()

    def run(self):
        """
        Does nothing at this point
        May need to be polling instead of event based to make the DB happy
        :return:
        """

        self.go = 1
        while self.go:
            self.local_lock.acquire()
            if len(self.files_to_add):
                for path, filename in self.files_to_add:
                    query = "INSERT OR REPLACE INTO Updates VALUES(path, '{path}', filename, {filename}" \
                    " );".format(path=path, filename=filename)
                    self.lock.acquire()
                    self.DB_cursor.execute(query)
                    self.lock.release()
            self.files_to_add = []
            if len(self.files_to_delete):
                for path, filename in self.files_to_delete:
                    query = "DELETE FROM Updates WHERE path ='{path}' and filename ='{filename}'" \
                    " ;".format(path=path, filename=filename)
                    self.lock.acquire()
                    self.DB_cursor.execute(query)
                    self.lock.release()
            self.files_to_delete = []
            if len(self.folders_to_delete):
                for path in self.folders_to_delete:
                    query = "DELETE FROM Updates WHERE path LIKE '{path}%'".format(path=path)
                    self.lock.acquire()
                    self.DB_cursor.execute(query)
                    self.lock.release()
            self.folders_to_delete = []
            self.local_lock.release()
            self.writeout()
            # TODO is 30 seconds a good time for the database to be written to?
            time.sleep(.1)


    def get_folders(self, filename):
        query = "SELECT path, filename WHERE filename = '{filename}';".format(filename=filename)
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        return data

    def writeout(self):
        self.lock.acquire()
        self.DB.commit()
        self.lock.release()