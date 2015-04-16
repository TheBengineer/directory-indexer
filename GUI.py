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

        self.scanner = DirectoryDB.DirectoryDB("C:/tmp/Monster.db")

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
        self.scan_button = tk.Button(self.scan_frame, text="Scan", command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT)
        self.scan_text = tk.Entry(self.scan_frame, font="courier 14")
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
        self.results_listbox.bind('<Double-Button-1>', self.a)

        self.results_frame.pack(fill=tk.BOTH, expand=1)

        # Tab order

        self.search_text.focus()

    def a(self, asdf):
        pass

    def start_scan(self):
        path = self.scan_text.get()
        print "Would now scan ", path
        # TODO make this start a scan running.

    def browse_scan_path(self):
        fullpath = tkFileDialog.askdirectory(initialdir="C:")
        self.scan_text.insert(0, fullpath)

    def search(self, event=""):
        search_text = self.search_text.get()
        results = self.scanner.get_folders("%" + search_text + "%")
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

    def open_folder(self):
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


    def startGetRMA(self):
        self.RMAThread.state = 0
        self.RMAThread.go = 1
        try:
            self.RMAThread.start()
        except RuntimeError:
            self.RMAThread.go = 0
            self.RMAThread = RMAstripper.getRMAs(self.startRMABar, self.status, self)  # the RMA getting thread
            self.RMAThread.state = 0
            self.RMAThread.substate = 0
            self.RMAThread.go = 1

        self.startRMA.config(text="Use latest RMA file", command=self.stopGetRMA)

    def getFileName(self):
        fullpath = tkFileDialog.askopenfilename(initialdir=self.RMAThread.DLpath,
                                                filetypes=(("Comma Separated Values", ".csv"), ("All Files", "*.*")))
        path, filename = os.path.split(fullpath)
        if filename != "":
            self.status["text"] = "Status: Using " + filename
            self.RMAThread.DLpath = path
            self.RMAThread.ticketFN = filename
            self.RMAThread.state = 3
            self.RMAThread.gp = 1
            try:
                self.RMAThread.start()
            except RuntimeError:
                self.RMAThread.go = 0
                self.RMAThread = RMAstripper.getRMAs(self.startRMABar, self.status, self)  # the RMA getting thread
                self.status["text"] = "Status: Using " + filename
                self.RMAThread.DLpath = path
                self.RMAThread.ticketFN = filename
                self.RMAThread.state = 3
                self.RMAThread.go = 1
                self.RMAThread.start()

    def shortcutRMA(self):
        self.RMAThread.state = 2
        self.RMAThread.go = 1
        try:
            self.RMAThread.start()
        except RuntimeError:
            self.RMAThread.go = 0
            self.RMAThread = RMAstripper.getRMAs(self.startRMABar, self.status, self)  # the RMA getting thread
            self.RMAThread.state = 2
            self.RMAThread.go = 1
            self.RMAThread.start()


    def updateLeftoutdated(self):
        self.RMALockL.acquire()
        self.RMAListBoxL.delete(0, tk.END)
        for i in self.RMAlist:
            RMA = self.RMAlist[i]
            text = " " + str(RMA["TICKET"]) + ": " + str(RMA["RMA"]) + "  " + str(RMA["DESC"])
            self.RMAListBoxL.insert(tk.END, text)
        self.RMALockL.release()

    def updateLeft(self):
        self.RMALockL.acquire()
        self.RMAListBoxL.delete(0, tk.END)
        if len(self.VisThread.uncheckedRMANums) == 0:
            self.RMALockL.release()
            self.updateLeftoutdated()
        else:
            for i in self.VisThread.uncheckedRMANums:
                RMA = self.VisThread.uncheckedRMANums[i]
                text = " " + str(RMA["TICKET"]) + ": " + str(RMA["RMA"]) + "  " + str(RMA["DESC"])
                # print "Adding to list:",text
                self.RMAListBoxL.insert(tk.END, text)
        self.RMALockL.release()

    def updateMiddle(self):
        self.RMALock2.acquire()
        self.RMAListBox2.delete(0, tk.END)
        tmp2 = self.SHaG.checkedRMANums.copy()
        tmp = []
        for i in tmp2:
            tmp.append((i, tmp2[i]["CSV"][14]))
        tmp.sort()
        for i, j in tmp:
            RMA = tmp2[i]
            text = " " + str(RMA["TICKET"]) + ": " + str(RMA["RMA"]) + "  Has not been received for " + str(
                RMA["CSV"][14]) + " days"
            # print "Adding to list:",text
            if RMA["RESULT"] == []:
                self.RMAListBox2.insert(tk.END, text)
        self.RMALock2.release()

    def updateRight(self):
        self.RMALockR.acquire()
        self.RMAListBoxR.delete(0, tk.END)
        for i in self.VisThread.checkedRMANums:
            RMA = self.VisThread.checkedRMANums[i]
            text = " " + str(RMA["TICKET"]) + ": " + str(RMA["RMA"]) + " " + str(RMA["DESC"])
            self.RMAListBoxR.insert(tk.END, text)
        self.RMALockR.release()

    def onselectL(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        self.RMALockR.acquire()
        w = evt.widget
        try:
            index = int(w.curselection()[0])
            value = w.get(index)
            RMA = int(value[6:14])
            string = str(RMA) + "-1;7;2" + ent
            self.window.clipboard_clear()
            self.window.clipboard_append(string)
            self.onCopy(string)
        except IndexError:
            pass
        finally:
            self.RMALockR.release()

    def onselectVis(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        self.RMALock2.acquire()
        w = evt.widget
        try:
            index = int(w.curselection()[0])
            value = w.get(index)
            RMA = int(value[6:14])
            string = str(RMA) + "-1;7;2" + ent + ent
            self.window.clipboard_clear()
            self.window.clipboard_append(string)
            self.onCopy(string)
        except IndexError:
            pass
        finally:
            self.RMALock2.release()

    def onselectR(self, evt):
        # Note here that Tkinter passes an event object to onselect()
        self.RMALockR.acquire()
        w = evt.widget
        try:
            index = int(w.curselection()[0])
            value = w.get(index)
            tk = int(value[:5])
            RMA = int(value[6:14])
            if self.RMAlist[RMA]["TN"] != "":
                string = "This RMA shipped back on " + self.RMAlist[RMA]["SD"] + " via UPS.\nTracking number: " + \
                         self.RMAlist[RMA]["TN"]
                self.window.clipboard_clear()
                self.window.clipboard_append(string)
                self.onCopy(string)
        except IndexError:
            pass
        finally:
            self.RMALockR.release()


    def openTicket(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        tk = int(value[:5])
        RMA = int(value[6:14])
        ticket = "https://app.teamsupport.com/?TicketNumber=" + str(tk)
        os.system("start chrome \"" + ticket + "\"")
        if self.RMAlist[RMA]["TN"] != "":
            string = "This RMA shipped back on " + self.RMAlist[RMA]["SD"] + " via UPS.\nTracking number: " + \
                     self.RMAlist[RMA]["TN"]
            self.window.clipboard_clear()
            self.window.clipboard_append(string)
            self.onCopy(string)

    def onCopy(self, text):
        oldText = self.status["text"]
        text = text.rstrip()
        self.status["text"] = "Status: Set paste buffer to: " + text
        self.status["bg"] = "pale green"
        self.window.after(1000, self.onUnCopy, oldText)

    def onUnCopy(self, text):
        self.status["text"] = text
        self.status["bg"] = "SystemButtonFace"


    def onQuit(self):
        print "User aborted, quitting."
        # self.RMAThread.interrupt_main()
        # self.VisThread.interrupt_main()
        self.window.destroy()

        os._exit(1)

    def run(self):
        self.window.mainloop()


a = Window()
a.start()