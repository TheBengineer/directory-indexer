
######################################################################
#
#    File:       mhMultiListBox.py
#
#    Purpose:    Multi-column list box.  Acts mostly like a regular
#                tkinter listbox + scrollbar, but supports multiple
#                columns with heading labels.
#
#                o Enhanced version of MultiListBox.py by Bob Hauck
#                  which can be found at <http://www.haucks.org/>
#                o Based on work by Brent Burley found at:
#                  
#<http://aspn.activestate.com/ASPN/Python/Cookbook/Recipe/52266>
#                o Uses code of SortedTable by Rick Lawson found at
#                  <http://tkinter.unpythonic.net/wiki/SortableTable>
#
#                Features:
#                  o Can call a command on <return> or double-click.
#                  o Grabs focus when clicked.
#                  o Columns are resizable.
#                  o Properly handles keyboard navigation.
#                  o Sorts when solumn labels are clicked.
#                  o Includes a vertical scrollbar.
#                  o No external libraries except tkinter.
#                   
#                Limitations:
#                  o Only single selection.
#                  o No horizontal scrolling.
#                  o Vertical scrollbar is always present.
#
#    Language:   Python 2.3
#
#    Author:     Bob Hauck
#    Copyright 2001, Codem Systems Inc.,  All rights reserved.
#
#    Codem Systems, Inc.
#    7 Executive Park Drive, 
#    Merrimack, NH  03054
#
# License
# -------
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the author nor the names of any contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# Warranty
# --------
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
######################################################################
from Tkinter import *

MOVE_LINES = 0
MOVE_PAGES = 1
MOVE_TOEND = 2

class MultiListbox(Frame):
    """
    MultiListbox Class.

    Defines a multi-column listbox.  The constructor takes a list of
    tuples, where each tuple is (column-label, character-width).  The
    list will have as many columns as tuples.  Add items to the list by
    passing tuples or lists of items, one for each column.

    Each column will be given the specified width in character units,
    with a header of column-label.  Also takes many of the normal
    Listbox options for background, font, etc.
    """
    def __init__(self, master, lists, command=None, **options):
        defaults = {
            'background': None,
            'borderwidth': 2,
            'font': None,
            'foreground': None,
            'height': 10,
            'highlightcolor': None,
            'highlightthickness': 1,
            'relief': SUNKEN,
            'takefocus': 1,
            }

        aliases = {'bg':'background', 'fg':'foreground', 'bd':'borderwidth'}

        for k in aliases.keys ():
            if options.has_key (k):
                options [aliases[k]] = options [k]
            
        for key in defaults.keys():
            if not options.has_key (key):
                options [key] = defaults [key]

        apply (Frame.__init__, (self, master), options)
        self.lists = []

        # MH (05/20049
        # These are needed for sorting
        self.colmapping={}
        self.origData = None

        #  Keyboard navigation.
        
        self.bind ('<Up>',    lambda e, s=self: s._move (-1, MOVE_LINES))
        self.bind ('<Down>',  lambda e, s=self: s._move (+1, MOVE_LINES))
        self.bind ('<Prior>', lambda e, s=self: s._move (-1, MOVE_PAGES))
        self.bind ('<Next>',  lambda e, s=self: s._move (+1, MOVE_PAGES))
        self.bind ('<Home>',  lambda e, s=self: s._move (-1, MOVE_TOEND))
        self.bind ('<End>',   lambda e, s=self: s._move (+1, MOVE_TOEND))
        if command:
            self.bind ('<Return>', command)

        # Columns are a frame with listbox and label in it.
        
        # MH (05/2004):
        # Introduced a PanedWindow to make the columns resizable
        
        m = PanedWindow(self, orient=HORIZONTAL, bd=0, 
background=options['background'], showhandle=0, sashpad=1)
        m.pack(side=LEFT, fill=BOTH, expand=1)

        for label, width in lists:
            lbframe = Frame(m)
            m.add(lbframe, width=width)
            # MH (05/2004)
            # modified this, click to sort
            b = Label(lbframe, text=label, borderwidth=1, relief=RAISED)
            b.pack(fill=X)
            b.bind('<Button-1>', self._sort)

            self.colmapping[b]=(len(self.lists),1)
            
            lb = Listbox (lbframe,
                          width=width,
                          height=options ['height'],
                          borderwidth=0,
                          font=options ['font'],
                          background=options ['background'],
                          selectborderwidth=0,
                          relief=SUNKEN,
                          takefocus=FALSE,
                          exportselection=FALSE)
            lb.pack (expand=YES, fill=BOTH)
            self.lists.append (lb)

            # Mouse features
            
            lb.bind ('<B1-Motion>', lambda e, s=self: s._select (e.y))
            lb.bind ('<Button-1>',  lambda e, s=self: s._select (e.y))
            lb.bind ('<Leave>',     lambda e: 'break')
            lb.bind ('<B2-Motion>', lambda e, s=self: s._b2motion (e.x, e.y))
            lb.bind ('<Button-2>',  lambda e, s=self: s._button2 (e.x, e.y))
            if command:
                lb.bind ('<Double-Button-1>', command)

        sbframe = Frame (self)
        sbframe.pack (side=LEFT, fill=Y)
        l = Label (sbframe, borderwidth=1, relief=RAISED)
        l.bind ('<Button-1>', lambda e, s=self: s.focus_set ())
        l.pack(fill=X)
        sb = Scrollbar (sbframe,
                        takefocus=FALSE,
                        orient=VERTICAL,
                        command=self._scroll)
        sb.pack (expand=YES, fill=Y)
        self.lists[0]['yscrollcommand']=sb.set

        return


    # MH (05/2004)
    # Sort function, adopted from Rick Lawson 
    # http://tkinter.unpythonic.net/wiki/SortableTable
    
    def _sort(self, e):
        # get the listbox to sort by (mapped by the header button)
        b=e.widget
        col, direction = self.colmapping[b]

        # get the entire table data into mem
        tableData = self.get(0,END)
        if self.origData == None:
            import copy
            self.origData = copy.deepcopy(tableData)

        rowcount = len(tableData)

        #remove old sort indicators if it exists
        for btn in self.colmapping:
            lab = btn.cget('text')
            if lab[0]=='[': btn.config(text=lab[4:])

        btnLabel = b.cget('text')
        #sort data based on direction
        if direction==0:
            tableData = self.origData
        else:
            if direction==1: b.config(text='[+] ' + btnLabel)
            else: b.config(text='[-] ' + btnLabel)
            # sort by col
            tableData.sort(key=lambda x: x[col], reverse=direction<0)

        #clear widget
        self.delete(0,END)

        # refill widget
        for row in range(rowcount):
            self.insert(END, tableData[row])

        # toggle direction flag 
        if direction==1: direction=-1
        else: direction += 1
        self.colmapping[b] = (col, direction) 
        

    def _move (self, lines, relative=0):
        """
        Move the selection a specified number of lines or pages up or
        down the list.  Used by keyboard navigation.
        """
        selected = self.lists [0].curselection ()
        try:
            selected = map (int, selected)
        except ValueError:
            pass

        try:
            sel = selected [0]
        except IndexError:
            sel = 0

        old  = sel
        size = self.lists [0].size ()
        
        if relative == MOVE_LINES:
            sel = sel + lines
        elif relative == MOVE_PAGES:
            sel = sel + (lines * int (self.lists [0]['height']))
        elif relative == MOVE_TOEND:
            if lines < 0:
                sel = 0
            elif lines > 0:
                sel = size - 1
        else:
            print "MultiListbox._move: Unknown move type!"

        if sel < 0:
            sel = 0
        elif sel >= size:
            sel = size - 1
        
        self.selection_clear (old, old)
        self.see (sel)
        self.selection_set (sel)
        return 'break'


    def _select (self, y):
        """
        User clicked an item to select it.
        """
        row = self.lists[0].nearest (y)
        self.selection_clear (0, END)
        self.selection_set (row)
        self.focus_set ()
        return 'break'


    def _button2 (self, x, y):
        """
        User selected with button 2 to start a drag.
        """
        for l in self.lists:
            l.scan_mark (x, y)
        return 'break'


    def _b2motion (self, x, y):
        """
        User is dragging with button 2.
        """
        for l in self.lists:
            l.scan_dragto (x, y)
        return 'break'


    def _scroll (self, *args):
        """
        Scrolling with the scrollbar.
        """
        for l in self.lists:
            apply(l.yview, args)

    def curselection (self):
        """
        Return index of current selection.
        """
        return self.lists[0].curselection()


    def delete (self, first, last=None):
        """
        Delete one or more items from the list.
        """
        for l in self.lists:
            l.delete(first, last)


    def get (self, first, last=None):
        """
        Get items between two indexes, or one item if second index
        is not specified.
        """
        result = []
        for l in self.lists:
            result.append (l.get (first,last))
        if last:
            return apply (map, [None] + result)
        return result

            
    def index (self, index):
        """
        Adjust the view so that the given index is at the top.
        """
        for l in self.lists:
            l.index (index)


    def insert (self, index, *elements):
        """
        Insert list or tuple of items.
        """
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert (index, e[i])
                i = i + 1
        if self.size () == 1:
            self.selection_set (0)
            

    def size (self):
        """
        Return the total number of items.
        """
        return self.lists[0].size ()


    def see (self, index):
        """
        Make sure given index is visible.
        """
        for l in self.lists:
            l.see (index)


    def selection_anchor (self, index):
        """
        Set selection anchor to index.
        """
        for l in self.lists:
            l.selection_anchor (index)


    def selection_clear (self, first, last=None):
        """
        Clear selections between two indexes.
        """
        for l in self.lists:
            l.selection_clear (first, last)


    def selection_includes (self, index):
        """
        Determine if given index is selected.
        """
        return self.lists[0].selection_includes (index)


    def selection_set (self, first, last=None):
        """
        Select a range of indexes.
        """
        for l in self.lists:
            l.selection_set (first, last)


if __name__ == '__main__':
    tk = Tk()
    Label(tk, text='MultiListbox').pack()
    mlb = MultiListbox (tk,
                        (('Subject', 150),
                         ('Sender', 100),
                         ('Date', 100)),
                        height=20,
                        bg='white')
    for i in range (100):
        mlb.insert (END, ('Important Message: %d' % i,
                          'John Doe',
                          '10/10/%04d' % (1900+i)))
    mlb.pack (expand=YES,fill=BOTH)
    Button (tk, text="button").pack ()
    tk.mainloop()