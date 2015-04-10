__author__ = 'boh01'

from threading import Thread
import os
import Tkinter as tk


class Window(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.window = tk.Tk()  # Init
        self.window.geometry("400x500+300+300")
        self.window.title("Fujifilm Dimatix File Index Database - Ben Holleran April 2014")
        self.window.protocol("WM_DELETE_WINDOW", self.onQuit)

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

        ################# Scan

        self.scan_frame = tk.Frame(self.window)
        self.scan_frame.config()
        self.scan_button = tk.Button(self.scan_frame, text="Scan")
        self.scan_button.pack(side=tk.LEFT)
        self.scan_text = tk.Entry(self.scan_frame, font="courier 13")
        self.scan_text.config(width=300)
        self.scan_browse = tk.Button(self.scan_frame, text="Browse")
        self.scan_browse.pack(side=tk.RIGHT)
        self.scan_text.pack()
        self.scan_frame.pack(fill=tk.X)

        self.scan_status_frame = tk.Frame(self.window)
        self.scan_status_frame.config(relief=tk.GROOVE)
        self.scan_status = tk.Label(self.scan_status_frame, text="Status:", justify=tk.LEFT)
        self.scan_status.pack()
        self.scan_status_frame.pack(fill=tk.X)


        ################# Search

        self.search_frame = tk.Frame(self.window)
        self.search_frame.config(borderwidth=4, relief=tk.GROOVE)
        self.search_button = tk.Button(self.search_frame, text="Search")
        self.search_text = tk.Entry(self.search_frame)
        self.search_button.pack()
        self.search_frame.pack()

        """
        self.mainFrame = tk.Frame(self.window)
        self.mainFrame.pack(fill=tk.BOTH, expand=1)

        self.menuFrame = tk.Frame(self.mainFrame)  # holds the buttons at the top

        self.add_path_frame = tk.Frame(self.menuFrame)  # Redundant?
        self.add_path_button = tk.Button(self.add_path_frame, text="Add Path")
        self.add_path_button.pack(fill=tk.BOTH, expand=1)
        self.add_path_button.pack_propagate(0)
        self.add_path_button.pack(side="left")
        self.startRMABar = ttk.Progressbar(self.menuFrame, orient='horizontal', mode='determinate', maximum=100)
        self.startRMABar.pack(expand=True, fill=tk.X, side="bottom")
        self.RMAButtonsFrame.pack(side="top")
        self.RMALatestButton = tk.Button(self.RMAButtonsFrame, text="Use latest ticket list")
        self.RMALatestButton.pack(side="left")
        self.RMAfileButton = tk.Button(self.RMAButtonsFrame, text="Select a ticket list")
        self.RMAfileButton.pack(side="left")
        self.launchPuttyB = tk.Button(self.RMAButtonsFrame, text="Launch Putty", command=self.launchPutty)
        self.launchPuttyB.pack(side="left")
        # End of Buttons
        self.status = tk.Label(self.window, text="Status: Waiting for a ticket list", bd=1, relief=tk.SUNKEN,
                               anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        # Menu bar for the top
        self.menuBar = tk.Menu(self.menuFrame)
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)
        self.window.config(menu=self.menuBar)
        self.menuFrame.pack(side="top")

        # Paned window
        self.mainWindow = tk.PanedWindow(self.mainFrame, orient=tk.HORIZONTAL)
        self.mainWindow.config(borderwidth=5, handlesize=15, showhandle=1, opaqueresize=1, width=250)
        self.mainWindow.pack(fill=tk.BOTH, expand=1)

        # Left side (Unscanned RMAS)
        self.RMAFrameLeft = tk.Frame(self.mainWindow)  # select of names
        self.scrollL = tk.Scrollbar(self.RMAFrameLeft, orient=tk.VERTICAL)
        self.RMAListBoxL = tk.Listbox(self.RMAFrameLeft, yscrollcommand=self.scrollL.set, height=6,
                                      activestyle='dotbox')
        self.scrollL.config(command=self.RMAListBoxL.yview)
        self.scrollL.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self.RMAFrameLeft, text="Unchecked RMAs").pack(side=tk.TOP, fill=tk.X)
        self.RMAListBoxL.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.RMAListBoxL.bind('<<ListboxSelect>>', self.onselectL)
        self.RMAListBoxL.bind('<Double-Button-1>', self.openTicket)

        # Not Recieved RMAs
        self.RMAFrame2 = tk.Frame(self.mainWindow)  # select of names
        self.scroll2 = tk.Scrollbar(self.RMAFrame2, orient=tk.VERTICAL)
        self.RMAListBox2 = tk.Listbox(self.RMAFrame2, yscrollcommand=self.scroll2.set, height=6, activestyle='dotbox')
        self.scroll2.config(command=self.RMAListBox2.yview)
        self.scroll2.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self.RMAFrame2, text="Outstanding RMAs").pack(side=tk.TOP, fill=tk.X)
        self.RMAListBox2.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        #self.RMAListBox2.bind('<<ListboxSelect>>', self.onselect2)
        self.RMAListBox2.bind('<Double-Button-1>', self.openTicket)
        #self.RMAListBox2.bind('<Button-3>', self.onselectVis)

        #Right side (Scanned RMAS)
        self.RMAFrameRight = tk.Frame(self.mainWindow)  # select of names
        self.scrollR = tk.Scrollbar(self.RMAFrameRight, orient=tk.VERTICAL)
        self.RMAListBoxR = tk.Listbox(self.RMAFrameRight, yscrollcommand=self.scrollR.set, height=6,
                                      activestyle='dotbox')
        self.scrollR.config(command=self.RMAListBoxR.yview)
        self.scrollR.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self.RMAFrameRight, text="Open tickets with shipped RMAs").pack(side=tk.TOP, fill=tk.X)
        self.RMAListBoxR.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.RMAListBoxR.bind('<<ListboxSelect>>', self.onselectR)
        self.RMAListBoxR.bind('<Double-Button-1>', self.openTicket)
        self.RMAListBoxR.bind('<Button-3>', self.onselectVis)
        self.RMALockR = Lock()



        #Add to Panes
        self.mainWindow.add(self.RMAFrameLeft)
        self.mainWindow.add(self.RMAFrame2)
        self.mainWindow.add(self.RMAFrameRight)
        self.RMAFrameLeft.pack_propagate(0)
        self.RMAFrameLeft.config(width=300)
        self.RMAFrame2.pack_propagate(0)
        self.RMAFrame2.config(width=300)
        self.RMALock2 = Lock()
        self.RMALockL = Lock()

        self.RMAThread = RMAstripper.getRMAs(self.startRMABar, self.status, self)  # the RMA getting thread
        self.startRMA.config(command=self.startGetRMA)
        self.RMALatestButton.config(command=self.shortcutRMA)
        self.fileMenu.add_command(label="Open", command=self.getFileName)
        self.RMAfileButton.config(command=self.getFileName)
        #self.RMAFrame.pack(fill=tk.BOTH,side="left",expand=1)
        #self.start()
        self.RMAlist = {}

    def launchPutty(self):
        self.putty.start()

    def stopParseRMA(self):
        self.RMAThread.go = 0
        self.startRMA.config(text="Quit Program", command=quit)

    def stopGetRMA(self):
        self.RMAThread.substate = 100
        self.startRMA.config(text="Launch Putty", command=self.openPutty)

    def openPutty(self):
        self.launchPutty()
        self.startRMA.config(text="Stop importing RMA numbers", command=self.stopParseRMA)


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

    """

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