#
# tkIcon
# $Id$
#
# attach a user-defined icon to a Tk toplevel window.
#
# Copyright (c) Secret Labs AB 1998.
#
# info@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted.  There are no warranties whatsoever.
# --------------------------------------------------------------------
#


__version__ = "0.9"


import Image   # required support library (PIL)
import _tkicon # required support module


class Icon:

    def __init__(self, file_or_image):

	if type(file_or_image) == type(""):
	    i = Image.open(file_or_image)
	else:
	    i = file_or_image

	# fixed size
	i = i.resize((64, 64))

	# create mask
	m = None
	if i.mode == "P":
	    try:
		t = i.info["transparency"]
		m = i.point(lambda i, t=t: i == t, "1")
	    except KeyError:
		pass
	elif i.mode == "RGBA":
	    # get transparency layer
	    m = i.split()[3].point(lambda i: i == 0, "1")

	if not m:
	    # opaque
	    m = Image.new("1", i.size, 0)

	# clear unused parts of the original image
	i = i.convert("RGB")
	i.paste((0, 0, 0), (0, 0), m)

	# create icon
	m = m.tostring("raw", ("1", 0, 1))
	c = i.tostring("raw", ("BGRX", 0, -1))

	self.icon = _tkicon.new(i.size, c, m)

    def attach(self, window):

	self.icon.attach(window.winfo_id())


if __name__ == "__main__":

    import Tkinter

    root = Tkinter.Tk()
    root.title("Hello, world")

    # you must call update to make sure that the window is
    # actually created before you can attach an icon to it.
    # to prevent flicker, we withdraw the window before doing
    # this.  another way to do this is to install the icon on
    # the <Visibility> event.  see imageView.py for an example.

    root.withdraw()
    root.update()

    file = "tkIcon.gif"

    icon = Icon(file)
    icon.attach(root)

    root.deiconify()

    root.mainloop()
