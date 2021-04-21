Quickstart Guide
================
BigPlanet has two different uses: Creating HDF5 files that hold all the data from the various
simulations (command line usage), and extracting the data for plotting (Module usage).


Command Line Usage
-------------------
Using BigPlanet on the command line is relatively straight forward. After a suite of
simulations (set up with `vspace <../vspace>`_) has completed, simply run the following
command in the in the command line:

.. code-block:: bash

    bigplanet <input file> -c [number of cores] -q -m [email]

where the input file is the same file used to run vspace and multi-planet.
There are three optional arguments:
:code:`-c` : the number of processors used
:code:`-q` : quiet mode (nothing is printed to the command line)
:code:`-m` : emails the user when Bigplanet is complete

Module Usage
------------
Using BigPlanet as a module is where majority of the *magic* happens. To start,
import BigPlanet as a module:

.. code-block:: python

    import bigplanet as bp

This allows you to use the various functions that are outlined in detail below, such as
print all the names of the variables (the "keys") in the HDF5 file (PrintKeys), extract a particular
variable from its key (ExtractColumn), extract the units of a particular key value
(ExtractUnits), extract unique values in a particular key (ExtractUniqueValues),
create a matrix based on two keys (CreateMatrix), and write out a list of keys
to a file (WriteOutput).


.. note::

    Keys using the following format for naming: body_variable_aggregation
