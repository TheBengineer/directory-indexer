__author__ = 'Wild_Doogy'

from Indexer import *
import datetime

if __name__ == '__main__':
    FolderToScan = "M:\\Drawings" # CHANGE this to whatever you want to. Just remember to use double slashes
    db_folder = "C:\\Projects"#os.getcwd()
    db_file = "DB.csv" # Will be placed next to the python file. Probably best to not run from network drive.
    last_update_date = datetime.datetime(1990, 1, 1)
    pathToOutputCSV = os.path.join(db_folder, db_file)

    # TODO need to create a config file

    if not os.path.isdir(FolderToScan):  # Make sure the folder exists
        print "Cannot access the folder to be scanned. Please fix this near the bottom of the source file."
        raw_input("Press enter to exit")
        exit()

    if not os.path.isfile(pathToOutputCSV):  # Make sure the output database can be created
        print "Cannot find an existing database. Get ready for hours of scanning."
        if not os.path.isdir(os.path.split(pathToOutputCSV)[0]):
            print "Cannot even find the folder for the output file to be placed. This means the scan will not be saved."
            print pathToOutputCSV
            raw_input("Press enter to exit")
            exit()

    startTime = time.time() # Write down time for later

    DirectoryDictionary = {}
    DirectoryDictionary[FolderToScan] = Directory(FolderToScan, last_update_date ,DirectoryDictionary)
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
    print "Cannot create output file"+pathToOutputCSV+"This is bad. Scan will not be saved."
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
