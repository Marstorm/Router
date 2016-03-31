#
# Tkinter
# $Id$
#
# yet another an image viewer.  this one shows how to
# use the file dialogues and messages boxes, and also
# the incredibly nifty icon module (optional)
#
# written by Fredrik Lundh, February 1998
#
# Copyright (c) 1998 by Secret Labs AB.  Permission
#
# info@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted.  There are no warranties whatsoever.
# --------------------------------------------------------------------

from Tkinter import *
import Image, ImageTk

import tkFileDialog
import tkMessageBox

try:
    import tkIcon
except ImportError:
    tkIcon = None # no icon support

import os

#
# supported file formats (this is just a subset of what
# PIL actually supports)

IMTYPES = (
    ("All images", "*.bmp"),  ("BMP images", "*.bmp"),
    ("All images", "*.gif"),  ("GIF images", "*.gif"),
    ("All images", "*.png"),  ("PNG images", "*.png"),
    ("All images", "*.ppm"),  ("PPM images", "*.ppm"),
    ("All images", "*.pgm"),  ("PPM images", "*.pgm"),
    ("All images", "*.pbm"),  ("PPM images", "*.pbm"),
    ("All images", "*.tif"),  ("TIFF images", "*.tif"),
    ("All images", "*.tiff"), ("TIFF images", "*.tiff"),
    ("All images", "*.jpg"),  ("JPEG images", "*.jpg"),
    ("All images", "*.jpeg"), ("JPEG images", "*.jpeg"),
    ("All files", "*")
)

#
# an image viewer component

class View(Frame):

    def __init__(self, master):
	Frame.__init__(self, master, bd=2, relief=SUNKEN)

	self.label = Label(self)
	self.label.pack(fill=BOTH, expand=1)

	self.setimage(None)

    def setimage(self, im):

	if not im:
	    self.image = PhotoImage()
	    self.label.config(image=self.image, width=400, height=400,
			      bg="white", bd=0)
	    return

	if im.mode == "1":
            # bitmap image
	    self.image = ImageTk.BitmapImage(im, foreground="white")
        else:
            # photo image
            self.image = ImageTk.PhotoImage(im)

	self.label.config(image=self.image, bg="black", bd=0,
			  width=im.size[0], height=im.size[1])

#
# the main application

class App:

    def __init__(self, master=None):

	if not master:
	    master = Tk()

	self.master = master

	self.master.protocol("WM_DELETE_WINDOW", self.exit)

	# used to track window visibility
	self.master.bind("<Visibility>", self.visibility)

	#
	# create a menu

	self.menubar = Menu(self.master)
	
	filemenu = Menu(self.menubar, tearoff=0)
	filemenu.add_command(label="New", command=self.new)
	filemenu.add_command(label="Open...", command=self.open)
	filemenu.add_separator()
	filemenu.add_command(label="Exit", command=self.exit)

	self.menubar.add_cascade(label="File", menu=filemenu)

	self.view = View(self.master)
	self.view.pack(expand=1, fill=BOTH)

	try:
	    self.master.config(menu=self.menubar)
	except AttributeError:
	    # the config method is not available on master windows
	    # in older versions of Tkinter (like the one shipped
	    # with Python 1.4).  do it the hard way instead:
	    self.master.tk.call(self.master, "config", "-menu", self.menubar)

	#
	# create file dialogue

	self.importdialog = tkFileDialog.Open(
	    title="Open image",
	    filetypes=IMTYPES,
	    parent=self.master
        )

	# create a default icon (a yellow square).  note that
	# the icon image should be at least 32x32 pixels.

	if tkIcon:
	    image = Image.new("RGB", (32,32), (255, 255, 0))
	    self.icon = self.defaulticon = tkIcon.Icon(image)

	self.setimage(None)


    def visibility(self, event):

	# the visibility event is fired for the master widget
	# itself, and all its subwidgets.  the following test
	# makes sure we only change the icon when we really
	# need to

	if tkIcon and event.widget is self.master:
	    self.icon.attach(self.master)


    def setimage(self, image, filename = None):

	self.view.setimage(image)

	if tkIcon:
	    if not image:
		self.icon = self.defaulticon
	    else:
		self.icon = tkIcon.Icon(image)
	    self.icon.attach(self.master)

	if filename:
	    path, file = os.path.split(filename)
	    self.master.title("%s -- imageView" % file)
	else:
	    self.master.title("imageView")


    def new(self):

	self.setimage(None)

    def open(self):

        filename = self.importdialog.show()
        if not filename:
            return

	try:
	    image = Image.open(filename)
	except IOError:
	    tkMessageBox.showwarning(
		"Cannot open image",
		"Cannot open image file\n(%s)" % filename
	    )
	    return 0

	self.setimage(image, filename)


    def exit(self):

	self.master.destroy()


app = App()
mainloop()
