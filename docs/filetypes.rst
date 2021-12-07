
BigPlanet File Types
=====================

``BigPlanet`` generates two different file types: a BigPlanet archive and a BigPlanet file. 
Below each file type is explained in depth. 


Archives
--------

The BigPlanet archive ontains *everything* from
the parameter sweep. The archive can require hours to build, depending on the size of the data set and number of cores
employed to build it.
When an archive is built, ``BigPlanet`` also performs an MD5 checksum and creates a file with the resultant hash,
i.e. GDwarf.md5, which is examined every time the archive is accessed to ensure the 
data are not corrupted. After building the BPA file, it is safe to remove the raw data. 
To generate an archive, run ``BigPlanet`` with the :code:`-a` option.


Files
-----

The BigPlanet file is a subset of the archive that is useful for rapid and in-depth analyses of a specific
aspect of the full parameter sweep.
BigPlanet files enable much faster data access than from the raw data or the archive itself.
There are two ways of creating a BigPlanet file: 1) extracting the data from the archive, or 2) extracting from
the raw simulation data. Extracting from the archive is always the *fastest* way 
to create a BigPlanet file.