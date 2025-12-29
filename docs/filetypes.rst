
BigPlanet File Types
=====================

``BigPlanet`` generates two different file types: a BigPlanet archive and a BigPlanet file. 
Below each file type is explained in depth. 


Archives
--------

The BigPlanet archive contains *everything* from
the parameter sweep. The archive can require hours to build, depending on the size of the data set and number of cores
employed to build it.
When an archive is built, ``BigPlanet`` enables Fletcher32 checksums on numeric datasets within the HDF5 file,
providing automatic data integrity verification. HDF5 validates these checksums whenever data is read,
ensuring the data are not corrupted. (Note: Fletcher32 checksums are applied only to numeric array data;
scalar values and string data do not receive checksum protection due to HDF5 limitations.)
After building the BPA file, it is safe to remove the raw data.
To generate an archive, run ``BigPlanet`` with the :code:`-a` option.


Files
-----

The BigPlanet file is a subset of the archive that is useful for rapid and in-depth analyses of a specific
aspect of the full parameter sweep.
BigPlanet files enable much faster data access than from the raw data or the archive itself.
There are two ways of creating a BigPlanet file: 1) extracting the data from the archive, or 2) extracting from
the raw simulation data. Extracting from the archive is always the *fastest* way 
to create a BigPlanet file.