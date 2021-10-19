
Bigplanet File Types
=====================


Overview
--------

[rewrite intro here]


Archive File (BPA)
-------------------

The Bigplanet Archive file (uses the .bpa extension) will have everything from
the parameter sweep.The BPA file does take longer to make than the filtered file, 
but it also builds an MD5 checksum file, which enables users to verfiy your 
data are not corrupted. After building the BPA file, its safe to remove the raw data. 
Every time the BPA file is accessed, the MD5 checksum routine is ran to ensure data integrity.


Filtered File (BPF)
-------------------

The Bigplanet Filtered file (uses the .bpf extension) is a subset of the data for a specific analysis.
To fully utilize this, the user should set up a :code:`bpl.in` file which is explained more in detail on :ref:`The Bigplanet Input File`.
Using a BPF file enables a much faster data accessing than from the raw data or the archive file. 


[Write statics that show how much faster the BPF file is vs reading in raw data vs reading from archive file]

