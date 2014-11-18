
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
        print self.path
        print self.root
        tmp = self.root.split("\\")
        for i in range(len(tmp)):
            dpath = ""
            for j in range(i):
                dpath += tmp[j]+"\\"
            print dpath
            if not dpath in self.DirectoryDictionary.keys():
                self.DirectoryDictionary[dpath] = Directory(dpath,self.timeUpdated,self.DirectoryDictionary)
        #while not self.root in self.DirectoryDictionary.keys():
        #    tmp = tmp[:tmp.rfind("\\")]

        #else:
        #    self.DirectoryDictionary[self.root].dirClasses[self.path] = self # Link this back up the tree
        #self.search()
    def search(self):
        for (self.path2, self.directories , self.files) in os.walk(self.path):
            break
        for self.folder in self.directories:
            print self.path,"\\",self.folder
            self.dirClasses.append(Directory(os.path.join(self.path,self.folder)))
    def printFiles(self):
        for i in self.files:
            print self.path+"\\"+i
    def writeFiles(self,file):
        for i in self.files:
            file.write(self.path+","+i+"\n")


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
            print Exception

print DirectoryDictionary[DirectoryDictionary.keys()[1]].printFiles()


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
