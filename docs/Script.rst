Scripting
=========

Importing ``bigplanet`` as a module in a Python script enables the extraction and reformatting of the data
from bigplanet archives and files. In this page we describe how to use it for plotting and other analyses.
To access the functionality described herein, enter this line in your script:

.. code-block:: python

    import bigplanet as bp

The ``bigplanet`` module allows you to print all the names of the available `keys <Keys>`_ with
the ``PrintGroups`` and ``PrintDatasets`` functions, extract a specific key into and array or list
(``ExtractColumn``), extract the units of a key (``ExtractUnits``), extract only the unique values for 
a particular key (``ExtractUniqueValues``), create a matrix from two keys (``CreateMatrix``), and 
write out a list of keys to a file (``WriteOutput``).


.. note::

    Keys using the following format for naming: body:parameter:aggregation


**PrintGroups and PrintDatasets**
---------------------------------

To print the contents of an archive or file, ``bigplanet`` provides two utilities. 
As HDF5 files are organized by "groups", it can be convenient to see the names of the
groups in a bigplanet archive. ``bigplanet`` organizes each simulation into a group. To view them, use the PrintGroups function, which, 
as the name suggests, prints all of the groups in a bigplanet archive or file.
Groups are the names of various simulation folders (called trials) that can be extracted.

*XXX This seems out of date!XXX*

PrintDatasets is identical except it prints the dataset names (ie 'earth:Obliquity:final')
datasets are where the actual data is stored in the BPL file.

PrintGroups takes in the following arguments:

.. code-block:: python

    PrintGroups(bpl_File)

where *bpl_File* is the name (string) of the archive or file. PrintDatasets takes in the 
following arguments:

.. code-block:: python

    PrintDatasets(bpl_File)

where *bpl_File* is the name (string) of the archive or file, which is used like so:

.. code-block:: python

    bpl_File = h5py.File(filename, 'r')



**ExtractColumn**
-----------------

ExtractColumn is a function that returns an array of values for a particular key in an
archive or file. It takes the following arguments:

.. code-block:: python

    ExtractColumn(bpl_File,key)

where:

*bpl_File* (string) is the name of the bpl file

*key* (string) is the name of the `bigplanet key <Keys>` whose values are to be extracted.

**ExtractUnits**
----------------
ExtractUnits is a function that returns the astropy units associated with a particular key in a
file or archive. It takes the following arguments:

.. code-block:: python

    ExtractUnits(bpl_File,key)

where:

*bpl_File* (string) is the name of the bpl file

*key* (string) is the name of the `bigplanet key <Keys>` whose values are to be extracted.

**ExtractUniqueValues**
-----------------------
ExtractUniqueValues is a function that returns a list of unique values in a key provided. The 
returned array is useful for contour plots. It takes the following arguments:

.. code-block:: python

    ExtractUniqueValues(bpl_File,key)

where:

*bpl_File* (string) is the name of the bpl file

*key* (string) is the name of the `bigplanet key <Keys>` whose values are to be extracted.


**CreatebplFile**
------------------
CreatebplFile is a function that creates an archive or file from the filename that is passed
to the function, i.e. 'bpl.in'. This is mainly used if you forgot to run bigplanet or want to run all
the code for bigplanet in module format

.. code-block:: python

    CreatebplFile(filename)

where:

*filename* (string) is the name of a ``bigplanet`` input file.


**CreateMatrix**
----------------
CreateMatrix is a function that returns a 2 two-dimensional array of values. It is designed to 
work with ExtractColumn and ExtractUniqueValues to generate contour plots from bigplanet files.
CreateMatrix takes the following arguments:

.. code-block:: python

    CreateMatrix(xaxis,yaxis,zarray,orientation=1)

where:

*xaxis* (vector float) is the ExtractUniqueValues() of the x-axis key

*yaxis* (vector float)is the ExtractUniqueValues() of the column you want the xaxis to be

*zarray* (matrix float)is the ExtractColumn() of what you want the zaxis to be

*orientation* (???) is the orientation of the data based on a 4 quadrant grid that
goes counter clockwise in 90 degree increments. The default is 1, or origin in the 
bottom left corner. *XXX What does this mean?XXX*



**WriteOutput**
---------------
WriteOutput is a function that writes the list of columns to an output (ASCII) file. Headers
are optional. WriteOutput takes the following arguments:

.. code-block:: python

    WriteOutput(inputfile, columns, file="bigplanet.out", delim=" ", header=False, ulysses=False)

where:

*inputfile* (string) is the name of the bpl file

*columns* (???) is the list of keys you are extracting (Use the same format as ExtractColumn, ExtractUnits and
ExtractUniqueValues) *XXX I don't know what this meansXXX*

*file* (string) is the name of the output file

*delim* (string) is the delimiter for the output file (the default is a space)

*header* (bool) adds the names and units for each column (default is False)

*ulysses* (bool) writes the output file in `VR Ulysses <https://www.vrulysses.com/download-ulysses>`_  format (default is False)