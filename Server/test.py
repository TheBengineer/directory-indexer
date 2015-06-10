# from memory_profiler import profile
import os
import time
import signal
import subprocess

import scandir as sd


def main():
    def scan_dir(a=0):
        path = "O:\\Technical_Support\\Applications_Engineering\\Customer Archives"

        def scan(directory):
            for (pathS, directoriesS, filesS) in sd.walk(directory):
                for d in directoriesS:
                    scan(d)

        t = time.time()
        scan(path)
        return time.time() - t

    for i in range(0,25,5):
        children = []
        for x in range(i):
            children.append(subprocess.Popen("python Node.py").pid)
        print i, scan_dir()
        for c in children:
            if c:
                try:
                    os.kill(c, signal.SIGTERM)
                except:
                    pass


if __name__ == "__main__":
    main()
