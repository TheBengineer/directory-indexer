__author__ = 'boh01'

from threading import Thread
import os
import Tkinter as tk
import tkFileDialog
import subprocess

import DirectoryDB


class Window(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.window = tk.Tk()  # Init
        self.window.geometry("800x500+300+300")
        self.window.title("Fujifilm Dimatix File Index Database - Ben Holleran April 2014")
        self.window.protocol("WM_DELETE_WINDOW", self.onQuit)

        self.Directory_index_database = DirectoryDB.DirectoryDB("C:/tmp/Monster.db")
        self.Directory_index_database.start()
        # self.directory_indexer = Directory.Directory()

        # ################ Menu

        self.menu = tk.Menu(self.window)
        self.window.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=self.window.quit)

        self.edit_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)

        self.help_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About")  # TODO add an about window here.

        # ################ Scan

        self.scan_frame = tk.Frame(self.window)
        self.scan_frame.config()
        self.scan_button = tk.Button(self.scan_frame, text="Index", command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT)
        self.scan_text = tk.Entry(self.scan_frame, font="courier 14")
        self.scan_text.bind('<Return>', self.start_scan)
        self.scan_text.config(width=300)
        self.scan_browse = tk.Button(self.scan_frame, text="Browse", command=self.browse_scan_path)
        self.scan_browse.pack(side=tk.RIGHT)
        self.scan_text.pack()
        self.scan_frame.pack(fill=tk.X)

        self.scan_status_frame = tk.Frame(self.window)
        self.scan_status = tk.Label(self.scan_status_frame, text="Status:", justify=tk.LEFT)
        self.scan_status.pack(side=tk.LEFT)
        self.scan_status_frame.pack(fill=tk.X)


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
        self.results_frame.config(borderwidth=4, relief=tk.GROOVE)
        self.results_options_frame = tk.Frame(self.results_frame)
        self.open_file_button = tk.Button(self.results_options_frame, text="Open File", command=self.open_file)
        self.open_folder_button = tk.Button(self.results_options_frame, text="Open Folder", command=self.open_folder)
        self.open_file_button.pack(side=tk.LEFT)
        self.open_folder_button.pack(side=tk.LEFT)
        self.results_options_frame.pack()

        # ################ Results Scroll Box

        self.results_frame_scroll = tk.Frame(self.results_frame)  # select of names
        self.scrollL = tk.Scrollbar(self.results_frame_scroll, orient=tk.VERTICAL)
        self.results_listbox = tk.Listbox(self.results_frame_scroll, yscrollcommand=self.scrollL.set, height=6,
                                          activestyle='dotbox')
        self.scrollL.config(command=self.results_listbox.yview)
        self.scrollL.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_label = tk.Label(self.results_frame, text="Files matching search")
        self.results_label.pack(side=tk.TOP, fill=tk.BOTH)
        self.results_frame_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.results_listbox.config(width=300)
        self.results_listbox.pack(fill=tk.Y, expand=1)
        # self.results_listbox.bind('<<ListboxSelect>>', self.a) # No single click action needed
        self.results_listbox.bind('<Double-Button-1>', self.open_folder)

        self.results_frame.pack(fill=tk.BOTH, expand=1)

        # Tab order

        self.search_text.focus()

    def a(self, asdf):
        pass

    def start_scan(self, event=""):
        path = self.scan_text.get()
        print "Would now scan ", path
        # TODO make this start a scan running.

    def browse_scan_path(self):
        fullpath = tkFileDialog.askdirectory(initialdir="C:")
        self.scan_text.insert(0, fullpath)

    def search(self, event=""):
        search_text = self.search_text.get()
        results = self.Directory_index_database.get_folders("%" + search_text + "%")
        self.results_listbox.delete(0, tk.END)
        for result in results:
            self.results_listbox.insert(0, os.path.join(result[0], result[1]))

    def open_file(self):
        try:
            index = int(self.results_listbox.curselection()[0])
            path = self.results_listbox.get(index)
            subprocess.Popen(path, shell=True)
        except IndexError:
            pass

    def open_folder(self, event=""):
        path = ""
        try:
            index = int(self.results_listbox.curselection()[0])
            path = self.results_listbox.get(index)
        except IndexError:
            pass
        if path:
            folder_path, filename = os.path.split(path)
            command = "explorer /Select, \"{0}\"".format(path)
            subprocess.Popen(command, shell=True)


    def onQuit(self):
        print "User aborted, quitting."
        self.Directory_index_database.go = 0
        self.window.destroy()
        os._exit(1)

    def run(self):
        self.window.mainloop()
