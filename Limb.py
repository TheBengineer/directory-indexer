__author__ = 'boh01'

import os
import math
import random


class Limb():
    def __init__(self, path, limbs_dict, parent=None):
        """

        :param path:
        :param limbs_dict:
        :type parent: Limb.Limb
        :return:
        """
        self.path = os.path.normpath(path)
        self.limbs_dict = limbs_dict
        self.parent = parent
        self.location = (0, 0)
        self.angle = 0.0
        self.length = 20.0
        self.size = 1
        self.width = 1
        self.color = "black"
        self.children = {}

    def draw(self, canvas, parent, recursive=False):
        canvas.create_line(self.location[0], self.location[1], self.location[0] + (self.length * math.cos(self.angle)),
                           self.location[1] + (self.length * math.sin(self.angle)), fill=self.color, width=self.width)
        if recursive:
            for l in self.children:
                self.children[l].draw(canvas, self, True)

    def add_path(self, path):
        path = os.path.normpath(path)
        dir = os.path.split(path)[0]
        dirs = self.split_path(dir)
        me = os.path.split(self.path)[1]
        print me, self.path, dirs, dir
        if me in dirs:
            return
        if self.path == path[:len(self.path)]:
            tail = path[len(self.path):]
            tails = self.split_path(tail)
            new_dir = tails[0]
            if tails:
                child_path = os.path.join(self.path, new_dir)
                new_limb = Limb(child_path, self.limbs_dict, self)
                new_limb.add_path(path)
                self.add_limb(new_limb)
        else:
            if not self.parent:
                drive = os.path.splitdrive(path)
                if drive:
                    if drive not in self.children:
                        new_trunk = Limb(path, self.limbs_dict, self)
                        print "New trunk", drive, path
                        self.add_limb(new_trunk)
                    else:
                        self.children[drive].add_path(path)
                else:
                    print path, "Seems to not have a drive"
            else:
                self.parent.add_path(path)

    def add_limb(self, limb):
        self.limbs_dict[limb.path] = limb
        self.children[os.path.split(limb.path)[1]] = limb
        if self.parent:
            self.location = (self.parent.location[0] + (self.parent.length * math.cos(self.parent.angle)),
                             self.parent.location[1] + (self.parent.length * math.sin(self.parent.angle)))
            self.angle = self.parent.angle + random.uniform(-10.0, 10.0)
            self.length = 20
        self.grow()

    def split_path(self, p):
        a, b = os.path.split(p)
        c = (self.split_path(a) if len(a) and len(b) else []) + [b]
        c[0] = os.path.splitdrive(p)[0]
        return c

    def grow(self):
        self.size += 1
        self.width = math.sqrt(self.size)
        if self.parent:
            self.parent.grow()

    def fatten(self):
        self.size += 1
        if self.parent:
            self.parent.fattten()