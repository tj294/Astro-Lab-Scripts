"""
Usage:
    make_wcs (<dir> TARGET)
"""

import glob
from astroquery.exceptions import TimeoutError
from astroquery.astrometry_net import AstrometryNet
from astropy.io import fits
from astropy.coordinates import SkyCoord, Angle
import multiprocessing
import copy
import os
import sys
from photutils.utils import NoDetectionsWarning
import warnings
from docopt import docopt
from pathlib import Path


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def solve_wcs(source_image_name, target):
    """
    Function to use astrometry.net to solve for the World Coordinate System
    of a given image.

    Parameters
    ----------
    source_image_name : string
        The relative or absolute file path of the file containing the image
        to have its WCS solved.

    target : string
        The name of the object being WCS corrected

    """
    try_again = True
    submission_id = None
    n_submissions = 0
    wcs_header = None

    # Get the nominal RA / DEC.
    source_image = fits.open(source_image_name)
    ra = Angle(source_image[0].header["OBJCTRA"] + " hours")
    dec = Angle(source_image[0].header["OBJCTDEC"] + " degrees")

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="'datfix' made the change 'Set MJD-OBS to"
        )
        warnings.filterwarnings(
            "error",
            message="Sources were found, but none pass the sharpness, roundness",
        )
        warnings.filterwarnings("ignore", message="Removing photutils functionality")
        while try_again:
            if n_submissions == 0:
                print("Trying {}".format(source_image_name))
            else:
                print("    Trying {} again".format(source_image_name))
            if n_submissions > 9:
                try_again = False
            try:
                if not submission_id:
                    # astroquery's astrometry.net monitor_submission prints
                    # once every second while monitoring, so we suppress these
                    # print statements with the above class from
                    # https://stackoverflow.com/questions/8391411/how-to-block-calls-to-print.
                    with HiddenPrints():
                        wcs_header = ast.solve_from_image(
                            source_image_name,
                            center_ra=ra.degree,
                            center_dec=dec.degree,
                            radius=0.5,
                            fwhm=5,
                            detect_threshold=30,
                            publicly_visible="n",
                            allow_modifications="n",
                            allow_commercial_use="n",
                            scale_units="arcsecperpix",
                            scale_type="ev",
                            scale_est=1,
                            scale_err=25,
                            parity=1,
                            positional_error=2,
                            submission_id=submission_id,
                            solve_timeout=120,
                        )
                else:
                    with HiddenPrints():
                        wcs_header = ast.monitor_submission(
                            submission_id, solve_timeout=120
                        )
            except TimeoutError as e:
                print(f"\tsubmission {n_submissions} timed out. Resubmitting.")
                submission_id = e.args[1]
                n_submissions += 1
            except NoDetectionsWarning:
                print("                    No Detections in {}".format(source_image_name))
                try_again = False
                # NoDetectionsWarning doesn't seem to trigger, so catching all
                # exceptions below. This should be fixed at some point.
            except KeyboardInterrupt:
                # Needs to be in separately or the general except will stop you
                # being able to KeyboardInterrupt
                exit()
            except:
                print("                    Failed to fit {}".format(source_image_name))
                try_again = False
            else:
                # got a result, so terminate
                try_again = False

                if not wcs_header:
                    print("\tWCS solution not found.")
                else:
                    print(f"\tFinished {source_image_name}")

    if wcs_header:
        solved_image_name = source_image_name.replace(".fits", "_wcs.fits")
        source_image = fits.open(source_image_name)
        source_image_data = source_image[0].data
        source_image_head = source_image[0].header
        source_image.close()
        solved_image_head = copy.copy(source_image_head)
        solved_image_head.extend(wcs_header)
        hdu = fits.PrimaryHDU(data=source_image_data, header=solved_image_head)
        hdu.header["WCSSolve"] = True  # Add a new line of info in the HEADER.
        hdu.writeto(solved_image_name, overwrite=True)
        print(f"\t\tWrote to {solved_image_name}")


if __name__ == "__main__":
    # obs_date = sys.argv[1]
    # workingdir = '/Users/clairedavies/Documents/PHY2026_data/2024-10-25/2024-10-25/WCSXXCygni/'
    args = docopt(__doc__)
    print(args)
    basedir = args["<dir>"]
    target = args["TARGET"]
    workingdir = Path(basedir).joinpath(target)
    # target = "M37"
    # workingdir = (
    #     "/Users/clairedavies/Documents/PHY2026_data/2025-02-24/2025-02-24/"
    #     + target
    #     + "/"
    # )

    # if not os.path.exists(workingdir):
    #     os.makedirs(workingdir, exist_ok=True)

    # ccd_files = glob.glob(workingdir + "*.fits")
    ccd_files = workingdir.glob("*.fits")

    # # Set the second number to your desired parallelisation count.
    # # Having multiple connections open to astrometry.net may not work
    # # anymore -- setting n_pool = 1 seems to be fine, though.

    # # n_pool = min(multiprocessing.cpu_count(), 2)
    # # pool = multiprocessing.Pool(n_pool)
    # # for _ in pool.imap_unordered(solve_wcs, ccd_files, chunksize=len(ccd_files) // n_pool):
    # #     pass
    # # pool.close()
    ast = AstrometryNet()
    ast.api_key = "dftcsswtydizkjix"

    for file in ccd_files:
        solve_wcs(str(file), target)

ast = AstrometryNet()
ast.api_key = "dftcsswtydizkjix"
