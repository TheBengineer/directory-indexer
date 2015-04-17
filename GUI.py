__author__ = 'boh01'

from threading import Thread
import os
import Tkinter as tk
import tkFileDialog
import subprocess

import Scanner


class Window(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.scanner = Scanner.Scanner()
        self.scanner.start()

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
        self.results_paned = tk.PanedWindow(self.results_frame, orient=tk.HORIZONTAL)
        self.results_paned.config(borderwidth=5, handlesize=15, showhandle=1, opaqueresize=1, width=250)

        self.results_paned.config(borderwidth=4, relief=tk.GROOVE)
        self.results_options_frame = tk.Frame(self.results_frame)
        self.open_file_button = tk.Button(self.results_options_frame, text="Open File", command=self.open_file)
        self.open_folder_button = tk.Button(self.results_options_frame, text="Open Folder", command=self.open_folder)
        self.open_file_button.pack(side=tk.LEFT)
        self.open_folder_button.pack(side=tk.LEFT)
        self.results_options_frame.pack()

        # ################ Results Scroll Box

        self.results_frame_scroll_left = tk.Frame(self.results_paned)  # select of names
        self.results_frame_scroll_right = tk.Frame(self.results_paned)  # select of names
        self.scrollL = tk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.yview)
        self.folders_listbox = tk.Listbox(self.results_frame_scroll_left, yscrollcommand=self.a, height=6,
                                          activestyle='dotbox', exportselection=0)
        self.files_listbox = tk.Listbox(self.results_frame_scroll_right, yscrollcommand=self.a, height=6,
                                        activestyle='dotbox', exportselection=0)
        self.scrollL.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_label = tk.Label(self.results_frame, text="Files matching search")
        self.results_label.pack(side=tk.TOP, fill=tk.X)
        self.results_paned.pack(fill=tk.BOTH, expand=1)
        self.results_paned.add(self.results_frame_scroll_right)
        self.results_paned.add(self.results_frame_scroll_left)
        self.results_frame_scroll_left.pack_propagate(0)
        self.results_frame_scroll_left.config(width=300)
        self.results_frame_scroll_right.pack_propagate(0)
        self.results_frame_scroll_right.config(width=300)
        self.folders_listbox.config(width=300)
        self.files_listbox.config(width=300)
        self.files_listbox.pack(fill=tk.Y, side=tk.LEFT)
        self.folders_listbox.pack(fill=tk.Y, expand=1)
        self.folders_listbox.bind('<Double-Button-1>', self.open_file)
        self.files_listbox.bind('<Double-Button-1>', self.open_file)
        self.folders_listbox.bind('<Button-3>', self.open_folder)
        self.files_listbox.bind('<Button-3>', self.open_folder)
        self.folders_listbox.bind('<MouseWheel>', self.on_scroll)
        self.files_listbox.bind('<MouseWheel>', self.on_scroll)
        # self.folders_listbox.bind('<Button-4>', self.scroll_up)
        #self.files_listbox.bind('<Button-4>', self.scroll_up)
        #self.folders_listbox.bind('<Button-5>', self.scroll_down)
        #self.files_listbox.bind('<Button-5>', self.scroll_down)

        self.results_frame.pack(fill=tk.BOTH, expand=1)

        # Tab order

        self.search_text.focus()

    def a(self, asdf=0, asdf2=0):
        print "here"


    def yview(self, *args):
        """connect the yview action together"""
        self.folders_listbox.yview(*args)
        self.files_listbox.yview(*args)

    def on_scroll(self, event, delta=0):
        self.folders_listbox.yview("scroll", -int(event.delta / 10), "units")
        self.files_listbox.yview("scroll", -int(event.delta / 10), "units")

    def scroll_up(self, event):
        self.folders_listbox.yview("scroll", 1, "units")
        self.files_listbox.yview("scroll", 1, "units")

    def scroll_down(self, event):
        self.folders_listbox.yview("scroll", -1, "units")
        self.files_listbox.yview("scroll", -1, "units")

    def start_scan(self, event=""):
        path = self.scan_text.get()
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
        self.folders_listbox.delete(0, tk.END)
        self.files_listbox.delete(0, tk.END)
        for result in results:
            text = os.path.join(result[0], result[1])
            self.folders_listbox.insert(0, text)
            self.files_listbox.insert(0, result[1])

    def open_file(self, event=""):
        try:
            index = int(self.folders_listbox.curselection()[0])
            path = self.folders_listbox.get(index)
            subprocess.Popen(path, shell=True)
        except IndexError:
            pass

    def open_folder(self, event=""):
        path = ""
        try:
            index = int(self.folders_listbox.curselection()[0])
            path = self.folders_listbox.get(index)
        except IndexError:
            pass
        if path:
            folder_path, filename = os.path.split(path)
            command = "explorer /Select, \"{0}\"".format(path)
            subprocess.Popen(command, shell=True)


    def onQuit(self):
        print "User aborted, quitting."
        self.scanner.directory_database.go = 0
        self.window.destroy()
        os._exit(1)

    def run(self):
        self.window.mainloop()


class dual_lists():

    def __init__(self, root):

        self.frame = Frame(root, borderwidth=1, relief=GROOVE)
        self.frame.pack()
        self.frame.place(x=40, y=40)

        self.scrollbar = Scrollbar(self.frame, orient=VERTICAL, command=self.OnVsb)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.listbox1 = Listbox(self.frame, font=('Courier', 12, 'roman'),
            width=16, height=6)
        self.listbox1.pack(side=LEFT, fill=Y)

        self.listbox2 = Listbox(self.frame, font=('Courier', 12, 'roman'),
            width=16, height=6)
        self.listbox2.pack(side=LEFT, fill=Y)

        self.listbox1.configure(yscrollcommand=self.scrollbar.set)
        self.listbox2.configure(yscrollcommand=self.scrollbar.set)

        closeBtn = tk.Button(padx = 4, pady = 4, text = "Exit",
            font=('Helvetica', 12), command = self.close_window)
        closeBtn.pack()
        closeBtn.place(x=20, y=200)

        txt = 'Click on a listbox and use these keys to scroll:\n' + \
              'Home, End, PageUp, PageDown,\n' \
              'UpArrow, DownArrow, and the Mousewheel'
        tk.Label(root, text=txt, font=('Helvetica', 10)).place(x=90, y=180)

        for n in range(64+26, 64, -1):
            self.listbox1.insert(0, chr(n)+'able')
            self.listbox2.insert(0, chr(n)+'able')

        self.listbox1.bind('<Up>', lambda event: self.scroll_listboxes(-1))
        self.listbox2.bind('<Up>', lambda event: self.scroll_listboxes(-1))
        self.listbox1.bind('<Down>', lambda event: self.scroll_listboxes(1))
        self.listbox2.bind('<Down>', lambda event: self.scroll_listboxes(1))

        self.listbox1.bind('<End>', self.end_pressed)
        self.listbox2.bind('<End>', self.end_pressed)
        self.listbox1.bind('<Home>', self.home_pressed)
        self.listbox2.bind('<Home>', self.home_pressed)

        self.listbox1.bind('<Next>', self.pgdown_pressed)
        self.listbox2.bind('<Next>', self.pgdown_pressed)
        self.listbox1.bind('<Prior>', self.pgup_pressed)
        self.listbox2.bind('<Prior>', self.pgup_pressed)

        self.listbox1.bind("<MouseWheel>", self.OnMouseWheel)
        self.listbox2.bind("<MouseWheel>", self.OnMouseWheel)

        self.listbox1.focus_set()  #set up listbox1 for immediate scrolling
        self.listbox1.activate(0)  #first scrolling will scroll away from listbox item #1

    def OnMouseWheel(self, event):
        if event.num == 5 or event.delta == -120:
            yFactor = 1
        else:
            yFactor = -1
        self.listbox1.yview("scroll", yFactor, "units")
        self.listbox2.yview("scroll", yFactor, "units")
        return "break"

    def OnVsb(self, *args):    #vertical scrollbar position changed
        self.listbox1.yview(*args)
        self.listbox2.yview(*args)

    def home_pressed(self, event):
        self.listbox1.see(0)
        self.listbox1.activate(0)    #added
        self.listbox2.see(0)
        self.listbox2.activate(0)    #added
        self.clear_sel()

    def end_pressed(self, event):
        lboxSize = self.listbox1.size()
        self.listbox1.see(lboxSize)
        self.listbox1.activate(lboxSize)    #added
        self.listbox2.see(lboxSize)
        self.listbox2.activate(lboxSize)    #added
        self.clear_sel()

    def pgup_pressed(self, event):
        self.listbox1.yview_scroll(-(self.listbox1['height']), "units")
        self.listbox2.yview_scroll(-(self.listbox2['height']), "units")
        self.clear_sel()
        return "break"

    def pgdown_pressed(self, event):
        self.listbox1.yview_scroll(self.listbox1['height'], "units")
        self.listbox2.yview_scroll(self.listbox2['height'], "units")
        self.clear_sel()
        return "break"

    def scroll_listboxes(self, yFactor):
        #function runs when a listbox has focus and the Up or Down arrow keys are pressed
        self.listbox1.yview_scroll(yFactor, "units")
        self.listbox2.yview_scroll(yFactor, "units")

    def clear_sel(self):
        self.listbox1.selection_clear(0, tk.END)
        self.listbox2.selection_clear(0, tk.END)

    def close_window(self):
        root.destroy()
