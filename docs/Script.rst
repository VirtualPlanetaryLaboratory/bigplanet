Scripting with BigPlanet
========================
Using BigPlanet as a module is where majority of the *magic* happens. To start,
import BigPlanet as a module:

.. code-block:: python

    import BigPlanet as bp

This allows you to use the various functions that are outlined in detail below, such as
print all the names of the variables (the "keys") in the bpl file (PrintGroups and PrintDatasets), extract a particular
variable from its key (ExtractColumn), extract the units of a particular key value
(ExtractUnits), extract unique values in a particular key (ExtractUniqueValues),
create a matrix based on two keys (CreateMatrix), and write out a list of keys
to a file (WriteOutput).


.. note::

    Keys using the following format for naming: body:variable:aggregation



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
to the function. This is mainly used if you forgot to run BigPlanet or want to run all
the code for BigPlanet in module format

.. code-block:: python

    CreatebplFile(inputfile)

where:

*inputfile* is the same file used to run ``VSPACE`` and ``multi-planet``


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



**BPtoCSV**
---------------
BPtoCSV is a function that writes the list of columns to an output file. Headers
are optional. WriteOutput takes the following arguments:

.. code-block:: python

    BPtoCSV(inputfile, columns, file="BigPlanet.out", delim=" ", header=False, ulysses=False)

where:

*inputfile* is the name of the bpl file

*columns* is the list of keys you are extracting (Use the same format as ExtractColumn, ExtractUnits and
ExtractUniqueValues)

*File* is the name of the output file

*delim* is the delimiter for the output file (the default is spaces)

*header* adds the names and units for each column (default is False)

*ulysses* makes the file compatable with `VR Ulysses <https://www.vrulysses.com/download-ulysses>`_ (default is False)