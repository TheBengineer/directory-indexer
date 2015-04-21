__author__ = 'boh01'

from threading import Thread
import os
import Tkinter as tk
import tkFileDialog
import subprocess

import Scanner
import mhMultiListBox


class Window(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.scanner = Scanner.Scanner(self)
        self.version = "Beta"

        self.window = tk.Tk()  # Init
        self.window.geometry("800x500+300+300")
        self.window.title("Fujifilm Dimatix File Index Database - Ben Holleran April 2014")
        self.window.protocol("WM_DELETE_WINDOW", self.onQuit)

        # self.Directory_index_database = DirectoryDB.DirectoryDB("C:/tmp/Monster.db")
        # self.Directory_index_database.start()
        # self.directory_indexer = Directory.Directory()

        # ################ Menu

        self.menu = tk.Menu(self.window)
        self.window.config(menu=self.menu)
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=self.window.quit)

        #self.edit_menu = tk.Menu(self.menu)
        #self.menu.add_cascade(label="Edit", menu=self.edit_menu)

        self.help_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_version)

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

        #self.multi_list_box.colmapping['Files'].bind('<Double-Button-1>', self.open_file)
        self.multi_list_box.bind('<Double-Button-1>', self.open_file)
        self.multi_list_box.bind('<Button-3>', self.open_folder)
        #self.files_listbox.bind('<Button-3>', self.open_folder)
        #self.folders_listbox.bind('<MouseWheel>', self.on_scroll)
        #self.files_listbox.bind('<MouseWheel>', self.on_scroll)
        # self.folders_listbox.bind('<Button-4>', self.scroll_up)
        #self.files_listbox.bind('<Button-4>', self.scroll_up)
        #self.folders_listbox.bind('<Button-5>', self.scroll_down)
        #self.files_listbox.bind('<Button-5>', self.scroll_down)

        self.results_frame.pack(fill=tk.BOTH, expand=1)

        # Tab order

        self.search_text.focus()
        self.scanner.start()

    def a(self, asdf=0, asdf2=0):
        print "here"


    def set_status(self, status):
        self.scan_status["text"] = status

    def start_scan(self, event=""):
        path = self.scan_text.get()
        # self.set_status("Scanning: " + path)
        if os.path.isdir(path):
            self.scanner.scan_dir(path)
        else:
            print "Path does not exist for scanning:", path

    def browse_scan_path(self):
        fullpath = tkFileDialog.askdirectory(initialdir="C:")
        self.scan_text.insert(0, fullpath)

    def search(self, event=""):
        search_text = self.search_text.get()
        results = self.scanner.directory_database.get_folders("%" + search_text + "%")
        self.multi_list_box.delete(0, tk.END)
        for result in results:
            text = (
            result[1], result[1][result[1].rfind(".") + 1:].upper(), os.path.join(result[0], result[1]).replace("/", "\\"))
            self.multi_list_box.insert(0, text)

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
            folder_path, filename = os.path.split(path)
            command = "explorer /Select, \"{0}\"".format(path)
            subprocess.Popen(command, shell=True)

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
        self.scanner.directory_database.go = 0
        self.window.destroy()
        os._exit(1)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    a = Window()
    a.start()
