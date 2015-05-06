from memory_profiler import profile

@profile(precision = 16)
def my_func():
    import random
    import string
    import sys
    import time

    for j in xrange(1000*100):
        pass

    d = {}
    for i in xrange(1000*10):
        s = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        v = random.random()
        d[s] = v
        if i%1000 == 0:
            print i
    print sys.getsizeof(d)
    time.sleep(3)
    d = {}
    time.sleep(3)
    for i in xrange(1000*10):
        s = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        v = random.random()
        d[s] = v
        if i%1000 == 0:
            print i
    time.sleep(3)
    del d
    d = {}
    time.sleep(3)

if __name__ == '__main__':
    my_func()


