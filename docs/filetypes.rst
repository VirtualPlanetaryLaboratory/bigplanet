
Bigplanet File Types
=====================


Overview
--------
Bigplanet has two different file types: the Archive File and Filtered file both with
their own advantages and usages. Below each file type is explained in depth. 


Archive File (BPA)
-------------------

The Bigplanet Archive file (uses the .bpa extension) will have everything from
the parameter sweep.The BPA file does take longer to make than the filtered file, 
but it also builds an MD5 checksum file, which enables users to verfiy your 
data are not corrupted. After building the BPA file, its safe to remove the raw data. 
Every time the BPA file is accessed, the MD5 checksum routine is ran to ensure data integrity.
To generate an archive file, run bigplanet with the :code:`-a` option.


Filtered File (BPF)
-------------------

The Bigplanet Filtered file (uses the .bpf extension) is a subset of the data for a specific analysis.
To fully utilize this, the user should set up a :code:`bpl.in` file which is explained more in detail on 
:ref:`The Bigplanet Input File`.
Using a BPF file enables a much faster data accessing than from the raw data or the archive file.
There are two ways of creating a filtered file: extracting the data from the archive file or extracting from
the raw simulation data. Extracting the archive file is the *fastest* way of accessing the data and creating 
the filtered file, but the option is available to extract from the raw data itself but it will take longer to
generate that filtered file.