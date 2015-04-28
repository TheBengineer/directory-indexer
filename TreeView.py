__author__ = 'boh01'

from threading import Thread
import Queue
import Tkinter as tk
import os

import Limb


class TreeView(Thread):
    def __init__(self, tk, GUI):
        """

        :type tk: Tkinter
        :return:
        """
        Thread.__init__(self)
        self.GUI = GUI
        self.running = False
        self.tree_main = tk.Tk()

        self.canvas_width = 800
        self.canvas_height = 500
        self.canvas = tk.Canvas(self.tree_main, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()
        self.pile = {}
        self.limbs_dict = {}
        self.root = Limb.Limb("", self.limbs_dict)
        self.limbs_dict[""] = self.root
        self.root.location = (self.canvas_width / 2.0, self.canvas_height - 100)
        self.root.angle = 3.14159 * 1.5
        self.tree_main.title("Tree View - Ben Holleran April 2015")
        self.pile = Queue.Queue()
        self.tree_main.protocol("WM_DELETE_WINDOW", self.tree_main.destroy)

    def make_data(self):
        for root, dirs, files in os.walk("C:\\tmp"):
            for f in files:
                path = os.path.join(root, f)
                self.root.add_path(path)
                self.root.draw(self.canvas, None)

    def add_path(self, path):
        self.pile.put(path)

    def num_waiting(self):
        self.canvas.create_text(20, 40, text=str(self.GUI.scanned_paths.qsize()))

    def burn_pile(self):
        if self.GUI:
            self.num_waiting()
            while not self.GUI.scanned_paths.empty():
                path = self.GUI.scanned_paths.get()
                self.root.add_path(path)
            self.root.draw(self.canvas, None, True)
            self.tree_main.after(100, self.burn_pile)

    def run(self):
        # self.canvas.create_line(0, 0, random.random() * 40, random.random() * 40, fill="#00FFFF")
        self.running = True
        self.tree_main.after(100, self.burn_pile)
        self.tree_main.mainloop()


if __name__ == "__main__":
    a = TreeView(tk, None)
    a.start()

    def foo(root, level=0):
        print "\t" * level, root.path
        for i in root.children:
            foo(root.children[i], level + 1)

            # foo(a.root)
