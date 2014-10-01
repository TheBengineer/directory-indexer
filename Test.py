
#"C:\Users\boh01\Downloads"

import fnmatch

import os, time,datetime



class Directory(object):
    path = ""
    files = []
    directories = []
    dirClasses = []
    def __init__(self, path):
        self.path = path
        self.search()
    def search(self):
        for (self.path2, self.directories , self.files) in os.walk(self.path):
            break
        for self.folder in self.directories:
            print self.path,"\\",self.folder
            self.dirClasses.append(Directory(os.path.join(self.path,self.folder)))

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
