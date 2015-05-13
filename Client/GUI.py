__author__ = 'boh01'

from threading import Thread
import os
import Tkinter as tk
import tkFileDialog
import subprocess
import Queue
import socket
import time

import mhMultiListBox

def log(*args):
    print "[GUI]",
    print time.strftime("%c"),
    print " ",
    for arg in args:
        print arg,
    print ""

class Window(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.scanned_paths = Queue.Queue()
        self.tree = None


        self.version = "Beta"

        self.window = tk.Tk()  # Init
        self.window.geometry("800x500+300+300")
        self.window.title("Fujifilm Dimatix File Index Database - Ben Holleran April 2015")
        self.window.protocol("WM_DELETE_WINDOW", self.onQuit)

        # self.Directory_index_database = DirectoryDB.DirectoryDB("C:/tmp/Monster.db")
        # self.Directory_index_database.start()
        # self.directory_indexer = Directory.Directory()

        # ################ Menu

        self.menu = tk.Menu(self.window)
        self.window.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=self.onQuit)

        # self.edit_menu = tk.Menu(self.menu)
        # self.menu.add_cascade(label="Edit", menu=self.edit_menu)

        self.help_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_version)


        # ################ Search

        self.search_frame = tk.Frame(self.window)
        # self.search_frame.config(borderwidth=4, relief=tk.GROOVE) # layout
        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search)
        self.search_text = tk.Entry(self.search_frame, width=300, font="courier 14")
        self.search_text.bind('<Return>', self.search)
        self.search_button.pack(side=tk.LEFT)
        self.search_text.pack()
        self.search_frame.pack(side=tk.TOP, fill=tk.X)

        # ################ Results


        self.results_frame = tk.Frame(self.window)

        self.results_options_frame = tk.Frame(self.results_frame)
        self.open_file_button = tk.Button(self.results_options_frame, text="Open File", command=self.open_file)
        self.open_folder_button = tk.Button(self.results_options_frame, text="Open Folder", command=self.open_folder)
        self.open_file_button.pack(side=tk.LEFT)
        self.open_folder_button.pack(side=tk.LEFT)
        self.results_label = tk.Label(self.results_frame, text="Files matching search")

        # ################ Results Scroll Box
        self.multi_list_box = mhMultiListBox.MultiListbox(self.results_frame, (('File', 170),
                                                                               ('Type', 70),
                                                                               ('Path', 400)), height=20,
                                                          command=self.open_folder, commandRC=self.open_file)
        # self.results_options_frame.pack()

        # self.results_label.pack(side=tk.TOP, fill=tk.X)
        self.multi_list_box.pack(expand=tk.YES, fill=tk.BOTH)

        # self.multi_list_box.colmapping['Files'].bind('<Double-Button-1>', self.open_file)
        self.multi_list_box.bind('<Double-Button-1>', self.open_file)
        self.multi_list_box.bind('<Button-3>', self.open_folder)
        # self.files_listbox.bind('<Button-3>', self.open_folder)
        # self.folders_listbox.bind('<MouseWheel>', self.on_scroll)
        # self.files_listbox.bind('<MouseWheel>', self.on_scroll)
        # self.folders_listbox.bind('<Button-4>', self.scroll_up)
        # self.files_listbox.bind('<Button-4>', self.scroll_up)
        # self.folders_listbox.bind('<Button-5>', self.scroll_down)
        # self.files_listbox.bind('<Button-5>', self.scroll_down)

        self.results_frame.pack(fill=tk.BOTH, expand=1)

        # Tab order

        # self.tree.start()
        self.search_text.focus()


    def socket_init(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def socket_connect(self, my_socket, address):
        """

        :param my_socket: A socket object to start listening on
        :type my_socket: socket.socket
        :param address: The address to start listening on. Format: ("localhost", 80)
        :type address: tuple of (str, int)
        :return:
        """
        my_socket.connect(address)
        return my_socket


    def a(self, asdf=0, asdf2=0):
        pass

    def add_scanned_path(self, path):
        self.scanned_paths.put(path)


    def search(self, event=""):
        search_text = self.search_text.get()
        if search_text:
            s = self.socket_connect(self.socket_init(), ("BOH001", 9091))
            s.send(search_text) # Need to add some checks here
            result_string = s.recv(1000000000)
            num_results = 0
            self.multi_list_box.delete(0, tk.END)
            while result_string != "":
                results = result_string.split("\n")
                i = 0
                for i, result in enumerate(results):
                    text = (
                        result[result.rfind("\\") + 1:], result[result.rfind(".") + 1:].upper(),
                        result)
                    self.multi_list_box.insert(0, text)
                num_results += i
                result_string = s.recv(1000000000)
            log("Got ", num_results, "Results")

    def open_file(self, event=""):
        try:
            index = int(self.multi_list_box.curselection()[0])
            path = self.multi_list_box.get(index)[2]
            subprocess.Popen(path, shell=True)
        except IndexError:
            pass

    def open_folder(self, event=""):
        path = ""
        try:
            index = int(self.multi_list_box.curselection()[0])
            path = self.multi_list_box.get(index)[2]
        except IndexError:
            pass
        if path:
            if os.path.isfile(path):
                command = "explorer /Select, \"{0}\"".format(path)
                subprocess.Popen(command, shell=True)
            else:
                print "Could not open", path, "(Does not seem to exist)"

    def show_version(self):
        frmMain = tk.Tk()
        label = tk.Label(frmMain, text="Version:\n" + self.version)
        label.pack()
        frmMain.mainloop()


    def show_help(self):
        frmMain = tk.Tk()
        label = tk.Label(frmMain, text="Version:\n" + self.version)
        label.pack()
        frmMain.mainloop()

    def onQuit(self):
        print "User aborted, quitting."
        self.window.destroy()
        os._exit(1)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    a = Window()
    a.start()
