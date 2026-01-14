.. _level-one-data-products:

Level 1 Data
==============

Level 1 data are provided by the DKIST Data Center for all scientific observations carried out by the telescope.
The Level 1 data are calibrated to remove any effects introduced by the telescope or instruments.
The result of these calibration recipes is a Level 1 "dataset", which is the smallest unit of data searchable from the data center.

A Level 1 "Dataset"
---------------------

A dataset contains observations from a single camera, a single instrument, in a single pass band for a continuous period of observation.
Each dataset is spread across many FITS files in the form described by :ref:`spec-214`.
In addition to the FITS files, a Level 1 dataset also contains the following files:

* A single metadata ASDF file, which has a record of all the metadata for the dataset and can be loaded using the `dkist` Python package.
* A quality report PDF, which is a high-level summary of the observing conditions and parameters of the data which might affect scientific utility. The data that generated this report are also contained in the ASDF file.
* A quick view movie, which is an animation of the dataset that can be used as a preview.

The Metadata File
-----------------

The metadata ASDF file is provided alongside the dataset to facilitate inspection and analysis of the metadata of a dataset, without having to transfer all the data.
This, in concert with the preview movie, is designed to help make decisions on if a given dataset is of interest, or what parts of it are, without needing to transfer it.

The metadata file provides the following information about the dataset:

* A table of all the FITS headers for all the FITS files contained in the dataset.
* An ordered nested list of the filenames of all the FITS files, providing the information about how to reconstruct the full dataset array from all the component FITS arrays.
* Information about the dtype, shape, and HDU number of the arrays in the FITS file.
* A `gWCS <https://gwcs.readthedocs.io/>`__ object providing the coordinate information for the reconstructed dataset array.

The FITS Files
--------------

As already mentioned, the data in a single dataset is distributed across many FITS files.
This is due to the potential size of each of these datasets and eliminates on-demand processing at the data center.
Each individual FITS file represents what can be considered to be a "single calibrated exposure".
When all the processing steps have been taken into account, there can be many actual exposures of the instrument involved,
but the exposures have been reduced to a single array.
The exact contents of each FITS file vary depending on the type of instrument and the mode it was operating in, but some examples are:

* A single wideband image without polarimetric information with a single timestamp (VBI).
* A single slit position, at one Stokes profile, with a single timestamp (ViSP / CryoNIRSP).
* A single narrow band image, at one Stokes profile, with a single timestamp (VTF).

Each Level 1 FITS file will have only one HDU that contains data, expected to be the second HDU
in the file.  The data will be RICE compressed as described by the FITS 4 standard.
For more information about the metadata provided in each FITS file see :ref:`spec-214`.

The Dataset Extra Files
-----------------------

The dataset extras are the intermediate products created during the processing and calibration of a dataset, and are
intended for advanced users who need additional information about how a dataset was created.  The table below shows
which extras are included with each instrument:

==========================================  ===  ====  =========  ========
Extra                                       VBI  ViSP  CryoNIRSP  DL-NIRSP
==========================================  ===  ====  =========  ========
Bad Pixel Map                                          X          X
Dark                                             X     X          X
Background Light                                 X
Solar Gain                                       X     X          X
Characteristic Spectra                           X     X          X
Modulation State Offsets                         X
Beam Angles                                      X     X
Beam Offsets                                           X
Spectral Curvature Shifts                        X     X          X
Spectral Curvature Scales                                         X
Wavelength Calibration Input Spectrum            X     X (SP)     X
Wavelength Calibration Reference Spectrum        X     X (SP)     X
Reference Wavelength Vector                      X     X          X
Demodulation Matrices                            X     X          X
PolCal as Science (PCAS)                         X     X          X
==========================================  ===  ====  =========  ========

See the individual instrument pipeline documentation for more information about specific dataset extras.
For information about metadata provided in the dataset extra FITS files, see :ref:`dataset_extra`.
