__author__ = 'Ben'
import sqlite3 as lite

from threading import Thread
from threading import Lock
import cPickle
import time


"""
This database will hold all the files and paths that are normally written to a CSV file.

"""


class DirectoryDB(Thread):
    def __init__(self):
        # TODO make this save data more efficiently
        Thread.__init__(self)
        self.lock = Lock()
        self.lock.acquire()
        self.DB = lite.connect(self.filename+".db", check_same_thread=False)
        self.DB_cursor = self.DB.cursor()
        self.lock.release()

    def create_table(self):
        create_updates = "CREATE TABLE Updates " \
                         "(sector_id INT, body_id TEXT, attribute INT, data INT, dataF REAL, dataS TEXT, dataB BLOB, " \
                         "PRIMARY KEY (sector_id, body_id, attribute));"
        # Multiple fields to hold the data. Three will be null.
        self.lock.acquire()
        tables = self.DB_cursor.execute("SELECT name FROM sqlite_master"
                                        " WHERE type='table' AND name='Updates';").fetchall()
        if tables == []:
            self.DB_cursor.execute(create_updates)
        self.lock.release()

    def run(self):
        """
        Does nothing at this point
        May need to be polling instead of event based to make the DB happy
        :return:
        """

        self.go = 1
        while self.go:
            self.writeout()
            # TODO is 30 seconds a good time for the database to be written to?
            time.sleep(30)


    def save_attribute(self, sector_id, body_id, attribute_id, data):
        """
        This function will save an updated attribute
        :param sectorID:
        :param bodyID:
        :param data:
        :return:
        """

        payload = None
        payload_complex = 0
        if type(data) == int:
            payload = str(data)+", Null, Null, Null"
        elif type(data) == float:
            payload = "Null, "+str(data)+", Null, Null"
        elif type(data) == str:
            payload = "Null, Null, '"+data+"', Null"
        else:
            payload = "Null, Null, Null, ?"
            payload_complex = 1

        query = "INSERT OR REPLACE INTO Updates VALUES({sector_id}, '{body_id}', {attribute_id}, {payload}" \
                " );".format(sector_id=sector_id, body_id=body_id, attribute_id=attribute_id, payload=payload)
        self.lock.acquire()
        if payload_complex:
            self.DB_cursor.execute(query, (lite.Binary(cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)),))
        else:
            self.DB_cursor.execute(query)
        self.lock.release()

    def get_changes(self, sector_id):
        """
        This function returns the ID and seed of a sector
        :return str:
        """
        query = "SELECT body_id, attribute, data, dataF, dataS, dataB FROM Updates WHERE sector_id={sector_id};" \
                "".format(sector_id=sector_id)
        self.lock.acquire()
        self.DB_cursor.execute(query)
        data = self.DB_cursor.fetchall()
        self.lock.release()
        return data

    def make_id(self, x, y, z):
        return (int(x)*1000000) + (int(y)*1000) + int(z)

    def get_coordinates(self, ID):
        ID = int(ID)
        x = (ID - (ID % 1000000))/1000000
        y = ((ID - (ID % 1000))/1000) % 1000
        z = ID % 1000000
        print (x, y, z)
        return x, y, z

    def writeout(self):
        self.lock.acquire()
        self.DB.commit()
        self.lock.release()

    def make_body_id(self):
        pass
