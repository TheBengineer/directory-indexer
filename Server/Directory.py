__author__ = 'Wild_Doogy'
import os
import time

import Queue


def log(*args):
    print "[Directory]",
    print time.strftime("%c"),
    print " ",
    for arg in args:
        print arg,
    print ""


class Directory(object):
    """
    This class holds a directory in memory, all the files it has, and a dictionary of the directories it has under it.
    """

    def __init__(self, path, timeUpdated, DirDict):
        """

        :param path: This parameter is the file system path that this directory represents
        :type path: str
        :param timeUpdated: The time the directory was last scanned. If the folder was modified after this, update will rescan
        :type timeUpdated: time.time
        :param DirDict: The massive dictionary holding ALL directory classes
        :type DirDict: dict of Directory
        :return: Does not return anything
        """
        self.path = path
        self.files = []
        self.directories = []
        self.dirClasses = {}
        self.timeUpdated = timeUpdated
        self.DirectoryDictionary = DirDict
        self.root = self.path
        self.scanned = 0
        if os.sep in self.path:
            self.root = self.path[:self.path.rfind(os.sep)]
            tmp_root = self.root
            paths = []
            while os.sep in tmp_root:
                if tmp_root not in DirDict:
                    paths.append(tmp_root)
                    tmp_root = tmp_root[:tmp_root.rfind(os.sep)]
                else:
                    break
            for i in paths:
                DirDict[i] = Directory(i, self.timeUpdated, DirDict)
            if self.root in DirDict:
                DirDict[self.root].dirClasses[self.path] = self  # linking
            else:
                log("Assuming ", self.root, " to be the global root")
        else:
            log("Assuming ", self.root, " to be the global root because there are no slashes")

    def printFiles(self, thread_pool, recursive=True):
        """
        Prints the files of this folder, and all subfolders recursively depending on the flag
        :param recursive: If this is true, then all files are printed recursively. Defaults to true
        :type recursive: bool
        :return: Does not return anything
        """
        if self.scanned == 0:
            self.update(thread_pool)
        for i in self.files:
            log(self.path + "\\" + i)
        if recursive:
            for i in self.dirClasses:
                self.dirClasses[i].printFiles(thread_pool)

    def markLower(self):
        """
        Marks directory and subdirectories scanned. Usually used when a directory has not been updated
        :return: Does not return anything
        """
        for i in self.dirClasses:
            self.dirClasses[i].markLower()
        self.scanned = 1

    def delLower(self, DB):
        """
        Breaks the links associating this class with it's subdirectories. This is used when a folder does not exist.
        :return: Does not return anything
        """
        # for i in self.dirClasses:  # No need to go recursive. only break reference
        # self.dirClasses[i].delLower()
        self.dirClasses = {}
        DB.del_folder(self.path)
        # del self.DirectoryDictionary[self.path]

    def update(self, thread_pool, DB, recursive=True):
        """
        Where the real magic happens. This is used to refresh the files and folder in a directory. Recursive by default.
        :param thread_pool: A threaded pool to parallelize the update function
        :type thread_pool: Pool
        :type thread_pool.thread_lock: multiprocessing.Pool
        :type thread_pool.messages: Queue.Queue
        :type thread_pool.thread_count: int
        :type DB: DirectoryDB.DirectoryDB
        :param recursive: Flag for recursion
        :type recursive: bool
        :return: Does not return anything.

        """
        thread_pool.messages.put(
            "Processing " + str(self.path) + " Folder Time:" + str(self.timeUpdated) + " Now:" + str(time.time()))
        import scandir as myScandir

        thread_pool.thread_lock.acquire()
        thread_pool.thread_count += 1
        thread_pool.thread_lock.release()
        if os.path.isdir(self.path):
            if type(self.timeUpdated) == "date":
                self.timeUpdated = 0.0
                log("fixed")
            if os.path.getmtime(self.path) > self.timeUpdated:
                thread_pool.messages.put("Updating " + str(self.path))
                # Needs an update
                (pathS, directoriesS, filesS) = ([], [], [])
                for (pathS, directoriesS, filesS) in myScandir.walk(self.path):
                    break
            else:
                thread_pool.messages.put("Path is all up to date: " + str(self.path))
                self.markLower()
            pathS = []
            for folder in directoriesS:
                fullfolder = os.path.join(self.path, folder)
                if fullfolder not in self.dirClasses:
                    tmpDir = Directory(fullfolder, 0.0, self.DirectoryDictionary)
                    self.DirectoryDictionary[fullfolder] = tmpDir
                    self.dirClasses[fullfolder] = tmpDir
            directoriesS = []
            thread_pool.messages.put("Writing " + str(self.path))
            for f in filesS:
                DB.add_fileB(self.path, f)
            filesS = []
            if recursive:
                for i in self.dirClasses:
                    thread_pool.apply_async(self.dirClasses[i].update, args=(thread_pool, DB,))
        else:
            thread_pool.messages.put("Detected deleted path: " + str(self.path))
            self.delLower(DB)
        self.scanned = 1
        self.timeUpdated = time.time()
        thread_pool.thread_lock.acquire()
        thread_pool.thread_count -= 1
        thread_pool.thread_lock.release()





