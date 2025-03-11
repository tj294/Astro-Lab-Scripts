##!/Users/hatchell/Applications/miniconda3/envs/astroconda/bin/python
## previously !/Applications/scisoft/i386/bin/python
# Create log from fits header
# JH Feb 2016
# Oct 2017: tyke version under astroconda using astropy.io.fits
# Feb 2018: updated to unzip files first
# Feb 2024: TO DO update using pathlib

import os, re, sys, glob, zipfile
import rename_maxim
import rename_obs
from pathlib import Path
from astropy.io import fits


def main(basedir):
    # dir='/Volumes/Astrophysics/Observations 2015-16/2016-02-10/DarkChiPer/'
    # basefitsfiles = glob.glob('*.f*t*')
    # level1fitsfiles = glob.glob('*/*.f*t*')
    # To do: switch to os.walk to go through subdirectories

    # basedir = basedir+'/'

    # First iteration to unzip if needed
    for fname in os.listdir(basedir):
        if fname.endswith(".zip"):
            print("Unzipping %s" % fname)
            zf = zipfile.ZipFile(basedir + "/" + fname, mode="r")
            zf.extractall(path=basedir)
            zf.close

    # 2nd iteration to fix filenames
    for root, dirs, fnames in os.walk(basedir, topdown=True):
        subdir = root[len(basedir) :]
        depth = subdir.count(os.path.sep)
        print("root = %s, depth = %s" % (root, depth))
        if depth >= 2:
            continue
        root = root + os.path.sep
        # Find Fits files
        # print 'ext =',ext
        for fname in fnames:
            (head, ext) = os.path.splitext(fname)
            print("ext = %s" % ext)

            match = re.match(r"\.f.*t.*", ext)
            if match:

                # Fix filenames with spaces and fix numbering so files sort
                fname_new = rename_maxim.rename_maxim(head)
                if fname_new != fname:
                    print("Renaming to", root + fname_new)
                    os.rename(root + fname, root + fname_new)

        # TJH Added: Sort fits files into folder depending on their target
        # Rename .fits files depending on header information
        bad_paths = rename_obs.sort_by_target(root)

    # 3rd iteration to rename .fits filenames
    for root, dirs, fnames in os.walk(basedir, topdown=True):
        rename_obs.process_folder(root)

    # 4th iteration with sorted filenames to make log

    misc_flag = False

    log_path = basedir
    logname = os.path.basename(basedir) + ".log"
    logfullname = log_path + f"/{logname}"
    print(f"Creating log at {logfullname}")
    log = open(logfullname, "w")
    log.write("Log of FITS files in %s\n" % basedir)
    log.write(
        "%-20s %-30s %-22s %-8s %-10s %-13s %-7s %-10s\n"
        % (
            "Subdirectory",
            "File",
            "DATE-OBS",
            "OBJECT",
            "RA",
            "DEC",
            "EXPTIME/s",
            "FILTER",
        )
    )
    log.write(
        "-------------------------------------------------------------------------------------------------\n"
    )
    for root, dirs, fnames in os.walk(basedir, topdown=True):
        subdir = root[len(basedir) :]
        depth = subdir.count(os.path.sep)
        print("root = %s, depth = %s" % (root, depth))
        if depth >= 3:
            continue
        if "Misc" in root:
            misc_flag = True
            continue

        root = root + os.path.sep
        # Find Fits files
        # print
        #  'ext =',ext
        for fname in sorted(fnames):
            print("Working on fname", fname)
            (head, ext) = os.path.splitext(fname)
            match = re.match(r"\.f.*t.*", ext)
            if match:
                hdulist = fits.open(root + fname)
                # Log images from new SBIG CCD, not Orion autoguider
                if hdulist[0].header["INSTRUME"][:4] == "SBIG":
                    if hdulist[0].header["IMAGETYP"] == "Dark Frame":
                        log.write(
                            "%-20s %-30s %-22s DARK     N/A         N/A          %-7.1f     N/A\n"
                            % (
                                subdir,
                                fname,
                                hdulist[0].header["DATE-OBS"],
                                hdulist[0].header["EXPTIME"],
                            )
                        )
                    elif hdulist[0].header["IMAGETYP"] == "Bias Frame":
                        log.write(
                            "%-20s %-30s %-22s BIAS     N/A         N/A          %-7.1f     N/A\n"
                            % (
                                subdir,
                                fname,
                                hdulist[0].header["DATE-OBS"],
                                hdulist[0].header["EXPTIME"],
                            )
                        )
                    elif hdulist[0].header["IMAGETYP"] == "Flat Field":
                        log.write(
                            "%-20s %-30s %-22s FLAT     N/A         N/A          %-7.1f %10s\n"
                            % (
                                subdir,
                                fname,
                                hdulist[0].header["DATE-OBS"],
                                hdulist[0].header["EXPTIME"],
                                hdulist[0].header["FILTER"],
                            )
                        )
                    elif hdulist[0].header["IMAGETYP"] == "FLAT":
                        log.write(
                            "%-20s %-30s %-22s FLAT     N/A         N/A          %-7.1f %10s\n"
                            % (
                                subdir,
                                fname,
                                hdulist[0].header["DATE-OBS"],
                                hdulist[0].header["EXPTIME"],
                                hdulist[0].header["FILTER"],
                            )
                        )
                    elif hdulist[0].header["IMAGETYP"] == "Light Frame":
                        # hdulist.info()
                        log.write(
                            "%-20s %-30s %-22s %-8s"
                            % (
                                subdir,
                                fname,
                                hdulist[0].header["DATE-OBS"],
                                hdulist[0].header["OBJECT"],
                            )
                        )
                        try:
                            log.write(
                                "%-10s %-13s"
                                % (
                                    hdulist[0].header["OBJCTRA"],
                                    hdulist[0].header["OBJCTDEC"],
                                )
                            )
                        except KeyError:
                            log.write("  N/A         N/A          ")
                        log.write(
                            "%-7.1f %10s"
                            % (
                                hdulist[0].header["EXPTIME"],
                                hdulist[0].header["FILTER"],
                            )
                        )
                        log.write("\n")
                    else:
                        print(
                            "IMAGETYP %s not known for %s"
                            % (hdulist[0].header["IMAGETYP"], fname)
                        )
    if misc_flag:
        subdir = "/Misc"
        for fname in Path(basedir).joinpath("Misc").iterdir():
            hdulist = fits.open(fname)
            log.write(
                "%-20s %-30s %-22s UNKNOWN     N/A         N/A          %-7.1f     %10s\n"
                % (
                    subdir,
                    fname.name,
                    hdulist[0].header["DATE-OBS"],
                    hdulist[0].header["EXPTIME"],
                    hdulist[0].header["FILTER"],
                )
            )
    log.close()
    print("Written log to %s" % logfullname)

    rename_obs.list_wcs_targets(log_path)


if __name__ == "__main__":
    # print "sys.argv = ", sys.argv
    if len(sys.argv) > 0:
        # run on directory given in command line
        main(sys.argv[1])
    else:
        # or default to running on current directory
        main(os.listdir("."))
