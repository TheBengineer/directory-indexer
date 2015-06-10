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

    for i in range(20):
        children = []
        for x in range(i):
            children.append(subprocess.Popen("python Node.py"))
        print i, scan_dir()
        for c in children:
            os.kill(c, signal.SIGTERM)


if __name__ == "__main__":
    main()
