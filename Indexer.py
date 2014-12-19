
import fnmatch
import shutil

import os, time,datetime
import sqlite3



class Directory(object):
    def __init__(self, path, timeUpdated, DirDict):
        self.path = path
        self.files = []
        self.directories = []
        self.dirClasses = {}
        self.timeUpdated = timeUpdated
        self.DirectoryDictionary = DirDict
        self.root = self.path
        self.scanned = 0
        if self.path.rfind("\\") > 0:
            self.root = self.path[:self.path.rfind("\\")]
            tmp = self.root.split("\\")
            paths = []
            for i in range(len(tmp)):
                dpath = tmp[0]
                for j in range(1,i+1):
                    dpath += "\\"+tmp[j]
                paths.append(dpath)
            for i in paths:
                if not i in  self.DirectoryDictionary.keys():
                    self.DirectoryDictionary[i] = Directory(i,self.timeUpdated,self.DirectoryDictionary)
            try:
                self.DirectoryDictionary[self.root].dirClasses[self.path] = self # linking
            except KeyError:
                print "Assuming", self.root, "to be the global root"
        else:
            print "Assuming", self.root, "to be the global root because there are no slashes"

    def printFiles(self):
        if self.scanned == 0:
            self.update()
        for i in self.files:
            print self.path+"\\"+i
        for i in self.dirClasses:
            self.dirClasses[i].printFiles()

    def writeFiles(self, mfile):
        if self.scanned == 0:
            self.update()
        self.files.sort()
        for i in self.files:
            mfile.write("\""+self.path+"\",\""+i+"\"\n")
        sortedKeys = self.dirClasses.keys()
        sortedKeys.sort()
        for i in sortedKeys:
            self.dirClasses[i].writeFiles(mfile)

    def markLower(self):
        for i in self.dirClasses:
            self.dirClasses[i].markLower()
        self.scanned = 1

    def delLower(self):
        # for i in self.dirClasses:
        #    self.dirClasses[i].delLower()
        self.dirClasses = {}
        # del self.DirectoryDictionary[self.path]

    def update(self):
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
                    if fullfolder not in self.dirClasses.keys():
                        tmpDir = Directory(fullfolder, datetime.datetime(1900, 1, 1), self.DirectoryDictionary)
                        self.DirectoryDictionary[fullfolder] = tmpDir
                        self.dirClasses[fullfolder] = tmpDir
                for i in self.dirClasses:
                    self.dirClasses[i].update()
            else:
                print "Path is all up to date:", self.path
                self.markLower()
        else:
            print "Detected deleted path:", self.path
            self.delLower()
        self.scanned = 1
        self.timeUpdated = datetime.date.fromtimestamp(time.time())


def importOldScan(oldScanFile,tmpDirectoryDictionary):
    import csv
    print "Attempting to import old Database"
    try:
        with open(oldScanFile, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar="\"")
            daterow = spamreader.next()
            timeUpdated = date_object = datetime.datetime(int(daterow[1]), int(daterow[2]), int(daterow[3]))
            for row in spamreader:
                if spamreader.line_num%1000 == 0:
                    print "reading line:", spamreader.line_num
                try:
                    path = row[0].strip("\"")
                    file = row[1].strip("\"")
                    if path in tmpDirectoryDictionary:
                        tmpDirectoryDictionary[path].files.append(file)
                    else:
                        tmpDirectoryDictionary[path] = Directory(path, timeUpdated, tmpDirectoryDictionary)
                except:
                    print "Here", Exception
    except IOError:
        print "Could not read existing database. Scanning from scratch."



FolderToScan = "M:\\Drawings" # CHANGE this to whatever you want to. Just remember to use double slashes

pathToOutputCSV = "DB.csv" # Will be placed next to the python file. Probably best to not run from network drive.

if not os.path.isdir(FolderToScan):
    print "Cannot access the folder to be scanned. Please fix this near the bottom of the source file."
    raw_input("Press enter to exit")
    exit()

if not os.path.isfile(pathToOutputCSV):
    print "Cannot find an existing database. Get ready for hours of scanning."
    if not os.path.isdir(os.path.split(pathToOutputCSV)[0]):
        print "Cannot even find the folder for the output file to be placed. This means the scan will not be saved."
        raw_input("Press enter to exit")
        exit()


startTime = time.time() # Write down time for later


DirectoryDictionary = {}
DirectoryDictionary[FolderToScan] = Directory(FolderToScan, datetime.datetime(1990, 1, 1),DirectoryDictionary)
# Above plants a seed at the base of the folder tree. Any folders made before the date will not be scanned

importOldScan(pathToOutputCSV,DirectoryDictionary) # populate memory with already scanned files.



try:
    shutil.move(pathToOutputCSV, pathToOutputCSV+".backup") # Move old database to a backup location
    print "Output file backed up."
except:
    print "Output file not backed up. File may not exist, permissions, etc. This might be a problem later"

try:
    with open(pathToOutputCSV,"w"):
        print "Output file opened."
except:
    print "Cannot create output file. This is bad. Scan will not be saved."
    raw_input("Press enter to exit, and then go create the directory, fix the file path. etc. ")
    exit()

DirectoryDictionary[FolderToScan].update() # Go. Scan. Be Free.


filewritten = 0

while filewritten == 0:
    try:
        f = open(pathToOutputCSV,"w")
        dt = datetime.datetime.now().timetuple()
        st = "Python Datetime"
        for i in dt:
            st += ","+str(i)
        st += "\n"
        print "Writing database."
        f.write(st)
        DirectoryDictionary[FolderToScan].writeFiles(f)
        f.close()
        filewritten = 1
    except IOError:
        print "Something broke. Cannot open output file. Please type a new path for the output file"
        pathToOutputCSV = raw_input("Path:")






raw_input("Completed in "+str((time.time()-startTime)/60)+" Minutes")
