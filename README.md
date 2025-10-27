# Astro-Lab Scripts
## Initially by J. Hatchell
## Updated for 2025 by T. Joshi-Hartley

Four scripts that work together to organise, re-name and allow WCS correction of
one night of observations taken with the University of Exeter teaching telescope.

Data comes from the telescope in the form:
    `DATE/DATE/CCD_Image_xxxx.fits`
where `DATE` is the date of observations, i.e. `2025-02-26` and `_xxxx` is the index of image taken that night.

This data should be **moved** onto the back-up hard drive (i.e. removed from the Observatory computer) and then **copied** onto a local machine for processing. Once processed, the obsercations can be added to the Sharepoint.

## Processing the Data

On your local machine (i.e. on a copy of the data), you should run 
```bash
python log.py <BASEDIR>
```
where `<BASEDIR>` is the top directory for the data, i.e. `DATE/` not `DATE/DATE`.

This will organise the observations into directories based on target; rename the files to contain information about the target, filter and exposure time; and create `DATE/date.log` which will contain information about the structure of the subdirectories.

Upon completion, `log.py` will print to terminal what targets it has found that we can attempt to obtain a WCS header for. To select a target, run

```bash
python make_wcs.py DATE/DATE TARGET
```

and the `make_wcs.py` script will attempt to obtain a wcs header for all images in that target's subdirectory. Images of solar system planets and/or flatfields should not be submitted to the `make_wcs.py` code. This can take some time as the code needs to acquire a link to Astrometry.net.

Once all cluster images have been run through the make_wcs.py code, the night's observations are ready to be uploaded to Sharepoint.

## Required Packages

Running these scripts requires docopt, astropy, astroquery and photutils and their dependencies to be installed.
    
You can do
```bash
conda create -n MakeWCS -c conda-forge docopt astropy astroquery photutils
```
to create a conda environment called `MakeWCS` with the relevant packages.

Versions that definitely work are:
    - docopt=0.6.2
    - astropy=7.1.1
    - astroquery=0.4.11
    - photutils=2.3.0