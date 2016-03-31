#!/usr/bin/env python
#
# Setup script
# $Id: //modules/console/setup.py#3 $
#
# Usage: python setup.py install
#

from distutils.core import setup, Extension
from glob import glob

setup(
    name="tkicon",
    version="0.9-19980218",
    author="Fredrik Lundh",
    author_email="fredrik@pythonware.com",
    maintainer="PythonWare",
    maintainer_email="info@pythonware.com",
    description="tkIcon -- attach user-defined icon to Tkinter window",
    py_modules = ["tkIcon"],
    scripts = ["imageView.py"],
    ext_modules = [
        Extension("_tkicon", ["_tkicon.c"], libraries=["user32", "gdi32"])
        ]
    )
