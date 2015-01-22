__author__ = 'Wild_Doogy'
import os, time,datetime
import gc

from multiprocessing import Pool

gc.disable()



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
        if "\\" in self.path:
            self.root = self.path[:self.path.rfind("\\")]
            tmp_root = self.root
            paths = []
            while "\\" in tmp_root:
                if tmp_root not in DirDict:
                    paths.append(tmp_root)
                    tmp_root = tmp_root[:tmp_root.rfind("\\")]
                else:
                    break
            for i in paths:
                DirDict[i] = Directory(i,self.timeUpdated,DirDict)
            if self.root in DirDict:
                DirDict[self.root].dirClasses[self.path] = self # linking
            else:
                print "Assuming", self.root, "to be the global root"
        else:
            print "Assuming", self.root, "to be the global root because there are no slashes"

    def printFiles(self, recursive=True):
        """
        Prints the files of this folder, and all subfolders recursively depending on the flag
        :param recursive: If this is true, then all files are printed recursively. Defaults to true
        :type recursive: bool
        :return: Does not return anything
        """
        if self.scanned == 0:
            self.update()
        for i in self.files:
            print self.path+"\\"+i
        if recursive:
            for i in self.dirClasses:
                self.dirClasses[i].printFiles()

    def writeFiles(self, mfile, recursive=True):
        """
        Writes the files in this directory to the provided FILE object. Recursive can be turned off.
        :param mfile: A FILE object where the files names will be written in CSV format
        :type mfile: file
        :param recursive: Flag for recursion
        :type recursive: bool
        :return: does not return anything
        """
        if self.scanned == 0:
            self.update()
        self.files.sort()
        for i in self.files:
            mfile.write("\""+self.path+"\",\""+i+"\"\n")
        sortedKeys = self.dirClasses.keys()
        sortedKeys.sort()
        if recursive:
            for i in sortedKeys:
               self.dirClasses[i].writeFiles(mfile)

    def markLower(self):
        """
        Marks directory and subdirectories scanned. Usually used when a directory has not been updated
        :return: Does not return anything
        """
        for i in self.dirClasses:
            self.dirClasses[i].markLower()
        self.scanned = 1

    def delLower(self):
        """
        Breaks the links associating this class with it's subdirectories. This is used when a folder does not exist.
        :return: Does not return anything
        """
        # for i in self.dirClasses:  # No need to go recursive. only break reference
        #    self.dirClasses[i].delLower()
        self.dirClasses = {}
        # del self.DirectoryDictionary[self.path]

    def update(self, thread_pool, recursive=True):
        """
        Where the real magic happens. This is used to refresh the files and folder in a directory. Recursive by default.
        :param thread_pool: A threaded pool to parallelize the update function
        :type thread_pool: Pool
        :param recursive: Flag for recursion
        :type recursive: bool
        :return: Does not return anything.
        """

        if os.path.isdir(self.path):
            if datetime.datetime.fromtimestamp(os.path.getmtime(self.path)) > self.timeUpdated:
                # Needs an update
                print "Updating",self.path
                (pathS, directoriesS , filesS) = (0,0,0)
                for (pathS, directoriesS, filesS) in os.walk(self.path):
                    break
                if filesS:
                    self.files = filesS
                if directoriesS:
                    self.directories = directoriesS
                for folder in self.directories:
                    fullfolder = os.path.join(self.path, folder)
                    if fullfolder not in self.dirClasses:
                        tmpDir = Directory(fullfolder, datetime.datetime(1900, 1, 1), self.DirectoryDictionary)
                        self.DirectoryDictionary[fullfolder] = tmpDir
                        self.dirClasses[fullfolder] = tmpDir
                if recursive:
                    for i in self.dirClasses:
                        thread_pool.apply_async(self.dirClasses[i].update, thread_pool)
            else:
                print "Path is all up to date:", self.path
                self.markLower()
        else:
            print "Detected deleted path:", self.path
            self.delLower()
        self.scanned = 1
        self.timeUpdated = datetime.date.fromtimestamp(time.time())


def importOldScan(oldScanFile,tmpDirectoryDictionary):
    """
    Used to import a .csv file generated from the last scan.
    :param oldScanFile: The path to the .csv file
    :type oldScanFile: str
    :param tmpDirectoryDictionary: A dictionary to hold all the imported Directory classes
    :type tmpDirectoryDictionary: dict of Directory
    :return: Does not return anything.
    """
    import csv
    print "Attempting to import old Database"
    try:
        with open(oldScanFile, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar="\"")
            try:
                daterow = spamreader.next()
                time_updated = datetime.datetime(int(daterow[1]), int(daterow[2]), int(daterow[3]))
            except StopIteration:
                print "Existing database file is empty."
                return
            for row in spamreader:
                if spamreader.line_num%10000 == 0:
                    print "reading line:", spamreader.line_num
                path = row[0].strip("\"")
                mfile = row[1].strip("\"")
                if path not in tmpDirectoryDictionary:
                    tmpDirectoryDictionary[path] = Directory(path, time_updated, tmpDirectoryDictionary)
                    tmpDirectoryDictionary[path].files.append(mfile)
                else:
                    tmpDirectoryDictionary[path].files.append(mfile)
    except IOError:
        print "Could not read existing database. Scanning from scratch."
        print oldScanFile



