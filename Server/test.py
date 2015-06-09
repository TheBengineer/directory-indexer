#from memory_profiler import profile
import random
import string
import sys
import time
from multiprocessing.dummy import Pool as ThreadPool
import scandir as sd

path = "O:\\Technical_Support\\Applications_Engineering\\Customer Archives"

def scan(directory):
    for (pathS, directoriesS, filesS) in sd.walk(directory):
        for d in directoriesS:
            scan(d)
t = time.time()
scan(path)
print time.time() - t




asdf = """
@profile(precision = 16)
def my_func():

    for j in xrange(1000*100):
        pass

    d = {}
    for i in xrange(1000*10):
        d = make(d)
    print sys.getsizeof(d)
    time.sleep(3)
    d = {}
    time.sleep(3)
    for i in xrange(1000*10):
        d = make(d)
    time.sleep(3)
    del d
    d = {}
    time.sleep(3)

@profile(precision = 16)
def make(d):
    s = ''
    for _ in xrange(10):
        c = random.choice(string.ascii_uppercase + string.digits)
        s = s.join(c)
    v = random.random()
    d[s] = v
    return d

if __name__ == '__main__':
    my_func()
"""

