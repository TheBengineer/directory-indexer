__author__ = 'boh01'

import os
import math
import random
import Tkinter as tk

class Limb():
    def __init__(self, path, limbs_dict, parent=None):
        """

        :param path:
        :param limbs_dict:
        :type parent: Limb.Limb
        :return:
        """
        self.path = os.path.normpath(path)
        self.path_list = self.split_path(path)
        self.limbs_dict = limbs_dict
        limbs_dict[path] = self
        self.parent = parent
        if self.parent:
            self.location = (parent.location[0] + (parent.length * math.cos(parent.angle)),
                             parent.location[1] + (parent.length * math.sin(parent.angle)))
            self.angle = parent.angle + (random.random() *2.0) -1.0
        else:
            self.location = (0, 0)
            self.angle = 3.14159*1.5
        self.length = 40.0
        self.size = 1
        self.width = 1
        self.color = "black"
        self.color = random.choice(["red", "orange", "green", "blue", "violet"])
        self.children = {}

    def draw(self, canvas, parent, recursive=False):
        """

        :type canvas: tk.Canvas
        :param parent:
        :param recursive:
        :return:
        """
        x1 = self.location[0]
        y1 = self.location[1]
        x2 = self.location[0] + (self.length * math.cos(self.angle))
        y2 = self.location[1] + (self.length * math.sin(self.angle))
        print self.path, x1, y1, x2, y2
        canvas.create_line(x1, y1, x2, y2, fill=self.color, width=self.width)
        if recursive:
            for l in self.children:
                self.children[l].draw(canvas, self, True)

    def add_path(self, path):
        path = os.path.normpath(path)
        dir = os.path.split(path)[0]
        dirs = self.split_path(dir)

        dirs[0] = dirs[0].replace(":", ":" + os.sep)

        if dirs[0] not in self.limbs_dict:
            new_trunk = Limb(dirs[0], self.limbs_dict, self.limbs_dict[""])
            self.limbs_dict[dirs[0]] = new_trunk
        dirs_expanded = []

        for i, d in enumerate(dirs):
            if i == 0:
                dirs_expanded.append(d)
            else:
                dirs_expanded.append(os.path.join(*dirs[:i + 1]))

        for i, d in enumerate(dirs_expanded):
            if d not in self.limbs_dict and i > 0:
                print i, d, dirs, dirs[:i]
                parent_path = dirs_expanded[i - 1]
                new_limb = Limb(d, self.limbs_dict, self.limbs_dict[parent_path])
                self.add_limb(new_limb)
        self.limbs_dict[dir].grow()
        return

    def add_limb(self, limb):
        self.limbs_dict[limb.path] = limb
        self.children[os.path.split(limb.path)[1]] = limb
        if self.parent:
            self.location = (self.parent.location[0] + (self.parent.length * math.cos(self.parent.angle)),
                             self.parent.location[1] + (self.parent.length * math.sin(self.parent.angle)))
            self.angle = self.parent.angle + (random.random()*2) -1
            self.length = 40
        limb.grow()

    def split_path(self, p):
        a, b = os.path.split(p)
        c = (self.split_path(a) if len(a) and len(b) else []) + [b]
        c[0] = os.path.splitdrive(p)[0]
        return c

    def grow(self):
        self.size += 1
        self.width = (math.sqrt(self.size)/5) + 1
        if self.parent:
            self.parent.grow()

    def fatten(self):
        self.size += 1
        if self.parent:
            self.parent.fattten()


if __name__ == "__main__":
    ld = {}
    a = Limb("", ld)
    a.add_path("C:\\tmp\\crap\\more\\asdf\\no\\test.txt")