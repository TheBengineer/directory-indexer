__author__ = 'boh01'

import time

import scandir as sd

path = "O:\\Technical_Support\\Applications_Engineering\\Customer Archives"

def scan(directory):
    for (pathS, directoriesS, filesS) in sd.walk(directory):
        for d in directoriesS:
            scan(d)


t = time.time()
scan(path)
#print time.time() - t
