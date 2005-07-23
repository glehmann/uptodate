#!/usr/bin/python
from distutils.command.install_scripts import install_scripts
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib
import distutils.file_util
import distutils.dir_util
import sys, os
import glob
import re

if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

verpat = re.compile("VERSION *= *\"(.*)\"")
data = open("uptodate.py").read()
m = verpat.search(data)
if not m:
    sys.exit("error: can't find VERSION")
VERSION = m.group(1)

# Make distutils copy uptodate.py to uptodate.
copy_file_orig = distutils.file_util.copy_file
copy_tree_orig = distutils.dir_util.copy_tree

def copy_file(src, dst, *args, **kwargs):
    if dst.endswith("bin/uptodate.py"):
        dst = dst[:-3]
    return copy_file_orig(src, dst, *args, **kwargs)

def copy_tree(*args, **kwargs):
    outputs = copy_tree_orig(*args, **kwargs)
    for i in range(len(outputs)):
        if outputs[i].endswith("bin/uptodate.py"):
            outputs[i] = outputs[i][:-3]
    return outputs

distutils.file_util.copy_file = copy_file
distutils.dir_util.copy_tree = copy_tree

I18NFILES = []
for filepath in glob.glob("locale/*/LC_MESSAGES/*.mo"):
    targetpath = os.path.dirname(os.path.join(sys.prefix, "share", filepath))
    I18NFILES.append((targetpath, [filepath]))

setup(name =             "uptodate",
      version =          VERSION,
      description =      "uptodate helps you to know when a new version of what you want is out",
      author =           "Gaetan Lehmann",
      author_email =     "gaetan.lehmann@jouy.inra.fr",
      license =          "GPL",
      url =              "http://voxel.jouy.inra.fr/darcs/uptodate",
      packages =         ["uptodate", "uptodate.plugins"],
      scripts =          ["uptodate.py"],
      data_files =       I18NFILES,
      )
