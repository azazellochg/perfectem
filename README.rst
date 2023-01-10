The ``perfectem`` package provides a set of scripts designed to test TEM performance.
The scripts are using SerialEM's Python module.

Installation
------------

.. warning:: The project is still in development phase, no beta version has been released yet. Installing from sources is recommended.

Requirements:

    * python >= 3.6
    * matplotlib, mrcfile, numpy, scipy
    * SerialEM python module
    * network connection to SerialEM PC

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

#. Download \*.whl files for perfectem, mrcfile, numpy, matplotlib and scipy into the current folder
#. Execute from the command line (assuming you have your Python interpreter in the path):

.. code-block:: python

    py -m pip install mrcfile numpy matplotlib scipy perfectem --no-index --find-links .

Option B (from sources)
^^^^^^^^^^^^^^^^^^^^^^^

#. Download \*.whl files and https://github.com/azazellochg/perfectem sources
#. Run the following commands:

.. code-block:: python

    py -m pip install mrcfile numpy scipy matplotlib --no-index --find-links .
    py -m pip install -e <source_directory>

Available scripts
-----------------

    * tbd
