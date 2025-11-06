Installation
============

Requirements for this package:

    * python >= 3.8
    * matplotlib, mrcfile, numpy, scipy
    * SerialEM Python module will be compiled during installation unless already present

Online installation on Windows
##############################

This assumes you have connection to the Internet. Execute from the command line
(assuming you have your Python interpreter in the path):

.. code-block:: python

    py -m pip install perfectem

Offline installation on Windows 7 or 10
#######################################

The command below will download perfectem and its dependencies on a computer connected to the Internet. We assume your microscope PC runs Windows 7 or Windows 10
64-bit OS. You need to know the Python version on the microscope PC (example below is for 3.8):

.. code-block:: python

    pip download -d . perfectem --python-version 38 --only-binary=:all: --platform win_amd64

Copy downloaded \*.whl files to the target PC and install them:

.. code-block:: python

    py -m pip install perfectem --no-index --find-links .

If you want to install perfectem from sources instead, download them from GitHub. You will still need the wheel files for dependencies:

.. code-block:: python

    py -m pip install matplotlib mrcfile numpy scipy --no-index --find-links .
    py -m pip install -e <source_directory>

Installation on Linux
#####################

The installation command is the same as above:

.. code-block:: python

    pip install perfectem
