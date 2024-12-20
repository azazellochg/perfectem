The ``perfectem`` package provides a set of scripts designed to test TEM performance. Some tests have been adapted from TFS SAT procedures.
The scripts are using SerialEM's Python module. Installation on both Windows and Linux OS is supported.

.. image:: https://img.shields.io/pypi/v/perfectem.svg
        :target: https://pypi.python.org/pypi/perfectem
        :alt: PyPI release

.. image:: https://img.shields.io/pypi/l/perfectem.svg
        :target: https://pypi.python.org/pypi/perfectem
        :alt: License

.. image:: https://img.shields.io/pypi/pyversions/perfectem.svg
        :target: https://pypi.python.org/pypi/perfectem
        :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/dm/perfectem
        :target: https://pypi.python.org/pypi/perfectem
        :alt: Downloads

Installation
------------

Requirements:

    * python >= 3.8
    * matplotlib, mrcfile, numpy, scipy
    * SerialEM Python module will be compiled during installation unless already present

Installation from PyPI
######################

This assumes you have connection to the internet.

Execute from the command line (assuming you have your Python interpreter in the path):

**Windows:**

.. code-block:: python

    py -m pip install perfectem

**Linux:**

.. code-block:: python

    pip install perfectem

Offline installation
####################

#. Download \*.whl files for `matplotlib <https://pypi.org/project/matplotlib/#files>`_, `mrcfile <https://pypi.org/project/mrcfile/#files>`_, `numpy <https://pypi.org/project/numpy/#files>`_ and `scipy <https://pypi.org/project/scipy/#files>`_ into the current folder
#. Download https://github.com/azazellochg/perfectem sources
#. Execute from the command line (assuming you have your Python interpreter in the path):

**Windows:**

.. code-block:: python

    py -m pip install matplotlib mrcfile numpy scipy perfectem --no-index --find-links .
    py -m pip install -e <perfectem_source_directory>

**Linux:**

.. code-block:: python

    pip install matplotlib mrcfile numpy scipy perfectem --no-index --find-links .
    pip install -e <perfectem_source_directory>

Available scripts
-----------------

- AFIS validation
    - Specification (Krios): coma < 750 nm, astigmatism < 10 nm for 5 um shift. Glacios: coma < 1200 nm, astigmatism < 15 nm for 6 um shift
    - Description: Measure residual beam tilt and astigmatism at different image shift positions while EPU is open.
- Atlas realignment
    - Specification: none
    - Description: Compare the shift and rotation between two atlases acquired when reloading the same grid.
- Magnification anisotropy
    - Specification: <1%
    - Description: Acquire a defocus series and plot astigmatism versus defocus. Calculate anisotropy by estimating deviation from linear behaviour.
- C2 Fresnel fringes
    - Specification: on FFI system there should be <5 fringes at 96 kx in nanoprobe close to focus
    - Description: Take a picture of a flood beam to see if the fringes from C2 aperture extend all the way to the center (non-FFI systems).
- Eucentricity check
    - Specification: <2 um in X/Y, <4 um defocus (Krios G2, G3, G3i)
    - Description: Estimate X,Y and defocus offset while tilting the stage.
- Gain reference check
    - Specification: none
    - Description: Take a picture of a flood beam and check the auto-correlation image.
- Gold diffraction
    - Specification: none
    - Description: Take a high magnification image of Au-Pt and check the diffraction spots up to 1 A in all directions.
- Information limit
    - Specification (Krios < G4): 0.14 nm at 0 tilt, 0.23 nm at 70 deg. tilt. Glacios: 0.23 nm at 0 tilt, 0.34 nm at 70 deg. tilt.
    - Description: Take two images with a small image shift (0.12 nm), add them together and calculate FFT. You should observe Young fringes.
- Point resolution
    - Specification (Krios): 0.2 nm at 73 nm defocus. Glacios: 0.24 nm at 82 nm defocus.
    - Description: Take a high-resolution image on carbon (Pt-Ir grid recommended) at extended 1.2 Scherzer defocus. The first CTF ring defines the point resolution.
- Stage drift
    - Specification: 0.5 nm/min (but TFS does the test in a very different way)
    - Description: From a starting position move 1 um in each direction and measure drift until it is below threshold (1 A/s).
- Thon rings
    - Specification (Krios): rings visible beyond 0.33 nm at -1 um defocus. Glacios: rings visible beyond 0.37 nm at -2 um defocus.
    - Description: Take a high-resolution image on carbon and fit CTF rings as far as you can. Calculate a radial average from one quadrant.
- Tilt axis offset
    - Specification: <1 um
    - Description: Estimate the tilt axis offset optimized for movement along the z-axis during tilting

Running scripts
---------------

The scripts have been tested only on TFS Titan Krios and Glacios microscopes. All tests except maybe Point resolution (which needs a Pt-Ir grid) require a cross-grating grid (e.g. **AGS106L** Diffraction grating replica with latex spheres) inserted and the eucentric height adjusted. Also, it is assumed that the microscope is already well aligned.

First, have a look at **config.py**: edit *microscopes* dictionary and individual parameters for each test. Make sure SerialEM is open. To start the program, simply type in the Windows CMD / Linux console:

.. code-block:: python

    perfectem

If you prefer clicking buttons over console, you can create a desktop script **PerfectEM.bat** that contains one line:

.. code-block::

    perfectem-gui

PS. The simple GUI requires Python built with tkinter support.
