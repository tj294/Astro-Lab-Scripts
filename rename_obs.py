#!/usr/bin/python
"""
A python code that takes a directory, and for all fits files
in that directory reads in the header file and constructs a
file name. It then renames that fits file to the new file name

Usage:
    rename_obs (<dir>) [--force]

Options:
    --force -f          # Do not prompt rename
"""

from docopt import docopt
from glob import glob
from astropy.io import fits
from pathlib import Path
import os

import make_wcs


def create_fpath(fname, force=True):
    fname = Path(fname)
    obj_name = fname.parts[-2]
    with fits.open(fname) as f:
        header_info = f[0].header
    filter_name = header_info["FILTER"]
    exp_time = header_info["EXPTIME"]
    if exp_time % 1.0 == 0:
        exp_time = int(exp_time)
    else:
        exp_time = f"{exp_time:.3f}"
    new_fname = f"{obj_name}_{filter_name}_{exp_time}s_00.fits"
    old_fname = fname.name
    if not force:
        print(f"\t{old_fname} -> {new_fname}")
    new_fpath = Path.joinpath(fname.parent, new_fname)
    return new_fpath


def sort_by_target(fits_dir):
    fits_list = glob(fits_dir + "/*.fits")
    if len(fits_list) == 0:
        print(f"No .fits files found in {fits_dir}")
        return -1
    for file in fits_list:
        with fits.open(file) as f:
            header_info = f[0].header
        try:
            image_type = header_info["IMAGETYP"]
            target_ID = header_info["OBJECT"]
            if image_type == "Light Frame":
                folder_name = target_ID
            else:
                folder_name = image_type.replace(" ", "_")
        except KeyError:
            print(f"{file} does not have requisite header info")
            folder_name = "Misc"

        fpath = Path(file)
        new_fpath = fpath.parent.joinpath(folder_name, fpath.name)
        # print(f"Renaming {file} to {new_fpath}")
        new_fpath.parent.mkdir(exist_ok=True)
        os.rename(fpath, new_fpath)
    failed_paths = []
    if Path(fits_dir).joinpath("Misc.").exists():
        for file in Path(fits_dir).joinpath("Misc.").iterdir():
            failed_paths.append(file)
    else:
        failed_paths = 0
    return failed_paths


def list_wcs_targets(fits_dir):
    print("Listing WCS Targets")
    fits_dir = Path(fits_dir)
    for target in fits_dir.glob("*/"):
        print("\t", target.name)
    print("\n")
    print("To obtain WCS solutions for a target, run:")
    print(f"python make_wcs.py {fits_dir} TARGET")
    return 0


def process_folder(fits_dir, force=True):
    fits_list = glob(fits_dir + "/*.fits")
    if len(fits_list) == 0:
        print(f"No .fits files found in {fits_dir}")
        return -1

    if not force:
        print(Path(fits_list[0]).parent)
    target = str(Path(fits_list[0]).parts[-2])

    # Create new path name
    new_fpaths = []
    # Attempt to obtain WCS Solution for files in directory
    # Rename files in directory based on header
    for file in fits_list:
        new_fpath = create_fpath(file, force)
        new_fpaths.append(new_fpath)
    old_to_new = zip(fits_list, new_fpaths)
    if force:
        go_ahead = "Y"
    else:
        go_ahead = input("Look okay? (Y/N) ")

    if go_ahead.capitalize() == "Y":
        for old_path, new_path in old_to_new:
            complete = False
            count = 0
            while complete == False:
                if new_path.exists():
                    count += 1
                    new_path = new_path.with_name(
                        new_path.name.replace(f"_{count-1:02d}.", f"_{count:02d}.")
                    )
                else:
                    os.rename(old_path, new_path)
                    complete = True
    else:
        print("Cancelled by user. No changes made.")


if __name__ == "__main__":
    args = docopt(__doc__)
    fits_dir = args["<dir>"]
    force = args["--force"]
    list_wcs_targets(fits_dir)
    # sort_by_target(fits_dir)
    # process_folder(fits_dir, force)
