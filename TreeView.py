__author__ = 'boh01'

from threading import Thread
import Tkinter as tk
import random
import os

import Limb


class TreeView(Thread):
    def __init__(self, tk):
        """

        :type tk: Tkinter
        :return:
        """
        Thread.__init__(self)
        self.tree_main = tk.Tk()
        self.canvas_width = 800
        self.canvas_height = 500
        self.canvas = tk.Canvas(self.tree_main, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        self.canvas.create_line(0, 0, random.random() * 40, random.random() * 40, fill="#FF00FF")
        self.pile = {}
        self.limbs_dict = {}
        self.root = Limb.Limb("", self.limbs_dict)
        self.limbs_dict[""] = self.root
        self.root.location = (self.canvas_width/2.0, self.canvas_height-100)
        self.root.angle = 3.14159*1.5
        self.make_data()


    def make_data(self):
        for root, dirs, files in os.walk("C:\\tmp"):
            for f in files:
                path = os.path.join(root, f)
                print path
                self.root.add_path(path)
                self.root.draw(self.canvas, self, True)

    def make_limb(self, depth, heritage):
        limb = Limb.Limb("", self.limbs_dict)
        if depth < 2:
            limbs = random.randrange(2, 5)
        elif depth < 4:
            limbs = random.randrange(2, 8)
        elif depth < 6:
            limbs = int(random.randrange(0, 2))
        else:
            if random.random() < 1.0 / depth:
                limbs = 1
            else:
                limbs = 0
        heritage.append(limb)
        for i in range(limbs):
            self.make_limb(depth + 1, heritage)

    def add_to_pile(self, data):
        pass

    def run(self):
        self.tree_main.mainloop()


if __name__ == "__main__":
    a = TreeView(tk)
    a.start()

    def foo(root, level=0):
        print "\t"*level, root.path
        for i in root.children:
            foo(root.children[i], level + 1)

    #foo(a.root)
