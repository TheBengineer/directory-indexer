
#"C:\Users\boh01\Downloads"

import fnmatch

import os, time,datetime



class Directory(object):
    def __init__(self, path,timeUpdated,DirDict):
        self.path = path
        self.files = []
        self.directories = []
        self.dirClasses = {}
        self.timeUpdated = timeUpdated
        self.DirectoryDictionary = DirDict
        self.root = self.path[:self.path.rfind("\\")]
        tmp = self.root.split("\\")
        self.scanned = 0
        if not tmp in self.DirectoryDictionary.keys():
            for i in range(len(tmp)):
                dpath = ""
                for j in range(i):
                    dpath += tmp[j]+"\\"
                if dpath != "":
                    if not dpath in self.DirectoryDictionary.keys():
                        self.DirectoryDictionary[dpath] = Directory(dpath,self.timeUpdated,self.DirectoryDictionary)
        self.DirectoryDictionary[self.root].dirClasses[self.path] = self # linking
    def printFiles(self):
        if self.scanned == 0:
            self.update()
        for i in self.files:
            print self.path+"\\"+i
    def writeFiles(self,file):
        if self.scanned == 0:
            self.update()
        for i in self.files:
            file.write(self.path+","+i+"\n")
    def markLower(self):
        for i in self.dirClasses:
            self.dirClasses[i].markLower()
        self.scanned = 1
    def delLower(self):
        #for i in self.dirClasses:
        #    self.dirClasses[i].delLower()
        self.dirClasses = {}
        #del self.DirectoryDictionary[self.path]

    def update(self):
        if os.path.isdir(self.path):
            print datetime.datetime.fromtimestamp(os.path.getmtime(self.path)) ,"asdfasdf", self.timeUpdated
            if datetime.datetime.fromtimestamp(os.path.getmtime(self.path)) > self.timeUpdated:
                #Needs an update
                print "Updating",self.path
                print self.dirClasses
                for i in self.dirClasses:
                    self.dirClasses[i].update()
                (pathS, directoriesS , filesS) = (0,0,0)
                for (pathS, directoriesS , filesS) in os.walk(self.path):
                    break
                if filesS:
                    self.files = filesS
                if directoriesS:
                    self.directories = directoriesS
                for folder in self.directories:
                    fullfolder = self.root+"\\"+folder
                    self.DirectoryDictionary[fullfolder] = Directory(fullfolder,datetime.datetime.fromtimestamp(time.time()),self.DirectoryDictionary)
            else:
                self.markLower()
        else:
            self.delLower()
        self.scanned = 1
        self.timeUpdated = datetime.date.fromtimestamp(time.time())


rootDIR = "M:\\Drawings"

DirectoryDictionary = {}
DirectoryDictionary[rootDIR] = Directory(rootDIR,datetime.datetime(1900,1,1),DirectoryDictionary)


pathToCSV = "H:\\Projects\\Monster\\DB_2.csv"

import csv

with open(pathToCSV , 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar="'")
    daterow = spamreader.next()
    timeUpdated = date_object = datetime.datetime(int(daterow[1]),int(daterow[2]),int(daterow[3]))
    for row in spamreader:
        if spamreader.line_num%1000 == 0:
            print spamreader.line_num
        try:
            path = row[0]
            file = row[1]
            if path in DirectoryDictionary:
                DirectoryDictionary[path].files.append(file)
            else:
                DirectoryDictionary[path] = Directory(path,timeUpdated,DirectoryDictionary)
        except:
            print "Here",Exception


DirectoryDictionary[rootDIR].update()


raw_input("All done")

#main = Directory("M:\\Drawings")
#main.search()

fpath = "C:\\Users\\boh01\\Documents\\allfilesinM"+datetime.datetime.now().strftime("%Y-%m-%d %H.%M")+".csv"
print fpath
f = open(fpath,'w')
lasttime = time.mktime(datetime.date(2014,8,8).timetuple())
once = 1
matches = []
lastroot = ""
for root, dirnames, filenames in os.walk("M:\\Drawings"):
    for dir in dirnames:
        if os.path.getmtime(root+"\\"+dir) < lasttime:
            dirnames.remove(dir)
    print "Directories to look at:",dirnames
    for filename in filenames:
        matches.append((root, filename))
        print (root, filename)
        f.write("\""+root +"\",\""+ filename+"\"\n")
        if root != lastroot:
            print time.ctime(os.path.getmtime(root)), root
        lastroot = root
        
f.close()
