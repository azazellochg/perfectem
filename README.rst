The ``perfectem`` package provides a set of scripts designed to test TEM performance.
The scripts are using SerialEM's Python module.

Installation
------------

.. warning:: The project is still in development phase, no beta version has been released yet. Installing from sources is recommended.

Requirements:

    * python >= 3.6
    * matplotlib, mrcfile, numpy, scipy
    * network connection to PC with SerialEM that controls the microscope

Installation from PyPI on Windows
#################################

This assumes you have connection to the internet.

Execute from the command line (assuming you have your Python interpreter in the path):

.. code-block:: python

    py -m pip install perfectem

Offline installation on Windows
###############################

Option A (from PyPi)
^^^^^^^^^^^^^^^^^^^^

#. Download \*.whl files for `perfectem <https://pypi.org/project/perfectem/#files>`_, `matplotlib <https://pypi.org/project/matplotlib/#files>`_, `mrcfile <https://pypi.org/project/mrcfile/#files>`_, `numpy <https://pypi.org/project/numpy/#files>`_ and `scipy <https://pypi.org/project/scipy/#files>`_ into the current folder
#. Execute from the command line (assuming you have your Python interpreter in the path):

.. code-block:: python

    py -m pip install matplotlib mrcfile numpy scipy perfectem --no-index --find-links .

Option B (from sources)
^^^^^^^^^^^^^^^^^^^^^^^

#. Download \*.whl files and https://github.com/azazellochg/perfectem sources
#. Run the following commands:

.. code-block:: python

    py -m pip install matplotlib mrcfile numpy scipy --no-index --find-links .
    py -m pip install -e <source_directory>

Available scripts
-----------------

* Stage drift
* Magnification anisotropy
* Information limit (Young fringes)
* Thon rings
* Gold diffraction
* C2 Fresnel fringes
* Tilt axis offset
* Gain reference check
* AFIS check
* Point resolution

Running scripts
---------------

First, have a look at `config.py`: edit *SCOPE_NAME*, *params_dict* value and individual parameters for each test. Make sure SerialEM is open. To start the program, simply type:

.. code-block:: python

    perfectem
