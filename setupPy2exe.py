from distutils.core import setup 
import sys, os, py2exe

if len(sys.argv) == 1:
	sys.argv.append('py2exe')

setup(
    console = ["bc2redirect.py"],
    zipfile = None, 
    options = {
        "py2exe": {
            "bundle_files": 1,
            "optimize": 1,
        }
    },
) 