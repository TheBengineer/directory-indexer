
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


f = open("C:\\Users\\boh01\\Documents\\allfilesinM"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M")+".csv",'w')
lasttime = datetime.date(2014,8,8)
print lasttime
once = 1
matches = []
lastroot = ""
for root, dirnames, filenames in os.walk("M:\\Drawings"):
    print dirnames
    for dir in dirnames:
        print time.time()-os.path.getmtime(root+"\\"+dir)
        if os.path.getmtime(root+"\\"+dir) < time.time():
            dirnames.remove(dir)
    print dirnames
    for filename in filenames:
        matches.append((root, filename))
        f.write("\""+root +"\",\""+ filename+"\"\n")
        if root != lastroot:
            print time.ctime(os.path.getmtime(root)), root
        lastroot = root
        
f.close()
