Command Line Usage
==================
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
============
Using BigPlanet as a module is where majority of the *magic* happens. To start,
import BigPlanet as a module:

.. code-block:: python

    import bigplanet as bp

This allows you to use the various functions that are outlined in detail below, such as
print all the names of the variables (the "keys") in the bpl file (PrintGroups and PrintDatasets), extract a particular
variable from its key (ExtractColumn), extract the units of a particular key value
(ExtractUnits), extract unique values in a particular key (ExtractUniqueValues),
create a matrix based on two keys (CreateMatrix), and write out a list of keys
to a file (WriteOutput).


.. note::

    Keys using the following format for naming: body_variable_aggregation


**PrintGroups and PrintDatasets**
---------------------------------

PrintGroups, as the name suggests, simply that prints all of the group names in the BPL file (ie test_rand_123)
Groups are the names of various simulation folders (called trials) that can be extracted.

PrintDatasets is identical except it prints the dataset names (ie 'earth_Obliquity_final')
datasets are where the actual data is stored in the BPL file.

PrintGroups takes in the following arguments:

.. code-block:: python

    PrintGroups(bpl_File)

PrintDatasets takes in the following arguments:

.. code-block:: python

    PrintDatasets(bpl_File)

where *bpl_File* is the name of the bpl file, which is used like so:

.. code-block:: python

    bpl_File = h5py.File(filename, 'r')



**ExtractColumn**
-----------------

ExtractColumn is a function that returns all of values of a particular column in the
bpl file. It takes the following arguments:

.. code-block:: python

    ExtractColumn(bpl_File,Key)

where:

*bpl_File* is the name of the bpl file

*Key* is the name of the particular variable you are extracting the units from.

See the `Understanding Keys`_ Section for an indepth look at the types of key options available.



**ExtractUnits**
----------------
ExtractUnits is a function that returns the units of a particular column in the
bpl file. It takes the following arguments:

.. code-block:: python

    ExtractUnits(bpl_File,Key)

where:

*bpl_File* is the name of the bpl file

*Key* is the name of the particular variable you are extracting the units from.

See the `Understanding Keys`_ Section for an indepth look at the types of key options available.



**ExtractUniqueValues**
-----------------------
ExtractUniqueValues is a function that returns a list of unique values in a key provided.
It takes the following arguments:

.. code-block:: python

    ExtractUniqueValues(bpl_File,Key)

where:

*bpl_File* is the name of the bpl file

*Key* is the name of the particular variable you are extracting the units from.


**CreatebplFile**
------------------
CreatebplFile is a function that creates an bpl file from the input file that is passed
to the function. This is mainly used if you forgot to run bigplanet or want to run all
the code for bigplanet in module format

.. code-block:: python

    CreatebplFile(inputfile)

where:

*inputfile* is the same file used to run vspace and multi-planet


**CreateMatrix**
----------------
CreateMatrix is a function that returns the zaxis for a 3D matrix. This is useful
for plotting Contour Plots of the data extracted. CreateMatrix takes the following
arguments:

.. code-block:: python

    CreateMatrix(xaxis,yaxis,zarray,orientation=1)

where:

*xaxis* is the ExtractUniqueValues() of the column you want the xaxis to be

*yaxis* is the ExtractUniqueValues() of the column you want the xaxis to be

*zarray* is the ExtractColumn() of what you want the zaxis to be

*orientation* is the orientation of the data based on a 4 quadrant grid that
goes counter clockwise in 90 degree interments. The default is 1, or bottom left corner.



**WriteOutput**
---------------
WriteOutput is a function that writes the list of columns to an output file. Headers
are optional. WriteOutput takes the following arguments:

.. code-block:: python

    WriteOutput(inputfile, columns, file="bigplanet.out", delim=" ", header=False, ulysses=False)

where:

*inputfile* is the name of the bpl file

*columns* is the list of keys you are extracting (Use the same format as ExtractColumn, ExtractUnits and
ExtractUniqueValues)

*File* is the name of the output file

*delim* is the delimiter for the output file (the default is spaces)

*header* adds the names and units for each column (default is False)

*ulysses* makes the file compatable with VR Ulysses (default is False)



Understanding Keys
==================
Keys are the bread and butter of BigPlanet. The keys, as briefly mentioned above,
are the names of the various variables that BigPlanet has extracted from the forward file,
the option files, and the log file that are generated when VPLanet finishes compiling.


.. note::

	  Keys using the following format for naming: body_variable_aggregation


Below is a table of all the various aggregations available at this time:

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Aggregation
     - Description
     - Usage
   * - Initial
     - returns a list of the *initial* values of the particular parameter for
       every simulation. This data is from the log file.
     - body_variable_initial
   * - Final
     - returns a list of the *final* values of the particular parameter for
       every simulation. This data is from the log file.
     - body_variable_final
   * - Output Order
     - returns a list of the names and units of the forward file values. This data is from the log file.
     - body_OutputOrder
   * - Forward
     - returns a nested list of the *forward* values of the particular
       parameter for every simulation. This data is from the forward file.
     - body_variable_forward
   * - Grid Output Order
     - if the Poise Module was used in the simulations,returns a list of the
       names and units of the climate file values. This data is from the log file.
     - body_GridOutputOrder
   * - Climate
     - if the Poise Module was used in the simulations, the climate options
       returns a nested list of the *climate* values of the particular
       parameter for every simulation. This data is from the climate files.
     - body_variable_climate
   * - Option
     - the option options returns a  list of the *option* values of the particular
       parameter for every simulation. This data is from the option files.
     - body_variable_option


.. warning::

    The following aggregations will **only** work with parameters that are
    from the *forward* file.
    If you attempt to use it with a value that is **NOT** in the forward file,
    it will produce an error.



 .. list-table::
    :widths: auto
    :header-rows: 1

    * - Aggregation
      - Description
      - Usage
    * - Min
      - returns a list of the minimum values from the *forward* values of the
        particular parameter for every simulation
      - body_variable_min
    * - Max
      - returns a list of the maximum values from the *forward* values of the
        particular parameter for every simulation
      - body_variable_max
    * - Mean
      - returns a list of the mean calculated from the *forward* values of the
        particular parameter for every simulation
      - body_variable_mean
    * - Geometric Mean
      - returns a list of the gemoetric mean calculated from the *forward*
        values of the particular parameter for every simulation
      - body_variable_geomean
    * - Standard Deviation
      - returns a list of the standard deviation calculated from the *forward*
        values of the particular parameter for every simulation
      - body_variable_stddev
