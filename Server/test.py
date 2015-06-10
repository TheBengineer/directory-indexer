#from memory_profiler import profile
import random
import string
import sys
import time
from multiprocessing.dummy import Pool as ThreadPool
import scandir as sd

import multiprocessing as mp

from multiprocessing import Pool



def main():
    pool = Pool()


    def scan_dir(a):
        return a + 1


    def scan_dira(a):
        path = "O:\\Technical_Support\\Applications_Engineering\\Customer Archives"

        def scan(directory):
            for (pathS, directoriesS, filesS) in sd.walk(directory):
                for d in directoriesS:
                    scan(d)


        t = time.time()
        scan(path)
        return time.time() - t



    print pool.map(scan_dir, range(3))



if __name__ == "__main__":
    mp.freeze_support()
    main()