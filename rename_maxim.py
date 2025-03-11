####!/usr/bin/python
## previously !/Applications/scisoft/i386/bin/python
# Fix filenames from MaximDL
# JH 2016
import os, re, sys


def rename_maxim(head):
    # Change .fts extensions from ACP to .fits for IRAF
    ext = ".fits"
    # Fix spaces
    head = head.replace(" ", "_")
    # Fix CCD Image numbering from Maxim so that directory listings sort in order
    # by adding leading zeros
    if head[:3] == "CCD":
        nimage = head[10:]
        newno = "%04d" % int(nimage)
        head = head[:10] + newno
    fname_new = head + ext
    return fname_new


def main(dir):
    # dir='/Volumes/Astrophysics/Observations 2015-16/2016-02-10/DarkChiPer/'
    dirlist = os.listdir(dir)
    dir = dir + "/"

    for fname in dirlist:
        (head, ext) = os.path.splitext(fname)
        if re.search("f.*t.*", ext):

            fname_new = rename_maxim(head)
            print(dir + fname, " -> ", dir + fname_new)
            os.rename(dir + fname, dir + fname_new)


if __name__ == "__main__":
    print("sys.argv = ", sys.argv)
    if len(sys.argv) > 0:
        # run on directory given in command line
        main(sys.argv[1])
    else:
        # or default to running on current directory
        main(os.listdir("."))
