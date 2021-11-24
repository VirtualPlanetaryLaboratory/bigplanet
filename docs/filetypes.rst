
Bigplanet File Types
=====================

``bigplanet`` generates two different file types: a bigplanet archive and a bigplanet file. 
Below each file type is explained in depth. 


Archives
--------

The bigplanet archive ontains *everything* from
the parameter sweep. The archive can require hours to build, depending on the size of the data set.
When an archive is built, ``bigplanet`` also performs an MD5 checksum and creates a file with the resultant hash,
i.e. GDwarf.md5, which is examined every time the archive is accessed to ensure the 
data are not corrupted. After building the BPA file, its safe to remove the raw data. 
To generate an archive file, run ``bigplanet`` with the :code:`-a` option.


Files
-----

The bigplanet file is a subset of the archive file that is useful for in-depth analyses of a specific
aspect of the full parameter sweep.
Bigplanet files enable a much faster data accessing than from the raw data or the archive file.
There are two ways of creating a filtered file: 1) extracting the data from the archive file or 2) extracting from
the raw simulation data. Extracting the archive file is always the *fastest* way 
to create a bigplanet file.