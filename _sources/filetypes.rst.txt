
Bigplanet File Types
=====================

``bigplanet`` generates two different file types: a bigplanet archive and a bigplanet file. 
Below each file type is explained in depth. 


Archives
--------

The bigplanet archive ontains *everything* from
the parameter sweep. The archive can require hours to build, depending on the size of the data set and number of cores
employed to build it.
When an archive is built, ``bigplanet`` also performs an MD5 checksum and creates a file with the resultant hash,
i.e. GDwarf.md5, which is examined every time the archive is accessed to ensure the 
data are not corrupted. After building the BPA file, it is safe to remove the raw data. 
To generate an archive, run ``bigplanet`` with the :code:`-a` option.


Files
-----

The bigplanet file is a subset of the archive that is useful for rapid and in-depth analyses of a specific
aspect of the full parameter sweep.
Bigplanet files enable much faster data access than from the raw data or the archive itself.
There are two ways of creating a bigplanet file: 1) extracting the data from the archive, or 2) extracting from
the raw simulation data. Extracting from the archive is always the *fastest* way 
to create a bigplanet file.