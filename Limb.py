__author__ = 'boh01'

import os
import math


class Limb():
    def __init__(self, path, limbs_dict, parent=None):
        self.path = os.path.normpath(path)
        self.limbs_dict = limbs_dict
        self.parent = parent
        self.location = (0, 0)
        self.angle = 0.0
        self.length = 20.0
        self.size = 1
        self.color = "black"
        self.children = {}

    def draw(self, canvas, parent, recursive=False):
        canvas.draw_line(self.location[0], self.location[1], self.location[0] + (self.length * math.cos(self.angle)),
                         self.location[1] + (self.length * math.sin(self.angle)), fill=self.color)
        if recursive:
            for l in self.children:
                l.draw(canvas, self, True)

    def add_path(self, path):
        path = os.path.normpath(path)
        print self.path, path
        if self.path == path[:len(self.path)]:
            tail = path[len(self.path):]
            tails = self.split_path(tail)
            new_dir = tails[0]
            if tails:
                child_path = os.path.join(self.path, new_dir)
                new_limb = Limb(child_path, self.limbs_dict, self)
                self.add_limb(new_limb)
        else:
            if not self.parent:
                new_trunk = Limb(path, self.limbs_dict, self)
                drive = os.path.splitdrive(path)
                if drive:
                    self.add_limb(new_trunk)
                else:
                    print path, "Seems to not have a drive"
            else:
                self.parent.add_path(path)

    def add_limb(self, limb):
        self.limbs_dict[limb.path] = limb
        self.children[limb.path] = limb
        self.grow()

    def split_path(self, p):
        a, b = os.path.split(p)
        return (self.split_path(a) if len(a) and len(b) else []) + [b]

    def grow(self):
        self.size += 1
        if self.parent:
            self.parent.grow()

    def fatten(self):
        self.size += 1
        if self.parent:
            self.parent.fattten()