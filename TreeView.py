__author__ = 'boh01'

from threading import Thread

import Tkinter as tk
import random


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
        self.data = {}
        self.make_data()

    def make_data(self):
        for i in range(random.randrange(2,5)):
            self.make_limb(0, [])

    def make_limb(self, depth, heritage):
        limb = Limb()
        if depth < 2:
            limbs = random.randrange(2,5)
        elif depth < 4:
            limbs = random.randrange(2,8)
        elif depth < 6:
            limbs = int(random.randrange(0,2))
        else:
            if random.random() < 1.0/depth:
                limbs = 1
            else:
                limbs = 0
        heritage.append(limb)
        for i in range(limbs):
            self.make_limb(depth+1, heritage)


    def run(self):
        self.tree_main.mainloop()
        print "here"

class Limb():
    def __init__(self, limbs, history, heritage):
        self.heritage = heritage
        self.limbs = limbs
        self.history = history

    def draw(self, canvas):
        pass

if __name__ == "__main__":
    a = TreeView(tk)
    a.start()