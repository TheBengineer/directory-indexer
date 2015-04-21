__author__ = 'boh01'

from threading import Thread

class TreeView(Thread):
    def __init__(self, tk):
        Thread.__init__(self)
        self.tree_main = tk.Tk()
        self.

    def run(self):
        self.tree_main.mainloop()