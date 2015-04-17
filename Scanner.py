__author__ = 'boh01'

from threading import Thread
import os

import DirectoryDB


class Scanner(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.directory_dictionary = {}
        self.init_db()

    def init_db(self):
        FindIt = self.create_FindIt()
        if not FindIt:
            print "Could not create the FindIt directory. Will now crash."
            quit()
        self.directory_database = DirectoryDB.DirectoryDB(os.path.join(FindIt, "FindIt.db"))


    def create_FindIt(self):
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

        pass


    def load_database(self):
        pass

    def run(self):
        pass

    def scan_dir(self, dir):
        pass


a = Scanner()